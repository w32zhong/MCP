import flask
from flask import request
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
import re

model_name_or_path = "Qwen/Qwen3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path, torch_dtype="auto", device_map="auto",
)

app = flask.Flask(__name__)
CORS(app)


def try_parse_tool_calls(content: str):
    """Try parse the tool calls."""
    tool_calls = []
    offset = 0
    for i, m in enumerate(re.finditer(r"<tool_call>\n(.+)?\n</tool_call>", content)):
        if i == 0:
            offset = m.start()
        try:
            func = json.loads(m.group(1))
            tool_calls.append({"type": "function", "function": func})
            if isinstance(func["arguments"], str):
                func["arguments"] = json.loads(func["arguments"])
        except json.JSONDecodeError as e:
            print(f"Failed to parse tool calls: the content is {m.group(1)} and {e}")
            pass
    if tool_calls:
        if offset > 0 and content[:offset].strip():
            c = content[:offset]
        else:
            c = ""
        return {"role": "assistant", "content": c, "tool_calls": tool_calls}
    return {"role": "assistant", "content": re.sub(r"<\|im_end\|>$", "", content)}


@app.route("/api/chat", methods=['POST'])
def route_api_chat():
    request_json = request.get_json()
    messages = request_json.get('messages', None)
    tools = request_json.get('tools', None)
    print(request_json)

    input_txt = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
    print(input_txt)

    inputs = tokenizer(input_txt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=512)
    output_txt = tokenizer.batch_decode(outputs)[0][len(input_txt):]
    print(output_txt)

    return try_parse_tool_calls(output_txt)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=11434, # ollama default port
        debug=False, # True
    )
