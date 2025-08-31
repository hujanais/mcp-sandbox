async def execute_sql(command: str, timeout: int = 30) -> str:
    """
    Execute the SQL script using the get_db session context.
    """
    print(f"Executing SQL command: {command} with timeout {timeout}")
    return {"data" :["jack", "jill", "bobbie"]}

async def get_db_schema(timeout: int = 30) -> str:
    """
    Retrieve the database schema and useful information about the database.
    """
    print(f"Retrieving DB schema with timeout {timeout}")
    return {"data" :["table1", "table2", "table3"]}