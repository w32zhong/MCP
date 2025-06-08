Set up MCP server:
```sh
pip install python-sdk/ --break-system-packages
pip install --break-system-packages -r requirements.txt
python test-mcp-server.py --transport streamable-http
```

Call MCP server:
```
./test-mcp.sh
```
