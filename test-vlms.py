import torch
from PIL import Image
import requests
from transformers import AutoModel, AutoModelForVision2Seq, AutoTokenizer, AutoProcessor, TextStreamer

image_url = "https://c.ndtvimg.com/2025-06/vopt78mk_donald-trump-and-elon-musk_625x300_06_June_25.jpeg"
prompt = "Describe this image."


def test_Qwen(model_id="Qwen/Qwen2.5-VL-32B-Instruct"):
    from transformers import Qwen2_5_VLForConditionalGeneration
    from qwen2_5_vision_process import process_vision_info

    processor = AutoProcessor.from_pretrained(model_id)

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_id, torch_dtype="auto", device_map="auto"
    )
    messages = [
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
    #test_Qwen() # 32B (requiring 5x16=80G VRAM)
    #test_Mistral() # 24B (requiring 4x16=64G VRAM)
    test_MiMo() # 7B (requiring 2x16=32G VRAM)
