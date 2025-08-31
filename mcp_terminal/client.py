import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from mcp_client import MCPClient

async def main():
    mcpClient = MCPClient()
    await mcpClient.connect()

    try:
        while True:
            user_input = input("Enter your prompt (or type 'exit()' to quit): ")
            user_input = user_input.strip()
            if user_input == "exit()":
                print("Exiting...")
                break
            if 'exit' in user_input:
                print("Do you mean to exit? Please type 'exit()' to quit.")
                break
            resp = await mcpClient.process_query(user_input)
            print(resp)

    except KeyboardInterrupt:
        await mcpClient.cleanup()
        print("\nExiting...")
    
if __name__ == "__main__":
    asyncio.run(main())

