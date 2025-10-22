from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

import sys
import os
from typing import Optional

from database.models import TaskStatus


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastmcp import Context, FastMCP
from database.db_utils import DBUtils
from database.pydantic_models import PyModel, PyResult, PyTask


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


@mcp.tool("get_db_schema")
def get_db_schema(ctx: Context) -> str:
    """
    Retrieve the database schema and useful information about the database.
    This will return the CREATE TABLE scripts and associated relationships.
    """
    _ = ctx  # Reference ctx to avoid "not accessed" error
    return """
    # Enum for task status
        class TaskStatus(enum.Enum):
            QUEUED = "QUEUED"
            RUNNING = "RUNNING"
            SUCCESS = "SUCCESS"
            FAILED = "FAILED"

        # Association table for many-to-many between Task and Dataset
        task_dataset_association = Table(
            "task_dataset",
            Base.metadata,
            Column("task_id", Integer, ForeignKey("task.task_id", ondelete="CASCADE"), primary_key=True),
            Column("dataset_id", Integer, ForeignKey("dataset.dataset_id", ondelete="CASCADE"), primary_key=True)
        )

        class Model(Base):
            __tablename__ = "model"
            model_id = Column(Integer, primary_key=True, autoincrement=True)
            model_name = Column(String, nullable=False)

            tasks = relationship("Task", back_populates="model", cascade="all, delete")

        class Dataset(Base):
            __tablename__ = "dataset"
            dataset_id = Column(Integer, primary_key=True, autoincrement=True)
            dataset_name = Column(String, nullable=False)

            tasks = relationship(
                "Task",
                secondary=task_dataset_association,
                back_populates="datasets"
            )

        class Task(Base):
            __tablename__ = "task"
            task_id = Column(Integer, primary_key=True, autoincrement=True)
            model_id = Column(Integer, ForeignKey("model.model_id", ondelete="CASCADE"), nullable=False)
            status = Column(Enum(TaskStatus), nullable=False)

            model = relationship("Model", back_populates="tasks")
            datasets = relationship(
                "Dataset",
                secondary=task_dataset_association,
                back_populates="tasks"
            )
            result = relationship("Result", back_populates="task", uselist=False, cascade="all, delete")

        class Result(Base):
            __tablename__ = "result"
            result_id = Column(Integer, primary_key=True, autoincrement=True)
            task_id = Column(Integer, ForeignKey("task.task_id", ondelete="CASCADE"), nullable=False)
            value = Column(Float, nullable=False)
            category = Column(String, nullable=True)

            task = relationship("Task", back_populates="result")
        """


@mcp.tool()
def get_model(ctx: Context, model_id: Optional[str] = None) -> list[PyModel]:
    """
    Retrieve model(s) from the database.

    Args:
        model_id (Optional[str]): The specific model ID to retrieve. If None, returns all models.

    Returns:
        list[PyModel]: List of Pydantic Model objects. If model_id is provided, returns a list with one model.

    Example:
        >>> all_models = get_model()  # Get all models
        >>> specific_model = get_model("123e4567-e89b-12d3-a456-426614174000")  # Get specific model
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    sqlalchemy_models = db.get_model(int(model_id) if model_id else None)
    return [PyModel.model_validate(model) for model in sqlalchemy_models]


@mcp.tool()
def create_model(ctx: Context, model_name: str) -> PyModel:
    """
    Create a new model in the database.

    Args:
        model_name (str): The name of the model to be created.

    Returns:
        PyModel: A Pydantic Model object containing the created model.

    Example:
        >>> model = create_model("bert-base-uncased")
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    sqlalchemy_model = db.create_model(model_name)
    return PyModel.model_validate(sqlalchemy_model)


