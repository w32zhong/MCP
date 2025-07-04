import sys
sys.path.insert(0, 'python-sdk/src')
from mcp.server.fastmcp import FastMCP, Image
import cv2 as cv

mcp = FastMCP("Demo")


# tool calling may have side-effects
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
async def get_screen_snapshot():
    """Get the current screen frame as Image."""

    img = cv.imread('./test.png')
    return Image(data=img.tobytes(), format="png")


# resource has no side-effects
@mcp.resource('readme://getREADME')
def readme() -> str:
    """Read the contents of README file"""
    with open('README.md', 'r') as fh:
        return fh.read()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio",
                        choices=["stdio", "sse", "streamable-http"])
    parser.add_argument("--port", type=int, default=8989)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    mcp.settings.host = args.host
    mcp.settings.port = args.port
    print(mcp.settings)
    print(mcp._tool_manager.list_tools())

    mcp.run(transport=args.transport)
