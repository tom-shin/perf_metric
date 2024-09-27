## LLM CNNX Word Generation Example

This example is designed for a custom model tailored to handle fixed-size inputs for LLM inference. Due to the requirement for static tensors, the PyTorch LLM is converted into two CNNX formats:
- **Input Prompting (IP)** CNNX model for the prefill phase.
    - During this phase, the LLM processes the input tokens to compute the key-value (KV) tensors and yields the first new token.
- **Single Token Generation (STG)** CNNX model for the decoding phase.
    - During this phase, the LLM generates tokens sequentially by using and continuously updating the KV cache.

Assuming that both CNNX models are provided by users, this example supports the following functions necessary for end-to-end text generation:
- (1) All the Transformer blocks and the LM-Head block are extracted and stored separately.
- (2) Two rounds of inference are conducted for each Transformer block.
    - The first inference produces KV tensors within the attention block.
    - Utilizing these tensors, the second inference generates the output states from each Transformer block or the logits from the LM-Head block.

### Example Scripts
The related files can be found in this directory or at the `/home/sample/llm_ip_stg` path in the released Docker image.

#### (1) Partitioning the Transformer blocks within each CNNX model

- The segmented CNNX files are created in the `${CNNX_DIR}_split` folder given the `${CNNX_DIR}` folder. Loading these models requires the same external data files as the original CNNX model. Note that the corresponding encodings are automatically segmented.
- (1-1) To split the IP CNNX model, use: `python3 split_blocks_ip.py`
- (1-2) To split the STG CNNX model, use: `python3 split_blocks_stg.py`

#### (2) Generating text in an end-to-end manner
- Prepare the token and rotary embedding layers extracted from the PyTorch model. To this end, the following code can be used: `python3 extract_embed_layers.py` 
- Generate text based on the segmented CNNX files and extracted embedding layers.
    - For inference using the CNNX model, use the following code. This produces the results of **simulated quantization** via [Simulator](https://ennamis.nota.ai/samsung_lsi/eht-docs/-/blob/master/simulator/simulator.md) based on the encodings files.

        ```bash
        python3 generate_text.py\
            --runtime_mode cnnx\
            --save_file results_cnnx.txt
        ```

    - For inference using only the ONNX model, use the following code. This uses an empty encoding file for Simulator and yields the same results with onnxruntime.       
     
        ```bash
        python3 generate_text.py\
            --runtime_mode onnx\
            --save_file results_onnx.txt
        ```        