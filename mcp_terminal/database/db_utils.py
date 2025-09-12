from collections.abc import Sequence
from contextlib import contextmanager
import json
from typing import Any, Optional
from sqlalchemy import (
    MetaData, Row, create_engine, text
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from dotenv import load_dotenv
import os

from database.models import Base, Dataset, Model, Result, Task, TaskStatus
from mcp_terminal.database.pydantic_models import PyModel, PyDataset, PyResult, PyTask

class DBUtils:
    """
    Database utility class for managing database connections and operations.
    This class provides methods to create, read, update, and delete models, datasets, tasks, and results.
    It uses SQLAlchemy for ORM and context managers for session management.
    """

    def __init__(self, reset_db: bool = False):
        """
        Initialize the database utility class.
        Loads environment variables for database connection parameters.
        """
    # Load environment variables from .env file
        load_dotenv()

        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_NAME = os.getenv("DB_NAME")

        self.DATABASE_URL = f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # Create engine (long-lived, app-wide)
        self.engine = create_engine(
            self.DATABASE_URL,
            echo=False,         # set True to log SQL
            future=True
        )

        # Session factory (creates new sessions when needed)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

        if reset_db:
            # Drop all tables if reset_db is True
            Base.metadata.drop_all(self.engine)
            # Recreate all tables
            Base.metadata.create_all(self.engine)
            print("Database reset: All tables dropped and recreated.")

    # Dependency / context manager
    @contextmanager
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def introspect_schema(self):
        # Use the engine to reflect the database schema
        metadata = MetaData()
        metadata.reflect(bind=self.engine)

        schema_info = {}
        for table in metadata.tables.values():
            columns = {column.name: str(column.type) for column in table.columns}
            
            # Get foreign key relationships
            foreign_keys = {}
            for column in table.columns:
                # Check if the column has foreign key constraints
                if column.foreign_keys:
                    foreign_keys[column.name] = [fk.column.table.name for fk in column.foreign_keys]
            
            schema_info[table.name] = {
                "columns": columns,
                "foreign_keys": foreign_keys
            }
        
        schema_json = json.dumps(schema_info, indent=4)
        print(schema_json)
        return schema_json

    def execute_fetch_sql_script(self, sql_statement: str) -> Sequence[Row[Any]]:
        """
        Execute the SQL script for requesting informatiion from the database like SELECT.
        """
        with self.get_db() as db:
            try:
                result = db.execute(text(sql_statement))
                rows = result.fetchall()
                for row in rows:
                    print(row)
                return rows
            except Exception as e:
                # e.g. for DDL statements (CREATE, DROP) fetchall() will fail
                print(f"Error executing SQL: {e}")
                return None

    def execute_mutate_sql_script(self, sql_statement: str) -> Sequence[Row[Any]]:
        """
        Execute the SQL script for mutating the database like INSERT, UPDATE, DELETE.
        """
        with self.get_db() as db:
            try:
                result = db.execute(text(sql_statement))
                db.commit()  # Commit the transaction if it's an INSERT or UPDATE
                return "SQL statement executed successfully."
            except Exception as e:
                # e.g. for DDL statements (CREATE, DROP) fetchall() will fail
                print(f"Error executing SQL: {e}")
                return None

    # --- MODEL CRUD ---
    def create_model(self, model_name: str) -> PyModel:
        """
        Create a new model in the database.
        
        Args:
            model_name (str): The name of the model to be created.
            
        Returns:
            PyModel: A PyModel object representing the created model or error message
                    
        Example:
            >>> response = create_model("bert-base-uncased")
            >>> print({"status": response.status, "message": response.message, "data": response.data})
        """
        try:
            with self.get_db() as db:
                model = Model(model_name=model_name)
                db.add(model)
                db.commit()
                db.refresh(model)

                # Convert to Pydantic models
                pydantic_model = PyModel.model_validate(model)
                return pydantic_model
        except Exception as e:
            print (f"Error creating model: {str(e)}")

# Error executing tool create_model: 1 validation error for PyModel
#   Input should be a valid dictionary or instance of PyModel [type=model_type, input_value=<database.models.Model object at 0x109fe0110>, input_type=Model]
#     For further information visit https://errors.pydantic.dev/2.11/v/model_type
    def get_model(self, model_id: Optional[int] = None) -> list[PyModel]:
        """
        Retrieve model(s) from the database.
        
        Args:
            model_id (Optional[int]): The specific model ID to retrieve. If None, returns all models.
            
        Returns:
            list[Model]: List of Model objects. If model_id is provided, returns a list with one model.
            
        Example:
            >>> all_models = get_model()  # Get all models
            >>> specific_model = get_model(512)  # Get specific model
        """
        db_models = []
        with self.get_db() as db:
            if model_id:
                db_models = db.query(Model).filter(Model.model_id == model_id)
            else:
                db_models = db.query(Model).all()

        # Convert to Pydantic models
        pydantic_models = [PyModel.model_validate(model) for model in db_models]
        return pydantic_models

    def update_model(self, model_id: int, new_name: str) -> PyModel:
        """
        Update the name of an existing model.
        
        Args:
            model_id (int): The ID of the model to update.
            new_name (str): The new name for the model.
            
        Returns:
            PyModel: The updated model object or error
            
        Example:
            >>> updated_model = update_model(5000, "bert-large-uncased")
        """
        with self.get_db() as db:
            db_model = db.query(Model).filter(Model.model_id == model_id).first()
            if db_model:
                db_model.model_name = new_name
                db.commit()
                db.refresh(db_model)

                # Convert to Pydantic models
                pydantic_model = PyModel.model_validate(db_model)
                return pydantic_model

            return 'Model not found'
        
    def delete_model(self, model_id: int) -> str:
        """
        Delete a model from the database.
        
        Args:
            model_id (int): The ID of the model to delete.
            
        Returns:
            str: successs or error message
            
        Note:
            This operation will cascade delete all associated tasks and results.
            
        Example:
            >>> success = delete_model(5000)
            >>> print(f"Model deletion: {'Success' if success else 'Failed'}")
        """
        try:
            with self.get_db() as db:
                db_model = db.query(Model).filter(Model.model_id == model_id).first()
                if db_model is None:
                    raise ValueError(f"Model with ID {model_id} not found.")

                if db_model:
                    db.delete(db_model)
                    db.commit()
                    return "Model has been deleted"
        except Exception as e:
            return (f"Error deleting model: {str(e)}")

    # --- DATASET CRUD ---
    def create_dataset(self, dataset_name: str) -> Dataset:
        """
        Create a new dataset in the database.
        
        Args:
            dataset_name (str): The name of the dataset to be created.
            
        Returns:
            Dataset: The newly created dataset object with generated dataset_id.
            
        Example:
            >>> dataset = create_dataset("imagenet-1k")
            >>> print(f"Created dataset: {dataset.dataset_id} - {dataset.dataset_name}")
        """
        with self.get_db() as db:
            dataset = Dataset(dataset_name=dataset_name)
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            return dataset

    def get_dataset(self, dataset_id: Optional[str] = None) -> list[Dataset]:
        """
        Retrieve dataset(s) from the database.
        
        Args:
            dataset_id (Optional[str]): The specific dataset ID to retrieve. If None, returns all datasets.
            
        Returns:
            list[Dataset]: List of Dataset objects. If dataset_id is provided, returns a list with one dataset.
            
        Example:
            >>> all_datasets = get_dataset()  # Get all datasets
            >>> specific_dataset = get_dataset(5000)  # Get specific dataset
        """
        with self.get_db() as db:
            if dataset_id:
                return db.query(Dataset).filter(Dataset.dataset_id == dataset_id)
            
            return db.query(Dataset).all()

    def update_dataset(self, dataset_id: str, new_name: str) -> Dataset:
        """
        Update the name of an existing dataset.
        
        Args:
            dataset_id (str): The ID of the dataset to update.
            new_name (str): The new name for the dataset.
            
        Returns:
            Dataset: The updated dataset object, or None if dataset not found.
            
        Example:
            >>> updated_dataset = update_dataset(5000, "imagenet-21k")
            >>> print(f"Updated dataset name to: {updated_dataset.dataset_name}")
        """
        with self.get_db() as db:
            dataset = self.get_dataset(db, dataset_id)
            if dataset:
                dataset.dataset_name = new_name
                db.commit()
                db.refresh(dataset)
            return dataset

    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete a dataset from the database.
        
        Args:
            dataset_id (str): The ID of the dataset to delete.
            
        Returns:
            bool: True if the dataset was successfully deleted, False if dataset not found.
            
        Note:
            This operation will remove the dataset from all associated tasks.
            
        Example:
            >>> success = delete_dataset(5000)
            >>> print(f"Dataset deletion: {'Success' if success else 'Failed'}")
        """
        with self.get_db() as db:
            dataset = self.get_dataset(db, dataset_id)
            if dataset:
                db.delete(dataset)
                db.commit()
                return True
            return False

    # --- TASK CRUD ---
    def create_task(self, model_id: int, dataset_ids: list[str]) -> PyTask | str:
        """
        Create a new task in the database.
        
        Args:
            model_id (int): The ID of the model to use for this task.
            dataset_ids (list[str]): List of dataset IDs to associate with this task.
            status (TaskStatus): The initial status of the task (QUEUED, RUNNING, SUCCESS, FAILED).
            
        Returns:
            Task: The newly created task object with generated task_id and associated datasets.
            str: Error message if task creation fails.
            
        Example:
            >>> task = create_task("model-123", ["dataset-1", "dataset-2"], TaskStatus.QUEUED)
            >>> print(f"Created task: {task.task_id} with {len(task.datasets)} datasets")
        """
        try:
            with self.get_db() as db:
                datasets = db.query(Dataset).filter(Dataset.dataset_id.in_(dataset_ids)).all()
                task = Task(
                    model_id=model_id,
                    status=TaskStatus.QUEUED,
                    datasets=datasets
                )
                db.add(task)
                db.commit()
                db.refresh(task)

                return PyTask.model_validate(task)
        except Exception as e:
            return f"Error creating task: {e}"

    def get_task(self, task_id: Optional[str] = None) -> list[Task]:
        """
        Retrieve task(s) from the database with related model and dataset information.
        
        Args:
            task_id (Optional[str]): The specific task ID to retrieve. If None, returns all tasks.
            
        Returns:
            list[Task]: List of Task objects with loaded model and datasets relationships.
            
        Example:
            >>> all_tasks = get_task()  # Get all tasks with relationships
            >>> specific_task = get_task(5000)  # Get specific task
            >>> print(f"Task {specific_task.task_id} uses model: {specific_task.model.model_name}")
        """
        db_tasks: list[Task] = []
        try:
            with self.get_db() as db:
                query = db.query(Task).options(
                    joinedload(Task.model),
                    joinedload(Task.datasets)
                )
                if task_id:
                    db_tasks = query.filter(Task.task_id == task_id)
                else:
                    db_tasks = query.all()

            # Convert to Pydantic models
            pydantic_models = [PyTask.model_validate(task) for task in db_tasks]
            return pydantic_models
        except Exception as e:
            return f"Error retrieving tasks: {e}"

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> PyTask | str:
        """
        Update the status of an existing task.
        
        Args:
            task_id (str): The ID of the task to update.
            new_status (TaskStatus): The new status for the task (QUEUED, RUNNING, SUCCESS, FAILED).
            
        Returns:
            Task: The updated task object, or None if task not found.
                        
        Example:
            >>> updated_task = update_task_status(5000, TaskStatus.SUCCESS)
            >>> print(f"Task status updated to: {updated_task.status.value}")
        """
        try:
            with self.get_db() as db:
                task = self.get_task(task_id)
                if task:
                    task.status = new_status
                    db.commit()
                    db.refresh(task)

                    return PyTask.model_validate(task)
                else:
                    raise ValueError(f"Task with ID {task_id} not found")
        except Exception as e:
            print (f"Error updating task status: {e}")

    def delete_task(self, task_id: str) -> str:
        """
        Delete a task from the database.
        
        Args:
            task_id (str): The ID of the task to delete.
            
        Returns:
            bool: True if the task was successfully deleted, False if task not found.
            
        Note:
            This operation will cascade delete all associated results.
            
        Example:
            >>> success = delete_task(5000)
            >>> print(f"Task deletion: {'Success' if success else 'Failed'}")
        """
        try:
            with self.get_db() as db:
                task = self.get_task(task_id)
                if task:
                    db.delete(task)
                    db.commit()
                    return "Task deleted successfully"
                else:
                    raise ValueError(f"Task with ID {task_id} not found")
        except Exception as e:
            print (f"Error deleting task: {e}")

    # --- RESULT CRUD ---
    def create_result(self, task_id: str, category: str, value: float) -> Result:
        """
        Create a new result in the database.
        
        Args:
            task_id (str): The ID of the task this result belongs to.
            category (str): The category/class label for this result (e.g., 'dog', 'cat').
            value (float): The numerical value/score for this result.
            
        Returns:
            Result: The newly created result object with generated result_id.
            
        Example:
            >>> result = create_result("task-123", "dog", 95.5)
            >>> print(f"Created result: {result.result_id} - {result.category}: {result.value}")
        """
        try:
            with self.get_db() as db:
                result = Result(task_id=task_id, category=category, value=value)
                db.add(result)
                db.commit()
                db.refresh(result)
                return result
        except Exception as e:
            print (f"Error creating result: {str(e)}")

    def get_result(self, result_id: Optional[str] = None) -> list[PyResult]:
        """
        Retrieve result(s) from the database.
        
        Args:
            result_id (Optional[str]): The specific result ID to retrieve. If None, returns all results.
            
        Returns:
            list[Result]: List of Result objects. If result_id is provided, returns a list with one result.
            
        Example:
            >>> all_results = get_result()  # Get all results
            >>> specific_result = get_result(5000)  # Get specific result
        """
        try:
            db_results: list[Result] = []
            with self.get_db() as db:
                if result_id:
                    db_results = db.query(Result).options(joinedload(Task.model)).filter(Result.result_id == result_id)
                else:
                 db_results = db.query(Result).all()

            pydantic_results = [PyResult.model_validate(result) for result in db_results]
            return pydantic_results
        except Exception as e:
            print (f"Error retrieving results: {str(e)}")

    def update_result_value(self, result_id: str, new_value: float) -> PyResult:
        """
        Update the value of an existing result.
        
        Args:
            result_id (str): The ID of the result to update.
            new_value (float): The new numerical value for the result.
            
        Returns:
            Result: The updated result object, or None if result not found.
            
        Example:
            >>> updated_result = update_result_value(5000, 98.7)
            >>> print(f"Result value updated to: {updated_result.value}")
        """
        try:
            with self.get_db() as db:
                result = self.get_result(result_id)
                if result:
                    result.value = new_value
                    db.commit()
                    db.refresh(result)
                    return PyTask.model_validate(result)
                else:
                    raise ValueError(f"Result with ID {result_id} not found")
        except Exception as e:
            print (f"Error updating result value: {str(e)}")

    def delete_result(self, result_id: str) -> str:
        """
        Delete a result from the database.
        
        Args:
            result_id (str): The ID of the result to delete.
            
        Returns:
            bool: True if the result was successfully deleted, False if result not found.
            
        Example:
            >>> success = delete_result(5000)
            >>> print(f"Result deletion: {'Success' if success else 'Failed'}")
        """
        try:
            with self.get_db() as db:
                result = self.get_result(result_id)
                if result:
                    db.delete(result)
                    db.commit()
                    return "Result deleted successfully"
        except Exception as e:
            print (f"Error deleting result: {str(e)}")            

if __name__ == "__main__":
    db_utils = DBUtils(reset_db=True)  # Set to True to reset the database

    # Create models
    m1 = db_utils.create_model('model_a')
    m2 = db_utils.create_model('model_b')

    # Create datasets
    d1 = db_utils.create_dataset('dataset_a')
    d2 = db_utils.create_dataset('dataset_b')
    d3 = db_utils.create_dataset('dataset_c')
    d4 = db_utils.create_dataset('dataset_d')

    # Create tasks
    task1 = db_utils.create_task(m1.model_id, [d1.dataset_id, d2.dataset_id], TaskStatus.SUCCESS)
    task2 = db_utils.create_task(m2.model_id, [d1.dataset_id, d2.dataset_id], TaskStatus.SUCCESS)
    task3 = db_utils.create_task(m2.model_id, [d3.dataset_id, d4.dataset_id], TaskStatus.RUNNING)

    # Create Results
    db_utils.create_result(task1.task_id, 'dog', 90.9)
    db_utils.create_result(task1.task_id, 'cat', 78.9)
    db_utils.create_result(task1.task_id, 'bird', 34.9)

    db_utils.create_result(task2.task_id, 'dog', 60.9)
    db_utils.create_result(task2.task_id, 'cat', 98.9)
    db_utils.create_result(task2.task_id, 'bird', 88.9)

    # try:
    #     while True:
    #         user_input = input("Enter your prompt (or type 'exit()' to quit): ")
    #         user_input = user_input.strip()
    #         if user_input == "exit()":
    #             print("Exiting...")
    #             break
    #         if 'exit' in user_input:
    #             print("Do you mean to exit? Please type 'exit()' to quit.")
    #             break

    #         resp = db_utils.execute_fetch_sql_script(user_input)
    #         # db_utils.execute_mutate_sql_script(user_input)
    #         print(resp)

    # except KeyboardInterrupt:
    #     print("\nExiting...")