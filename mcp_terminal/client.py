import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

async def main():
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",  # The command to run your server
        args=["server.py"],  # Arguments to the command
    )


    # Connect to the server
    # async with stdio_client(server_params) as (read_stream, write_stream):
    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")


            # Call our calculator tool
            result = await session.call_tool("execute_command", arguments={'command': 'ls -l'})
            print(f"{result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())