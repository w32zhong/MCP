## Install
```sh
git submodule update --init --recursive --progress
conda create -n mcp python=3.10
pip install python-sdk/
pip install -r requirements.txt
```

## Example
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

## Reference
1. https://huggingface.co/learn/mcp-course/unit0/introduction
2. https://openrouter.ai/docs/features/tool-calling
3. https://qwen.readthedocs.io/en/latest/framework/function_call.html#hugging-face-transformers
4. https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle
