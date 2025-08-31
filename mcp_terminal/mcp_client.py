from contextlib import AsyncExitStack
import os
import json
from typing import Any, Dict, List, Optional
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    """Client for interacting with OpenAI models using MCP tools."""

    def __init__(self):
        
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None

        api_key = os.environ.get("OPENAI_API_KEY")
        self.openai_client = AsyncOpenAI(api_key=api_key)
        self.model = "o4-mini"

        self.system_prompt: str = ""

    async def connect(self):
        """Connect to the MCP server and list available tools."""

        # Connect to the server
        stdio_transport = await self.exit_stack.enter_async_context(
            sse_client("http://localhost:8050/sse")
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # Initialize the connection
        await self.session.initialize()
        print("Connected to MCP server.")

        # show available tools
        available_tools = await self.get_mcp_tools()
        print("Available tools:")
        for tool in available_tools:
            print(tool['function']['name'])

        # Get database schema for system prompt
        db_schema = await self.session.call_tool("introspect_db", {})
        self.system_prompt = f"You are an AI assistant with access to the following database schema:\n{db_schema.content[0].text}\nUse this information to assist with user queries."

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server in OpenAI format.

        Returns:
            A list of tools in OpenAI format.
        """
        tools_result = await self.session.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_result.tools
        ]

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available MCP tools.

        Args:
            query: The user query.

        Returns:
            The response from OpenAI.
        """
        # Get available tools
        tools = await self.get_mcp_tools()

        # Initial OpenAI API call
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ],
            tools=tools,
            tool_choice="auto",
        )

        # Get assistant's response
        assistant_message = response.choices[0].message

        # Initialize conversation with user query and assistant response
        messages = [
            {"role": "user", "content": query},
            assistant_message,
        ]

        # Handle tool calls if present
        if assistant_message.tool_calls:
            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                # Execute tool call
                print(f"Calling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
                result = await self.session.call_tool(
                    tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments),
                )

                # Add tool response to conversation
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content[0].text,
                    }
                )

            # Get final response from OpenAI with tool results
            final_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="none",  # Don't allow more tool calls
            )

            return final_response.choices[0].message.content

        # No tool calls, just return the direct response
        return assistant_message.content

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()
