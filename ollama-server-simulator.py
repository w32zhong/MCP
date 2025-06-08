import flask
from flask import request
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name_or_path = "Qwen/Qwen3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path, torch_dtype="auto", device_map="auto",
)

app = flask.Flask(__name__)
CORS(app)


@app.route("/api/chat", methods=['POST'])
def route_api_chat():
    request_json = request.get_json()
    print(request_json)
    messages = request_json.get('messages', None)
    tools = request_json.get('tools', None)
    model_input = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
    print(model_input)
    return "<p>Hello, World!</p>"


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=11434,
        debug=True
    )
