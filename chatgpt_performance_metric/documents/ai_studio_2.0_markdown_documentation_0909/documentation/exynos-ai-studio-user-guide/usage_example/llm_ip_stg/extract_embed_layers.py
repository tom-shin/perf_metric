import argparse
import inspect
import os
import pickle
import sys
from collections import OrderedDict
import torch
import torch.nn as nn

sys.path.append("./models/pytorch/src/")


class QuantizedLayer(nn.Module):
    def __init__(self):
        super(QuantizedLayer, self).__init__()
        self.inS, self.inQp, self.inQn, self.inZP = None, None, None, None
        self.outS, self.outQp, self.outQn, self.outZP = None, None, None, None

    def forward(self, x):
        if self.inS is not None:
            x = torch.clamp(x / self.inS + self.inZP, self.inQn, self.inQp).round()
            x = self.inS * (x - self.inZP)

        x = self.org_module(x)

        if self.outS is not None:
            x = torch.clamp(x / self.outS + self.outZP, self.outQn, self.outQp).round()
            x = self.outS * (x - self.outZP)

        return x


class EmbExtractor:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        os.makedirs(dir_path, exist_ok=True)

    def save_token_emb_layer(self, model):
        torch.save(
            model.model.embed_tokens, os.path.join(self.dir_path, "token_emb_layer.pt")
        )
        return

    def object_to_dict(self, obj):
        if isinstance(obj, dict):
            return {k: self.object_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, OrderedDict):
            return obj
        elif isinstance(obj, torch.Tensor):
            return obj
        elif hasattr(obj, "__dict__"):
            return {k: self.object_to_dict(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, list):
            return [self.object_to_dict(i) for i in obj]
        else:
            return obj

    def save_cls_value(self, rotary_emb_layer):
        extracted_obj = self.object_to_dict(rotary_emb_layer)
        extracted_obj["orig_module_name"] = rotary_emb_layer.__class__.__name__
        with open(
            os.path.join(self.dir_path, "rotary_emb_layer_values.pkl"), "wb"
        ) as f:
            pickle.dump(extracted_obj, f)

    def get_obj_code(self, obj):
        try:
            return inspect.getsource(obj)
        except:
            return inspect.getsource(obj.__class__)

    def gen_layer_cls_code(self, layer):
        class_code = self.get_obj_code(layer)
        return f"""import torch
{class_code}"""

    def save_cls_code(self, rotary_emb_layer):
        code_str = self.gen_layer_cls_code(rotary_emb_layer)
        with open(os.path.join(self.dir_path, "rotary_emb_layer_code.py"), "w") as f:
            f.write(code_str)

    def save_rotary_emb_layer(self, model):
        rotary_emb_layer = model.model.layers[0].self_attn.rotary_emb
        self.save_cls_value(rotary_emb_layer)
        self.save_cls_code(rotary_emb_layer)
        return

    def run(self, model_path, device="cuda"):
        model = torch.load(model_path, map_location=device)
        self.save_token_emb_layer(model)
        self.save_rotary_emb_layer(model)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_path", type=str, default="./embed_layers")
    parser.add_argument("--model_path", type=str, default="./models/pytorch/model.pt")
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()

    emb_extractor = EmbExtractor(dir_path=args.dir_path)
    emb_extractor.run(args.model_path, args.device)
