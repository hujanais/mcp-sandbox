import httpx
from fastmcp import FastMCP
import requests

from tools.models.model_tools import get_model

base_url = "http://localhost:8081/dms"

# client = httpx.AsyncClient(base_url=base_url)
# openapi_spec = httpx.get(f"{base_url}/openapi.json")

# mcp = FastMCP.from_openapi(openapi_spec=openapi_spec, client=client, name="DMS MCP Server")
mcp = FastMCP(name="DMS MCP Server", tools=[get_model])

if __name__ == "__main__":
    transport = "sse"  #  stdio, sse
    print(f"MCP server is running on {transport} transport...")
    mcp.run(transport=transport)
    