from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

import sys
import os
from typing import Optional

from database.models import TaskStatus


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server.fastmcp import Context, FastMCP
from database.db_utils import DBUtils
from database.pydantic_models import PyModel, PyTask
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
def get_model(ctx: Context, model_id: Optional[str] = None) -> list[PyModel]:
    """
    Retrieve model(s) from the database.
    
    Args:
        model_id (Optional[str]): The specific model ID to retrieve. If None, returns all models.
        
    Returns:
        list[Model]: List of Model objects. If model_id is provided, returns a list with one model.
        
    Example:
        >>> all_models = get_model()  # Get all models
        >>> specific_model = get_model("123e4567-e89b-12d3-a456-426614174000")  # Get specific model
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    return db.get_model(model_id)

@mcp.tool()
def create_model(ctx: Context, model_name: str) -> PyModel:
    """
    Create a new model in the database.
    
    Args:
        model_name (str): The name of the model to be created.
        
    Returns:
        PyResponse[Model]: A response object containing the created Model object.
        >>> print({"status": response.status, "message": response.message, "data": response.data})
    Example:
        >>> model = create_model("bert-base-uncased")
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    response = db.create_model(model_name)
    return response

@mcp.tool()
def delete_model(ctx: Context, model_id: str) -> str:
    """
    Delete a model from the database.
    
    Args:
        model_id (int): The ID of the model to delete.
        
    Returns:
        PyResponse: A response object indicating success or failure of the deletion.
        
    Note:
        This operation will cascade delete all associated tasks and results.
        
    Example:
        >>> response = delete_model(5000)
        >>> print({"status": response.status, "message": response.message})
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    return db.delete_model(model_id)

@mcp.tool()
def update_model(ctx: Context, model_id: str, model_name: str) -> PyModel:
    """
    Update the name of an existing model.
    
    Args:
        model_id (int): The ID of the model to update.
        new_name (str): The new name for the model.
        
    Returns:
        PyResponse[Model]: A response object containing the updated Model object.
        
    Example:
        >>> response = update_model(5000, "bert-large-uncased")
        >>> print({"status": response.status, "message": response.message, "data": response.data})
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    return db.update_model(model_id, model_name)

@mcp.tool()
def get_task(ctx: Context, task_id: Optional[str] = None) -> list[PyTask] | str:
    """
    Retrieve task(s) from the database.
    
    Args:
        task_id (Optional[str]): The specific task ID to retrieve. If None, returns all tasks.
        
    Returns:
        list[Task]: List of Task objects. If task_id is provided, returns a list with one task.
        str: Error message if an exception occurs during the operation.
        
    Example:
        >>> all_tasks = get_task()  # Get all tasks
        >>> specific_task = get_task("123e4567-e89b-12d3-a456-426614174000")  # Get specific task
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    return db.get_task(task_id)
        
@mcp.tool()
def create_task(ctx: Context, model_id: int, dataset_ids: list[str]) -> PyTask | str:
    """
    Create a new task in the database.
    
    Args:
        model_id (int): The ID of the model to use for this task.
        dataset_ids (list[str]): List of dataset IDs to associate with this task.
        status (TaskStatus): The initial status of the task (QUEUED, RUNNING, SUCCESS, FAILED).

    Returns:
        Task: The newly created task object with generated task_id and associated datasets or error messaage if failed.
        
    Example:
        >>> task = create_task("model-123", ["dataset-1", "dataset-2"], TaskStatus.QUEUED)
        >>> print(f"Created task: {task.task_id} with {len(task.datasets)} datasets")
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    return db.create_task(model_id, dataset_ids)

