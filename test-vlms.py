import torch
from PIL import Image
import requests
from transformers import AutoModel, AutoModelForVision2Seq, AutoTokenizer, AutoProcessor, TextStreamer

image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTIeBeOxN9BKWv8WIU11j6nDZsv3-nhYpRFlQ"
prompt = "仅通过调用提供的计算工具验证图中的加法。这里你只须要调用工具。"

system_prompt = """# About You
You are a powerful and helpful agent with language, tool-calling, and vision capabilities.

# Tools
You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "add_two_numbers", "description": "Add two numbers", "parameters": {"type": "object", "required": ["a", "b"], "properties": {"a": {"type": "integer", "description": "The first number"}, "b": {"type": "integer", "description": "The second number"}}}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
"""


def test_Qwen(model_id="Qwen/Qwen2.5-VL-32B-Instruct"):
    from transformers import Qwen2_5_VLForConditionalGeneration
    from qwen2_5_vision_process import process_vision_info

    processor = AutoProcessor.from_pretrained(model_id)

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_id, torch_dtype="auto", device_map="auto"
    )
    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": system_prompt},
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image_url,
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    print(text)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda")

    streamer=TextStreamer(processor.tokenizer,
                          skip_prompt=True, skip_special_tokens=False)
    model.generate(**inputs, max_new_tokens=2048, streamer=streamer)


def test_Mistral(model_id="mistralai/Mistral-Small-3.1-24B-Instruct-2503"):
    processor = AutoProcessor.from_pretrained(model_id)
    streamer=TextStreamer(processor.tokenizer,
                          skip_prompt=True, skip_special_tokens=False)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        },
    ]
    text = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False
    )
    image = Image.open(requests.get(image_url, stream=True).raw)
    print(text)
    inputs = processor(
        text=text,
        images=image,
        return_tensors="pt"
    )

    model = AutoModelForVision2Seq.from_pretrained(
        model_id, torch_dtype="auto", device_map="auto"
    )
    inputs.to(device=model.device, dtype=model.dtype)
    model.generate(**inputs, max_new_tokens=2048, streamer=streamer)


def test_InternVL(model_id='OpenGVLab/InternVL3-38B'):
    from internvl3_img_process import load_image
    tokenizer = AutoTokenizer.from_pretrained(model_id,
                    trust_remote_code=True, use_fast=False)
    question = '<image>\nPlease describe the image shortly.'
    image = load_image(requests.get(image_url, stream=True).raw)
    image = image.to(torch.bfloat16).cuda()

    model = AutoModel.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    model.eval()

    generation_config = dict(max_new_tokens=2048, do_sample=False)
    response = model.chat(tokenizer, image, question, generation_config)


def test_MiMo(model_id="XiaomiMiMo/MiMo-VL-7B-SFT"):
    test_Qwen(model_id)


if __name__ == "__main__":
    #test_InternVL() # 38B
    test_Qwen() # 32B (requiring 5x16=80G VRAM)
    #test_Mistral() # 24B (requiring 4x16=64G VRAM)
    #test_MiMo() # 7B (requiring 2x16=32G VRAM)
