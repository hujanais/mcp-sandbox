import os
import sys
from mcp.server.fastmcp import FastMCP

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_terminal.tools.python_tool import PythonTools

# Create the MCP server instance
mcp = FastMCP("mcp-demo", host="0.0.0.0", port=8051)
# tool = PythonTools()

# mcp.add_tool(tool.run_python_code)

# @mcp.tool
# def python_tool(code: str, data) -> str:
#     """
#     Executes the provided Python code in a restricted environment.

#     If successful, returns the output of the code.
#     If failed, returns an error message which will include ERROR: at the start.

#     :param code: The code to run.
#     :param data: The pandas DataFrame to be used for the visualization.
#     :return: the result from the python code if successful, otherwise returns an error message.
#     """
#     result = tool.run_python_code(code, data)
#     return result

if __name__ == "__main__":
    transport = "sse"  #  stdio, sse
    print(f"Python MCP server is running on {transport} transport...")
    mcp.run(transport=transport)