@mcp.tool()
def delete_task(ctx: Context, task_id: str) -> str:
    """
    Delete a task from the database.
    
    Args:
        task_id (str): The ID of the task to delete.
        
    Returns:
        str: A response message indicating success or failure of the deletion.
        
    Note:
        This operation will also delete all associated results.
        
    Example:
        >>> response = delete_task("123e4567-e89b-12d3-a456-426614174000")
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    return db.delete_task(task_id)

@mcp.tool()
def update_task_status(ctx: Context, task_id: str, new_status: TaskStatus) -> PyTask | str:
    """
    Update the status of an existing task.
    
    Args:
        task_id (str): The ID of the task to update.
        new_status (TaskStatus): The new status for the task (QUEUED, RUNNING, SUCCESS, FAILED).
        
    Returns:
        Task: The updated task object, or None if task not found.
        str: Error message if task not found.
                    
    Example:
        >>> updated_task = update_task_status(5000, TaskStatus.SUCCESS)
        >>> print(f"Task status updated to: {updated_task.status.value}")
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    return db.update_task_status(task_id, new_status)

# @mcp.tool()
# def execute_fetch_sql_tool(ctx: Context, command: str, timeout: int = 30) -> str:
#     """
#     Execute a SQL script to fetch information from the database.

#     This function is designed to execute SQL commands that retrieve data, such as 
#     SELECT statements. It interacts with the database configured in the current 
#     context and returns the result as a string representation.

#     Parameters:
#         ctx (Context): The context object that contains the request-specific 
#                        information, including the database connection.
#         command (str): The SQL command to be executed for fetching data. 
#                        It should be a valid SQL SELECT statement.
#         timeout (int, optional): The maximum time in seconds to wait for the 
#                                  SQL command to execute. The default is 30 seconds.

#     Returns:
#         str: A string representation of the rows retrieved from the database. 
#              If no rows are found, it may return an empty string.

#     Raises:
#         Exception: Raises any exceptions that occur during SQL execution, 
#                    such as syntax errors or connection issues.

#     Example:
#         >>> result = execute_fetch_sql_tool(ctx, "SELECT * FROM users;")
#         >>> print(result)  # Outputs the fetched rows as a string.

#     Notes:
#         - Ensure that the provided SQL command is safe and properly sanitized 
#           to prevent SQL injection attacks.
#         - The timeout parameter can be adjusted based on the expected duration 
#           of the SQL operation.
#     """
#     db = ctx.request_context.lifespan_context.db
#     print(f"Executing SQL command: {command} with timeout {timeout}")
#     rows = db.execute_fetch_sql_script(command)
#     return str(rows)

# @mcp.tool()
# def execute_mutate_sql_tool(ctx: Context, command: str, timeout: int = 30) -> str:
#     """
#     Execute a SQL script to mutate the database.

#     This function is intended for executing SQL commands that modify data in 
#     the database, such as INSERT, UPDATE, or DELETE statements. It utilizes 
#     the database connection available in the current context and returns a 
#     response indicating the result of the operation.

#     Parameters:
#         ctx (Context): The context object that holds request-specific information, 
#                        including the database connection.
#         command (str): The SQL command to be executed for mutating data. 
#                        It should be a valid SQL INSERT, UPDATE, or DELETE statement.
#         timeout (int, optional): The maximum time in seconds to wait for the 
#                                  SQL command to execute. The default is 30 seconds.

#     Returns:
#         str: A response message indicating the success or failure of the 
#              mutation operation, which may include the number of affected rows.

#     Raises:
#         Exception: Raises any exceptions encountered during SQL execution, 
#                    which may include syntax errors, constraint violations, 
#                    or connection errors.

#     Example:
#         >>> response = execute_mutate_sql_tool(ctx, "INSERT INTO users (name) VALUES ('John Doe');")
#         >>> print(response)  # Outputs a success message or the number of rows affected.

#     Notes:
#         - Ensure that the provided SQL command is safe and properly validated 
#           to avoid SQL injection vulnerabilities.
#         - The timeout parameter can be adjusted depending on the complexity 
#           of the transaction.
#     """
#     db = ctx.request_context.lifespan_context.db
#     print(f"Executing SQL command: {command} with timeout {timeout}")
#     resp = db.execute_mutate_sql_script(command)
#     return resp

if __name__ == "__main__":
    transport = "sse"  #  stdio, sse
    print(f"MCP server is running on {transport} transport...")
    mcp.run(transport=transport)
