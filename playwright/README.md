# Standalone MCP Server
npx @playwright/mcp@latest --port 8931

# Client Connection
{
  "mcpServers": {
    "playwright": {
      "url": "http://localhost:8931/mcp"
    }
  }
}