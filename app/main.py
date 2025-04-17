# app/main.py
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

mcp = FastMCP("SSE Demo Server")

@mcp.resource("hello://{name}")
def hello_resource(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

# Create SSE transport
transport = SseServerTransport("/messages/")

async def handle_sse(request):
    async with transport.connect_sse(
            request.scope, request.receive, request._send
    ) as streams:
        await mcp._mcp_server.run(
            streams, streams, mcp._mcp_server.create_initialization_options()
        )

# Define routes for SSE and message handling
routes = [
    Route("/sse/", endpoint=handle_sse),
    Mount("/messages/", app=transport.handle_post_message),
]

# Create Starlette app for SSE
sse_app = Starlette(routes=routes)

# Create FastAPI app and mount SSE app
app = FastAPI()
app.mount("/", sse_app)

@app.get("/")
async def root():
    return {"message": "SSE MCP Server is running"}
