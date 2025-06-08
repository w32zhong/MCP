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

Call MCP server:
```sh
./test-mcp.sh
```

## Reference
[1] https://huggingface.co/learn/mcp-course/unit0/introduction
