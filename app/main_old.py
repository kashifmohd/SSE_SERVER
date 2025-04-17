"""SSE-based MCP server example.
Exposes a resource and a tool.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SSE Demo Server")

app = mcp.sse_app()


@mcp.resource("hello://{name}")
def hello_resource(name: str) -> str:
    """Returns a personalized greeting."""
    return f"Hello, {name}!"


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
