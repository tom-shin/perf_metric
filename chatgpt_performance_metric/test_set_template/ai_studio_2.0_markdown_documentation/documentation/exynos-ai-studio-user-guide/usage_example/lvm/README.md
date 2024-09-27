## LVM CNNX Image Generation Pipeline Example

Clone [this repository](https://github.com/Amblyopius/Stable-Diffusion-ONNX-FP16/tree/main) and set the environment following Readme

Modify the pix2pixUI.py as follows.
The pipeline can be easily modified using our simulator API.

![[pix2pix]](images/pix2pix.png)

The modified code is as follows:

```python
    import numpy as np
    import gradio as gr
    
    from pipeline_onnx_stable_diffusion_instruct_pix2pix import OnnxStableDiffusionInstructPix2PixPipeline
    from diffusers import DDIMScheduler,  EulerAncestralDiscreteScheduler, LMSDiscreteScheduler
    from simulator.api import Simulator
    from simulator.schema.base import InferenceSessionParameters
    
    def pix2pix(input_img, prompt, guide, iguide, steps, seed):
        if seed == -1:
            generator=None
        else:
            generator=np.random
            generator.seed(seed)
        img = pipe(
            prompt=prompt,
            image=input_img,
            num_inference_steps=steps,
            guidance_scale=guide,
            image_guidance_scale=iguide,
            generator=generator).images[0]
        return img
    
    if __name__ == "__main__":
        model="./model/ip2p-base-fp16-vae_ft_mse-autoslicing"
        pipe = OnnxStableDiffusionInstructPix2PixPipeline.from_pretrained(model, provider="DmlExecutionProvider", safety_checker=None)
        pipe.scheduler=EulerAncestralDiscreteScheduler.from_pretrained(model, subfolder="scheduler")
    
        onnx_model_path = ".onnx file path of CNNX model"
        encodings_path = ".encodings file path of CNNX model"
        get_inference_session_params = InferenceSessionParameters(
            input_model_path=onnx_model_path,
            input_encodings_path=encodings_path,
            use_cuda=True,
        )
        pipe.unet.model = Simulator.get_inference_session(get_inference_session_params)
    
        demo=gr.Interface(pix2pix, gr.Image(shape=(512,512)), "image")
        title="ONNX Instruct Pix 2 Pix"
        css = "#imgbox img {max-width: 100%  !important; }\n#imgbox div {height: auto;}"
        with gr.Blocks(title=title, css=css) as demo:
            with gr.Row():
                with gr.Column(scale=1):
                    seed = gr.Number(value=-1, label="seed", precision=0)
                with gr.Column(scale=14):
                    prompt = gr.Textbox(value="", lines=2, label="prompt")
            with gr.Row():
                with gr.Column(scale=1):
                    guide = gr.Slider(1.1, 10, value=3, step=0.1, label="Text guidance")
                with gr.Column(scale=1):
                    iguide = gr.Slider(1, 10, value=1.1, step=0.1, label="Image guidance")
                with gr.Column(scale=1):
                    steps = gr.Slider(10,100, value=30, step=1, label="Steps")
            with gr.Row():
                with gr.Column(scale=1):
                    input_img = gr.Image(label="Input Image", type="pil", elem_id="imgbox").style(width=600,height=600)
                with gr.Column(scale=1):
                    image_out = gr.Image(value=None, label="Output Image", elem_id="imgbox").style(width=600,height=600)
            gen_btn = gr.Button("Generate", variant="primary", elem_id="gen_button")
    
            inputs=[input_img, prompt, guide, iguide, steps, seed]
            gen_btn.click(fn=pix2pix, inputs=inputs, outputs=[image_out])
    
        demo.launch()
```
