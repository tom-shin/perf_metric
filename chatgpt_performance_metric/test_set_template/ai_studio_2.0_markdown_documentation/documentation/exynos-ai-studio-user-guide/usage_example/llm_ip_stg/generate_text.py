import numpy as np
import torch
import argparse
import pickle
import importlib
import os
import sys
import tqdm
from simulator.api import Simulator, InferenceSessionParameters
from transformers import AutoTokenizer
import time


class EmbLoader:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def load_token_emb_layer(self, file_name="token_emb_layer.pt"):
        return torch.load(os.path.join(self.dir_path, file_name))

    def get_saved_rotary_layer(self, layer_cls, extracted_obj):
        new_obj = layer_cls(dim=extracted_obj["dim"])
        for k, v in extracted_obj.items():
            if k in new_obj.__dict__:
                setattr(new_obj, k, v)
        return new_obj

    def load_module(self, module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def get_new_layer_instance(self, module, module_name):
        return getattr(module, module_name)

    def load_rotary_emb_layer(
        self,
        v_file_name="rotary_emb_layer_values.pkl",
        c_file_name="rotary_emb_layer_code.py",
    ):
        with open(os.path.join(self.dir_path, v_file_name), "rb") as f:
            loaded_data = pickle.load(f)

        module_name = loaded_data["orig_module_name"]
        file_path = os.path.join(self.dir_path, c_file_name)
        module = self.load_module(module_name, file_path)
        new_layer = self.get_new_layer_instance(module, module_name)
        return self.get_saved_rotary_layer(new_layer, loaded_data)


class StopConditionChecker:
    def __init__(self, eos_token_id, max_seq_len):
        self.eos_token_id = eos_token_id
        self.max_seq_len = max_seq_len

    def reset_seq_len(self, max_seq_len):
        self.max_seq_len = max_seq_len

    def check(self, cur_token, position_id):
        if cur_token.item() == self.eos_token_id:
            print("Stop gen: EOS token is detected.")
            return False
        if position_id >= self.max_seq_len:
            print("Stop gen: Seq length reaches the maximum.")
            return False
        return True


def get_quantsims(
    onnx_folder,
    encodings_folder,
    num_files,
    mode="cnnx",
    empty_encodings_path="./models/cnnx/empty.encodings",
    device="cpu",
):
    quantsims = []
    for idx in range(num_files):
        onnx_file = os.path.join(onnx_folder, f"layer_{int(idx):02}.onnx")
        print(f"load {onnx_file}")

        if mode == "cnnx":
            encodings_file = os.path.join(
                encodings_folder, f"layer_{int(idx):02}.encodings"
            )
        elif mode == "onnx":
            encodings_file = empty_encodings_path
        print(f"load {encodings_file}")

        use_cuda = device != "cpu"
        params = InferenceSessionParameters(
            input_model_path=onnx_file,
            input_encodings_path=encodings_file,
            use_cuda=use_cuda,  # set this true to use GPU
        )
        quantsim = Simulator.get_quantization_sim(params)
        quantsims.append(quantsim)
    return quantsims


def run_session(session, inputs, output_names):
    outputs = session.run(output_names, inputs)
    outputs_dict = {}
    for k, v in zip(output_names, outputs):
        outputs_dict[k] = v
    return outputs_dict


def print_session_info(session):
    for block_idx, x in enumerate(session.get_inputs()):
        print(f"input {block_idx} - {x.name}: {x.type} {x.shape}")
    for block_idx, x in enumerate(session.get_outputs()):
        print(f"output {block_idx} - {x.name}: {x.type} {x.shape}")


def to_numpy(tensor, data_type):
    return (
        tensor.detach().cpu().numpy().astype(data_type)
        if tensor.requires_grad
        else tensor.cpu().numpy().astype(data_type)
    )


def get_datatype(session):
    data_type_str = session.get_inputs()[0].type
    if data_type_str == "tensor(float16)":
        data_type = np.float16
    elif data_type_str == "tensor(float32)" or data_type_str == "tensor(float)":
        data_type = np.float32
    else:
        raise Exception(f"Unknown data type {data_type_str}")
    print(f"data_type: {data_type_str}")
    return data_type


def get_input_shapes(session):
    for inputs_meta in session._inputs_meta:
        if inputs_meta.name == "past_key_values.0.key":
            k_cache_shape = inputs_meta.shape
            break
    batch = k_cache_shape[0]
    n_heads = k_cache_shape[1]
    max_seq_len = k_cache_shape[2]
    head_dim = k_cache_shape[3]
    return batch, n_heads, max_seq_len, head_dim


def prepare_inputs_block(inputs_block, record, block_idx):
    inputs_block["attention_mask"] = record["attention_mask"]
    inputs_block["cos"] = record["cos"]
    inputs_block["sin"] = record["sin"]
    inputs_block["lora_scale"] = record["lora_scale"]
    inputs_block[f"past_key_values.{block_idx}.key"] = record[
        f"past_key_values.{block_idx}.key"
    ]
    inputs_block[f"past_key_values.{block_idx}.value"] = record[
        f"past_key_values.{block_idx}.value"
    ]
    for proj_type in ["q_proj", "k_proj", "v_proj", "o_proj"]:
        for lora_type in ["lora_A", "lora_B"]:
            target = f"base_model.model.model.layers.{block_idx}.self_attn.{proj_type}.{lora_type}.weight"
            inputs_block[target] = record[target]
    return inputs_block


def get_next_token(logits, index):
    logit, next_token = torch.max(torch.tensor(logits[:, index, :]), dim=-1)
    next_token = next_token.to(torch.int64).unsqueeze(0)
    return next_token, logit


def generate_text(
    prompt,
    device,
    ip_quantsims,
    stg_quantsims,
    data_type,
    max_seq_len_ip,
    max_seq_len_stg,
    batch,
    n_heads,
    head_dim,
    token_emb_layer,
    rotary_emb_layer,
    tokenizer,
):
    # Prepare inputs and outputs
    inputs_pt = tokenizer(
        prompt, return_tensors="pt", max_length=max_seq_len_ip, padding="max_length"
    ).to(device)
    inputs_embeds = token_emb_layer(inputs_pt["input_ids"])
    attention_mask = inputs_pt["attention_mask"]

    position_id = int(attention_mask.sum())
    position_ids = torch.ones((1, max_seq_len_ip), dtype=torch.long, device=device)
    position_ids[0, :position_id] = torch.arange(0, position_id, device=device)
    cos, sin = rotary_emb_layer(inputs_embeds, seq_len=max_seq_len_ip)
    cos = cos.reshape(shape=(cos.shape[2], cos.shape[3]))
    sin = sin.reshape(shape=(sin.shape[2], sin.shape[3]))
    cos = cos[position_ids].unsqueeze(1)
    sin = sin[position_ids].unsqueeze(1)

    stop_cond_checker = StopConditionChecker(tokenizer.eos_token_id, max_seq_len_ip)

    # Initialize numpy-format inputs
    record = {}
    record["attention_mask"] = to_numpy(attention_mask, data_type)
    record["cos"] = np.squeeze(to_numpy(cos, data_type), axis=1)
    record["sin"] = np.squeeze(to_numpy(sin, data_type), axis=1)
    record["lora_scale"] = np.array([args.lora_scale]).astype(data_type)

    for block_idx in range(n_layers):
        # Initialize past_key_values matrices
        record[f"past_key_values.{block_idx}.key"] = np.zeros(
            [batch, n_heads, max_seq_len_ip, head_dim]
        ).astype(data_type)
        record[f"past_key_values.{block_idx}.value"] = np.zeros(
            [batch, n_heads, max_seq_len_ip, head_dim]
        ).astype(data_type)

        # Prepare lora weights
        for proj_type in ["q_proj", "k_proj", "v_proj", "o_proj"]:
            for lora_type in ["lora_A", "lora_B"]:
                target = f"base_model.model.model.layers.{block_idx}.self_attn.{proj_type}.{lora_type}.weight"
                record[target] = to_numpy(lora_weights[target], data_type)

    # Initialize outputs
    output_tokens = inputs_pt["input_ids"][:, :position_id]

    # [IP] Repeat two inference processes per block
    for block_idx, ip_quantsim in enumerate(
        tqdm.tqdm(ip_quantsims, desc="block-level forward")
    ):
        session = ip_quantsim.session
        output_names = [output.name for output in session.get_outputs()]

        inputs_block = {}
        if block_idx == 0:
            inputs_block["inputs_embeds"] = to_numpy(inputs_embeds, data_type)
        else:
            prev_output_node = f"/model/layers.{block_idx-1}/Add_1_output_0"
            inputs_block[prev_output_node] = outputs_dict[prev_output_node + "_updated"]

        if block_idx < len(ip_quantsims) - 1:  # except the last lm-head
            inputs_block = prepare_inputs_block(inputs_block, record, block_idx)

            # [IP] Pre ONNX inference (to get keys and values)
            outputs_dict = run_session(session, inputs_block, output_names)

            for head_idx in range(n_heads):
                for attr in ["key", "value"]:
                    # Squeeze the single keys & values: (1, 1, 1, max_seq_len, head_dim) to (1, 1, max_seq_len, head_dim)
                    squeezed = np.squeeze(
                        outputs_dict[f"single.{block_idx}.{head_idx}.{attr}"], axis=2
                    )
                    # Store past_key_values
                    inputs_block[f"past_key_values.{block_idx}.{attr}"][
                        :, head_idx, :, :
                    ] = squeezed
                    record[f"past_key_values.{block_idx}.{attr}"] = inputs_block[
                        f"past_key_values.{block_idx}.{attr}"
                    ]

        # [IP] Main ONNX inference (to get block output)
        outputs_dict = run_session(session, inputs_block, output_names)

        if block_idx == len(ip_quantsims) - 1:  # for the last lm-head
            next_token, logit = get_next_token(
                outputs_dict["logits_updated"], index=position_id - 1
            )
            output_tokens = torch.cat((output_tokens, next_token), dim=1)
            output_str = tokenizer.batch_decode(output_tokens, skip_special_tokens=True)

            print(
                f"\n* [IP] Output - pos {position_id} token {next_token.item()} logit {logit.item():.4f}"
            )
            print(output_str[0])

    # Prepare inputs for STG
    cos, sin = rotary_emb_layer(inputs_embeds, seq_len=max_seq_len_stg)
    stop_cond_checker.reset_seq_len(max_seq_len_stg)

    # Add zeros to increase seq_len of IP->STG
    pad_length = max_seq_len_stg - max_seq_len_ip
    record["attention_mask"] = np.pad(
        record["attention_mask"],
        ((0, 0), (0, pad_length)),
        "constant",
        constant_values=0,
    )
    for block_idx in range(n_layers):
        record[f"past_key_values.{block_idx}.key"] = np.pad(
            record[f"past_key_values.{block_idx}.key"],
            pad_width=((0, 0), (0, 0), (0, pad_length), (0, 0)),
            mode="constant",
            constant_values=0,
        )
        record[f"past_key_values.{block_idx}.value"] = np.pad(
            record[f"past_key_values.{block_idx}.value"],
            pad_width=((0, 0), (0, 0), (0, pad_length), (0, 0)),
            mode="constant",
            constant_values=0,
        )

    # [STG] Repeat two inference processes per block
    while stop_cond_checker.check(next_token, position_id):
        record["attention_mask"][:, position_id] = 1
        position_id = int(
            np.sum(record["attention_mask"])
        )  # position_id increases here
        record["cos"] = to_numpy(cos[:, :, position_id - 1, :], data_type)
        record["sin"] = to_numpy(sin[:, :, position_id - 1, :], data_type)

        for block_idx, stg_quantsim in enumerate(
            tqdm.tqdm(stg_quantsims, desc="block-level forward")
        ):
            session = stg_quantsim.session
            output_names = [output.name for output in session.get_outputs()]

            inputs_block = {}
            if block_idx == 0:
                cur_token = output_tokens[:, -1].to(device)
                inputs_embeds = token_emb_layer(cur_token).unsqueeze(1)
                inputs_block["inputs_embeds"] = to_numpy(inputs_embeds, data_type)
            else:
                prev_output_node = f"/model/layers.{block_idx-1}/Add_1_output_0"
                inputs_block[prev_output_node] = outputs_dict[
                    prev_output_node + "_updated"
                ]

            if block_idx < len(stg_quantsims) - 1:  # except the last lm-head
                inputs_block = prepare_inputs_block(inputs_block, record, block_idx)

                # [STG] Pre ONNX inference (to get keys and values)
                outputs_dict = run_session(session, inputs_block, output_names)

                for head_idx in range(n_heads):
                    for attr in ["key", "value"]:
                        # Squeeze the single keys & values: (1, 1, 1, 1, head_dim) to (1, 1, 1, head_dim)
                        squeezed = np.squeeze(
                            outputs_dict[f"single.{block_idx}.{head_idx}.{attr}"],
                            axis=2,
                        )
                        # Store past_key_values
                        inputs_block[f"past_key_values.{block_idx}.{attr}"][
                            :, head_idx, position_id - 1, :
                        ] = squeezed
                        record[f"past_key_values.{block_idx}.{attr}"] = inputs_block[
                            f"past_key_values.{block_idx}.{attr}"
                        ]

            # [STG] Main ONNX inference (to get block output)
            outputs_dict = run_session(session, inputs_block, output_names)

            if block_idx == len(stg_quantsims) - 1:  # for the last lm-head
                next_token, logit = get_next_token(
                    outputs_dict["logits_updated"], index=0
                )
                output_tokens = torch.cat((output_tokens, next_token), dim=1)
                output_str = tokenizer.batch_decode(
                    output_tokens, skip_special_tokens=True
                )

                print(
                    f"\n* [STG] Output - pos {position_id} token {next_token.item()} logit {logit.item():.4f}"
                )
                print(output_str[0])

    return output_str[0]


def file_write(file, text):
    file.write(text + "\n")
    print(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="summer is hot, and winter is",
    )
    parser.add_argument("--embed_folder", type=str, default="./embed_layers")
    parser.add_argument("--ip_folder", type=str, default="./models/cnnx/IP_split")
    parser.add_argument(
        "--ip_encodings_folder", type=str, default="./models/cnnx/IP_split/encodings"
    )
    parser.add_argument("--stg_folder", type=str, default="./models/cnnx/STG_split")
    parser.add_argument(
        "--stg_encodings_folder", type=str, default="./models/cnnx/STG_split/encodings"
    )
    parser.add_argument(
        "--lora_weights",
        type=str,
        default="./models/pytorch/lora.pt",
    )
    parser.add_argument("--lora_scale", type=float, default=4.0)
    parser.add_argument(
        "--tokenizer_path", type=str, default="./models/pytorch/tokenizer"
    )
    parser.add_argument("--n_layers", type=int, default=28)
    parser.add_argument("--runtime_mode", type=str, default="cnnx")
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--save_file", type=str, default="results.txt")
    args = parser.parse_args()

    # 1. Create the CNNX session
    device = args.device
    ip_quantsims = get_quantsims(
        args.ip_folder,
        args.ip_encodings_folder,
        args.n_layers + 1,
        mode=args.runtime_mode,
        device=device,
    )
    stg_quantsims = get_quantsims(
        args.stg_folder,
        args.stg_encodings_folder,
        args.n_layers + 1,
        mode=args.runtime_mode,
        device=device,
    )

    # 2. Prepare inputs
    # 2-1. Get the data type used by the model
    data_type = get_datatype(ip_quantsims[0].session)

    # 2-2. Get the input shapes
    batch, n_heads, max_seq_len_ip, head_dim = get_input_shapes(ip_quantsims[0].session)
    _, _, max_seq_len_stg, _ = get_input_shapes(stg_quantsims[0].session)
    n_layers = args.n_layers

    # 2-3. Prepare inputs from pytorch
    emb_loader = EmbLoader(args.embed_folder)
    token_emb_layer = emb_loader.load_token_emb_layer().to(device)
    rotary_emb_layer = emb_loader.load_rotary_emb_layer().to(device)
    lora_weights = torch.load(args.lora_weights)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_path)

    # 3. Generate text with CNNX pipeline
    if args.prompt is None:  # example prompts
        prompts = [
            "summer is hot, and winter is",
            "[{<(Task)>}]\nRemove all grammatical errors from this text\n\n[{<(Input)>}]\nLomg time no swe!\n\n[{<(Correction)>}]\n",
            "[{<(Task)>}]\nRemove all grammatical errors from this text\n\n[{<(Input)>}]\nHows it going?\n\n[{<(Correction)>}]\n",
            "[{<(Task)>}]\nRemove all grammatical errors from this text\n\n[{<(Input)>}]\nWhat's for diner?\n\n[{<(Correction)>}]\n",
        ]
    else:
        prompts = [args.prompt]

    with open(args.save_file, "w", encoding="utf-8") as file:
        t0 = time.time()
        for prompt in prompts:
            output = generate_text(
                prompt,
                device,
                ip_quantsims,
                stg_quantsims,
                data_type,
                max_seq_len_ip,
                max_seq_len_stg,
                batch,
                n_heads,
                head_dim,
                token_emb_layer,
                rotary_emb_layer,
                tokenizer,
            )
            file_write(file, "\n=== input ===")
            file_write(file, prompt)
            file_write(file, "=== output ===")
            file_write(file, output)
        file_write(
            file,
            f"\n** time elapsed (# prompts={len(prompts)}): {time.time()-t0:.1f} sec",
        )
    print(f"** results: {args.save_file}")
