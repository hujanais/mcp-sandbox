import sys
# sys.path.append("/tools") # Replace with the actual path
# sys.path.append("/database")

from mcp.server.fastmcp import FastMCP

from database.db_utils import get_model

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

# Create the MCP server instance
mcp = FastMCP("mcp-demo", host="0.0.0.0", port=8050)
mcp.add_tool(execute_command)
mcp.add_tool(get_command_history)
mcp.add_tool(get_current_directory)
mcp.add_tool(delete_file_content)
mcp.add_tool(change_directory)
mcp.add_tool(list_directory)
mcp.add_tool(write_file)
mcp.add_tool(read_file)
mcp.add_tool(insert_file_content)
mcp.add_tool(update_file_content)

mcp.add_tool(get_model)

if __name__ == "__main__":
    transport = "sse"  #  stdio, sse
    print(f"MCP server is running on {transport} transport...")
    mcp.run(transport=transport)