@mcp.tool()
def delete_model(ctx: Context, model_id: int) -> str:
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
def update_model(ctx: Context, model_id: int, model_name: str) -> PyModel:
    """
    Update the name of an existing model.

    Args:
        model_id (int): The ID of the model to update.
        model_name (str): The new name for the model.

    Returns:
        PyModel: A Pydantic Model object containing the updated model.

    Example:
        >>> response = update_model(5000, "bert-large-uncased")
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    sqlalchemy_model = db.update_model(model_id, model_name)
    return PyModel.model_validate(sqlalchemy_model)


@mcp.tool()
def get_task(ctx: Context, task_id: Optional[str] = None) -> list[PyTask] | str:
    """
    Retrieve one or more tasks from the database.

    Args:
        task_id (Optional[str]): The specific task ID to retrieve. If None, returns all tasks.

    Returns:
        list[PyTask]: List of Pydantic Task objects if successful.
        str: Error message if an error or exception occurs (e.g., not found, database error).

    Notes:
        This function may return a string error message instead of a list if an exception is raised or the query fails. This pattern is used throughout the MCP API to provide clear error feedback in protocol responses.

    Example:
        >>> all_tasks = get_task(ctx)
        >>> specific_task = get_task(ctx, "123e4567-e89b-12d3-a456-426614174000")
        >>> if isinstance(specific_task, str):
        ...     print(f"Error: {specific_task}")
        ... else:
        ...     print(specific_task)
    """
    try:
        db: DBUtils = ctx.request_context.lifespan_context.db
        sqlalchemy_tasks = db.get_task(task_id)
        return [PyTask.model_validate(task) for task in sqlalchemy_tasks]
    except Exception as e:
        return f"Error retrieving tasks: {e}"


@mcp.tool()
def create_task(ctx: Context, model_id: int, dataset_ids: list[str]) -> PyTask | str:
    """
    Create a new task in the database.

    Args:
        model_id (int): The ID of the model to use for this task.
        dataset_ids (list[str]): List of dataset IDs to associate with this task.

    Returns:
        PyTask: The newly created Pydantic task object if successful.
        str: Error message if creation fails (e.g., invalid model, database error).

    Notes:
        Functions in the MCP API may return either a data object or a string error message. Always check the return type before using the result.

    Example:
        >>> result = create_task(ctx, 123, ["ds1", "ds2"])
        >>> if isinstance(result, str):
        ...     print(f"Error: {result}")
        ... else:
        ...     print(f"Created task: {result.task_id}")
    """
    try:
        db: DBUtils = ctx.request_context.lifespan_context.db
        sqlalchemy_task = db.create_task(model_id, dataset_ids)
        return PyTask.model_validate(sqlalchemy_task)
    except Exception as e:
        return f"Error creating task: {e}"


@mcp.tool()
def delete_task(ctx: Context, task_id: int) -> str:
    """
    Delete a task from the database.

    Args:
        task_id (int): The ID of the task to delete.

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
def update_task_status(ctx: Context, task_id: int, new_status: TaskStatus) -> PyTask | str:
    """
    Update the status of an existing task.

    Args:
        task_id (int): The ID of the task to update.
        new_status (TaskStatus): The new status for the task (QUEUED, RUNNING, SUCCESS, FAILED).

    Returns:
        PyTask: The updated Pydantic task object if successful.
        str: Error message if the task is not found or update fails.

    Notes:
        MCP API functions may return either a data object or a string error message. Always check the return type before using the result.

    Example:
        >>> result = update_task_status(ctx, "task-123", TaskStatus.SUCCESS)
        >>> if isinstance(result, str):
        ...     print(f"Error: {result}")
        ... else:
        ...     print(f"Task status updated to: {result.status.value}")
    """
    try:
        db: DBUtils = ctx.request_context.lifespan_context.db
        task = db.update_task_status(task_id, new_status)
        return PyTask(task_id=task.task_id, status=task.status, model_id=task.model_id, datasets=[])
    except Exception as e:
        return f"Error updating task status: {e}"


@mcp.tool()
def get_result(ctx: Context, result_id: Optional[str] = None) -> list[PyResult] | str:
    """
    Retrieve one or more results from the database.

    Args:
        result_id (Optional[str]): The specific result ID to retrieve. If None, returns all results.

    Returns:
        list[PyResult]: List of Pydantic Result objects if successful.
        str: Error message if an error or exception occurs (e.g., not found, database error).

    Notes:
        This function may return a string error message instead of a list if an exception is raised or the query fails. This pattern is used throughout the MCP API to provide clear error feedback in protocol responses.

    Example:
        >>> all_results = get_result(ctx)
        >>> specific_result = get_result(ctx, "result-123")
        >>> if isinstance(specific_result, str):
        ...     print(f"Error: {specific_result}")
        ... else:
        ...     print(specific_result)
    """
    try:
        db: DBUtils = ctx.request_context.lifespan_context.db
        sqlalchemy_results = db.get_result(int(result_id) if result_id else None)
        return [PyResult.model_validate(result) for result in sqlalchemy_results]
    except Exception as e:
        return f"Error retrieving results: {e}"


@mcp.tool()
def create_result(ctx: Context, task_id: int, category: str, value: float) -> PyResult | str:
    """
    Create a new result in the database.
    Args:
        task_id (int): The ID of the task associated with this result.
        category (str): The category of the result.
        value (float): The value of the result.
    Returns:
        PyResult: The created Pydantic Result object if successful.
        str: Error message if creation fails (e.g., invalid task, database error).
    Notes:
        Functions in the MCP API may return either a data object or a string error message. Always check the return type before using the result.
    Example:
        >>> result = create_result(ctx, "task-123", "accuracy", 0.95)
        >>> if isinstance(result, str):
        ...     print(f"Error: {result}")
        ... else:
        ...     print(f"Created result: {result.result_id}")
    """
    try:
        db: DBUtils = ctx.request_context.lifespan_context.db
        sqlalchemy_result = db.create_result(task_id, category, value)
        return PyResult.model_validate(sqlalchemy_result)
    except Exception as e:
        return f"Error creating result: {e}"


@mcp.tool()
def update_result_value(ctx: Context, result_id: int, new_value: float) -> PyResult | str:
    """
    Update the value of an existing result.

    Args:
        result_id (int): The ID of the result to update.
        new_value (float): The new value for the result.

    Returns:
        PyResult: The updated Pydantic Result object if successful.
        str: Error message if the result is not found or update fails.

    Notes:
        MCP API functions may return either a data object or a string error message. Always check the return type before using the result.

    Example:
        >>> result = update_result_value(ctx, "result-123", 0.95)
        >>> if isinstance(result, str):
        ...     print(f"Error: {result}")
        ... else:
        ...     print(f"Result value updated to: {result.value}")
    """
    try:
        db: DBUtils = ctx.request_context.lifespan_context.db
        sqlalchemy_result = db.update_result_value(result_id, new_value)
        return PyResult.model_validate(sqlalchemy_result)
    except Exception as e:
        return f"Error updating result value: {e}"


@mcp.tool()
def delete_result(ctx: Context, result_id: int) -> str:
    """
    Delete a result from the database.

    Args:
        result_id (int): The ID of the result to delete.
    Returns:
        str: A response message indicating success or failure of the deletion.
    Example:
        >>> response = delete_result(5000)
        >>> print(response)  # Outputs success or failure message.
    """
    db: DBUtils = ctx.request_context.lifespan_context.db
    return db.delete_result(result_id)


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
