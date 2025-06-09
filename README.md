![MCP](https://github.com/user-attachments/assets/8c768f33-ac74-4ddf-b557-09f7090e3fbf)

## Install
```sh
git submodule update --init --recursive --progress
conda create -n mcp python=3.10
pip install python-sdk/
pip install -r requirements.txt
```

## Run an Example
Set up MCP server:
```sh
python test-mcp-server.py --transport streamable-http
```

Test calling MCP server:
```sh
./test-mcp.sh
```

Simulate Ollama server:
```sh
CUDA_VISIBLE_DEVICES=0,1,2 python ollama-server-simulator.py
```

Test a prompt that needs tool calling:
```sh
python ollama-tool-call.py
```

What actually happened is, we (as an agent service) request MCP server to obtain tool capabilities, and send user prompt with avaiable tools:
```
[request_json] {
    "model": "qwen3:8b",
    "stream": false,
    "messages": [
        {
            "role": "user",
            "content": "What is three plus one?"
        }
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "add_two_numbers",
                "description": "Add two numbers",
                "parameters": {
                    "type": "object",
                    "required": [
                        "a",
                        "b"
                    ],
                    "properties": {
                        "a": {
                            "type": "integer",
                            "description": "The first number"
                        },
                        "b": {
                            "type": "integer",
                            "description": "The second number"
                        }
                    }
                }
            }
        }
    ]
}
```

Ollama needs to apply chat template and turn that request to LLM input text:
```
[input_txt] <|im_start|>system
# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "add_two_numbers", "description": "Add two numbers", "parameters": {"type": "object", "required": ["a", "b"], "properties": {"a": {"type": "integer", "description": "The first number"}, "b": {"type": "integer", "description": "The second number"}}}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call><|im_end|>
<|im_start|>user
What is three plus one?<|im_end|>
<|im_start|>assistant
```

The model response containining a tool calling:
```
[output_txt] <think>
Okay, the user is asking "What is three plus one?" Let me see. I need to figure out how to respond. The tools provided include a function called add_two_numbers, which takes two integers as parameters. The question is a simple arithmetic problem, so the function should work here. The numbers are three and one. I should call the function with a=3 and b=1. Then, return the result. Let me make sure the parameters are correct. Both are integers, and the function is designed to add them. Yep, that's right. So the answer should be 4.
</think>

<tool_call>
{"name": "add_two_numbers", "arguments": {"a": 3, "b": 1}}
</tool_call><|im_end|>
```

Ollama then parses the model response into a conversation item with tool call(s), and sends it back to us:
```
[output_parsed] {
    "role": "assistant",
    "content": "<think>\nOkay, the user is asking \"What is three plus one?\" Let me see. I need to figure out how to respond. The tools provided include a function called add_two_numbers, which takes two integers as parameters. The question is a simple arithmetic problem, so the function should work here. The numbers are three and one. I should call the function with a=3 and b=1. Then, return the result. Let me make sure the parameters are correct. Both are integers, and the function is designed to add them. Yep, that's right. So the answer should be 4.\n</think>\n\n",
    "tool_calls": [
        {
            "type": "function",
            "function": {
                "name": "add_two_numbers",
                "arguments": {
                    "a": 3,
                    "b": 1
                }
            }
        }
    ]
}
```

We will invoke MCP tool and make **another** request with tool calling result:
```
[request_json] {
    "model": "qwen3:8b",
    "stream": false,
    "messages": [
        {
            "role": "user",
            "content": "What is three plus one?"
        },
        {
            "role": "assistant",
            "content": "<think>\nOkay, the user is asking \"What is three plus one?\" Let me see. I need to figure out how to respond. The tools provided include a function called add_two_numbers, which takes two integers as parameters. The question is a simple arithmetic problem, so the function should work here. The numbers are three and one. I should call the function with a=3 and b=1. Then, return the result. Let me make sure the parameters are correct. Both are integers, and the function is designed to add them. Yep, that's right. So the answer should be 4.\n</think>\n\n",
            "tool_calls": [
                {
                    "function": {
                        "name": "add_two_numbers",
                        "arguments": {
                            "a": 3,
                            "b": 1
                        }
                    }
                }
            ]
        },
        {
            "role": "tool",
            "content": "4"
        }
    ],
    "tools": []
}
```

Similarly, when Ollama receives it, it applies chat template and converts it into string:
```
[input_txt] <|im_start|>user
What is three plus one?<|im_end|>
<|im_start|>assistant
<think>
Okay, the user is asking "What is three plus one?" Let me see. I need to figure out how to respond. The tools provided include a function called add_two_numbers, which takes two integers as parameters. The question is a simple arithmetic problem, so the function should work here. The numbers are three and one. I should call the function with a=3 and b=1. Then, return the result. Let me make sure the parameters are correct. Both are integers, and the function is designed to add them. Yep, that's right. So the answer should be 4.
</think>

<tool_call>
{"name": "add_two_numbers", "arguments": {"a": 3, "b": 1}}
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
4
</tool_response><|im_end|>
<|im_start|>assistant
```

The model outputs the final answer based on the previous tool calling result:
```
[output_txt] <think>
Okay, the user asked "What is three plus one?" and I used the add_two_numbers function with a=3 and b=1. The response from the tool was 4. So the answer is 4. I should present that clearly. Let me check if there's anything else needed. The user probably just wants the sum, so stating the result directly makes sense. No complications here. Just confirm the calculation is correct. 3 + 1 equals 4. Yep, that's right. Alright, time to respond.
</think>

The result of three plus one is **4**.<|im_end|>
```

Ollama parses the model output into a new conversation and sends it back:
```
[output_parsed] {
    "role": "assistant",
    "content": "<think>\nOkay, the user asked \"What is three plus one?\" and I used the add_two_numbers function with a=3 and b=1. The response from the tool was 4. So the answer is 4. I should present that clearly. Let me check if there's anything else needed. The user probably just wants the sum, so stating the result directly makes sense. No complications here. Just confirm the calculation is correct. 3 + 1 equals 4. Yep, that's right. Alright, time to respond.\n</think>\n\nThe result of three plus one is **4**."
}
```

## Reference
1. https://huggingface.co/learn/mcp-course/unit0/introduction
2. https://openrouter.ai/docs/features/tool-calling
3. https://qwen.readthedocs.io/en/latest/framework/function_call.html#hugging-face-transformers
4. https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle
