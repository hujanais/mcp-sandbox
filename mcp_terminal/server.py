from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import json
import sys
from typing import AsyncIterator, Optional

import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# sys.path.append("/mcp_terminal/database")  # Replace with the actual path
# sys.path.append("/tools") # Replace with the actual path
# sys.path.append("/database")

from mcp.server.fastmcp import Context, FastMCP
from database.db_utils import DBUtils
from tools.terminal_tool import (
    change_directory,
    delete_file_content,
    execute_command,
    get_command_history,
    get_current_directory,
    insert_file_content,
    list_directory,
    read_file,
    write_file,
    update_file_content,
)

# Define a type-safe context class
@dataclass
class AppContext:
    db: DBUtils  # Replace with your actual resource type

# Create the lifespan context manager
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    # Initialize resources on startup
    db_utils = DBUtils(reset_db=False)  # Set reset_db=True to drop and recreate tables
    try:
        # Make resources available during operation
        yield AppContext(db=db_utils)
    finally:
        # Clean up resources on shutdown
        # await db_utils.disconnect()
        print("Cleaning up resources...")

# Create the MCP server instance
mcp = FastMCP("mcp-demo", host="0.0.0.0", port=8050, lifespan=app_lifespan)
# mcp.add_tool(execute_command)
# mcp.add_tool(get_command_history)
# mcp.add_tool(get_current_directory)
# mcp.add_tool(delete_file_content)
# mcp.add_tool(change_directory)
# mcp.add_tool(list_directory)
# mcp.add_tool(write_file)
# mcp.add_tool(read_file)
# mcp.add_tool(insert_file_content)
# mcp.add_tool(update_file_content)

# @mcp.tool()
# def introspect_db(ctx: Context):
#     """
#     Retrieve the database schema and useful information about the database.
#     """
#     db = ctx.request_context.lifespan_context.db
#     return db.introspect_schema()

@mcp.tool()
def execute_fetch_sql_tool(ctx: Context, command: str, timeout: int = 30) -> str:
    """
    Execute the SQL script for requesting informatiion from the database like SELECT.
    """
    db = ctx.request_context.lifespan_context.db
    print(f"Executing SQL command: {command} with timeout {timeout}")
    rows = db.execute_fetch_sql_script(command)
    return str(rows)

@mcp.tool()
def execute_mutate_sql_tool(ctx: Context, command: str, timeout: int = 30) -> str:
    """
    Execute the SQL script for mutating the database like INSERT, UPDATE, DELETE.
    """
    db = ctx.request_context.lifespan_context.db
    print(f"Executing SQL command: {command} with timeout {timeout}")
    resp = db.execute_mutate_sql_script(command)
    return resp

if __name__ == "__main__":
    transport = "sse"  #  stdio, sse
    print(f"MCP server is running on {transport} transport...")
    mcp.run(transport=transport)
