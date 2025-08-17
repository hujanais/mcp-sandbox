import asyncio

from contextlib import contextmanager
from ctypes import Union
from typing import Optional
from uuid import uuid4
from requests import Session
from sqlalchemy import (
    Integer, create_engine, Column, String, Float, Enum, ForeignKey, Table, text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.orm import joinedload
from dotenv import load_dotenv
import enum
import os

from models import Base, Dataset, Model, Result, Task, TaskStatus

# Load environment variables from .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine (long-lived, app-wide)
engine = create_engine(
    DATABASE_URL,
    echo=False,         # set True to log SQL
    future=True
)

# Session factory (creates new sessions when needed)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# Dependency / context manager
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_sql_script(sql_statement: str):
    """
    Execute the SQL script using the get_db session context.
    """
    with get_db() as db:
        result = db.execute(text(sql_statement))
        try:
            rows = result.fetchall()
            return rows
        except Exception:
            # e.g. for DDL statements (CREATE, DROP) fetchall() will fail
            print("SQL executed successfully (no rows returned).")
            return None

# --- MODEL CRUD ---
def create_model(model_name: str) -> Model:
    """
    Create a new model in the database.
    
    Args:
        model_name (str): The name of the model to be created.
        
    Returns:
        Model: The newly created model object with generated model_id.
        
    Example:
        >>> model = create_model("bert-base-uncased")
        >>> print(f"Created model: {model.model_id} - {model.model_name}")
    """
    with get_db() as db:
        model = Model(model_id=str(uuid4()), model_name=model_name)
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

def get_model(model_id: Optional[str] = None) -> list[Model]:
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
    with get_db() as db:
        if model_id:
            return db.query(Model).filter(Model.model_id == model_id)
        
        return db.query(Model).all()

def update_model(model_id: str, new_name: str) -> Model:
    """
    Update the name of an existing model.
    
    Args:
        model_id (str): The ID of the model to update.
        new_name (str): The new name for the model.
        
    Returns:
        Model: The updated model object, or None if model not found.
        
    Example:
        >>> updated_model = update_model("123e4567-e89b-12d3-a456-426614174000", "bert-large-uncased")
        >>> print(f"Updated model name to: {updated_model.model_name}")
    """
    with get_db() as db:
        model = get_model(db, model_id)
        if model:
            model.model_name = new_name
            db.commit()
            db.refresh(model)
        return model

def delete_model(model_id: str) -> bool:
    """
    Delete a model from the database.
    
    Args:
        model_id (str): The ID of the model to delete.
        
    Returns:
        bool: True if the model was successfully deleted, False if model not found.
        
    Note:
        This operation will cascade delete all associated tasks and results.
        
    Example:
        >>> success = delete_model("123e4567-e89b-12d3-a456-426614174000")
        >>> print(f"Model deletion: {'Success' if success else 'Failed'}")
    """
    with get_db() as db:
        model = get_model(db, model_id)
        if model:
            db.delete(model)
            db.commit()
            return True
        return False

# --- DATASET CRUD ---
def create_dataset(dataset_name: str) -> Dataset:
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
    with get_db() as db:
        dataset = Dataset(dataset_id=str(uuid4()), dataset_name=dataset_name)
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

def get_dataset(dataset_id: Optional[str] = None) -> list[Dataset]:
    """
    Retrieve dataset(s) from the database.
    
    Args:
        dataset_id (Optional[str]): The specific dataset ID to retrieve. If None, returns all datasets.
        
    Returns:
        list[Dataset]: List of Dataset objects. If dataset_id is provided, returns a list with one dataset.
        
    Example:
        >>> all_datasets = get_dataset()  # Get all datasets
        >>> specific_dataset = get_dataset("123e4567-e89b-12d3-a456-426614174000")  # Get specific dataset
    """
    with get_db() as db:
        if dataset_id:
            return db.query(Dataset).filter(Dataset.dataset_id == dataset_id)
        
        return db.query(Dataset).all()

def update_dataset(dataset_id: str, new_name: str) -> Dataset:
    """
    Update the name of an existing dataset.
    
    Args:
        dataset_id (str): The ID of the dataset to update.
        new_name (str): The new name for the dataset.
        
    Returns:
        Dataset: The updated dataset object, or None if dataset not found.
        
    Example:
        >>> updated_dataset = update_dataset("123e4567-e89b-12d3-a456-426614174000", "imagenet-21k")
        >>> print(f"Updated dataset name to: {updated_dataset.dataset_name}")
    """
    with get_db() as db:
        dataset = get_dataset(db, dataset_id)
        if dataset:
            dataset.dataset_name = new_name
            db.commit()
            db.refresh(dataset)
        return dataset

def delete_dataset(dataset_id: str) -> bool:
    """
    Delete a dataset from the database.
    
    Args:
        dataset_id (str): The ID of the dataset to delete.
        
    Returns:
        bool: True if the dataset was successfully deleted, False if dataset not found.
        
    Note:
        This operation will remove the dataset from all associated tasks.
        
    Example:
        >>> success = delete_dataset("123e4567-e89b-12d3-a456-426614174000")
        >>> print(f"Dataset deletion: {'Success' if success else 'Failed'}")
    """
    with get_db() as db:
        dataset = get_dataset(db, dataset_id)
        if dataset:
            db.delete(dataset)
            db.commit()
            return True
        return False

# --- TASK CRUD ---
def create_task(model_id: str, dataset_ids: list[str], status: TaskStatus) -> Task:
    """
    Create a new task in the database.
    
    Args:
        model_id (str): The ID of the model to use for this task.
        dataset_ids (list[str]): List of dataset IDs to associate with this task.
        status (TaskStatus): The initial status of the task (QUEUED, RUNNING, SUCCESS, FAILED).
        
    Returns:
        Task: The newly created task object with generated task_id and associated datasets.
        
    Example:
        >>> task = create_task("model-123", ["dataset-1", "dataset-2"], TaskStatus.QUEUED)
        >>> print(f"Created task: {task.task_id} with {len(task.datasets)} datasets")
    """
    with get_db() as db:
        datasets = db.query(Dataset).filter(Dataset.dataset_id.in_(dataset_ids)).all()
        task = Task(
            task_id=str(uuid4()),
            model_id=model_id,
            status=status,
            datasets=datasets
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

def get_task(task_id: Optional[str] = None) -> list[Task]:
    """
    Retrieve task(s) from the database with related model and dataset information.
    
    Args:
        task_id (Optional[str]): The specific task ID to retrieve. If None, returns all tasks.
        
    Returns:
        list[Task]: List of Task objects with loaded model and datasets relationships.
        
    Example:
        >>> all_tasks = get_task()  # Get all tasks with relationships
        >>> specific_task = get_task("123e4567-e89b-12d3-a456-426614174000")  # Get specific task
        >>> print(f"Task {specific_task.task_id} uses model: {specific_task.model.model_name}")
    """
    with get_db() as db:
        query = db.query(Task).options(
            joinedload(Task.model),
            joinedload(Task.datasets)
        )
        if task_id:
            return query.filter(Task.task_id == task_id)

        return query.all()

def update_task_status(task_id: str, new_status: TaskStatus) -> Task:
    """
    Update the status of an existing task.
    
    Args:
        task_id (str): The ID of the task to update.
        new_status (TaskStatus): The new status for the task (QUEUED, RUNNING, SUCCESS, FAILED).
        
    Returns:
        Task: The updated task object, or None if task not found.
        
    Example:
        >>> updated_task = update_task_status("123e4567-e89b-12d3-a456-426614174000", TaskStatus.SUCCESS)
        >>> print(f"Task status updated to: {updated_task.status.value}")
    """
    with get_db() as db:
        task = get_task(db, task_id)
        if task:
            task.status = new_status
            db.commit()
            db.refresh(task)
        return task

def delete_task(task_id: str) -> bool:
    """
    Delete a task from the database.
    
    Args:
        task_id (str): The ID of the task to delete.
        
    Returns:
        bool: True if the task was successfully deleted, False if task not found.
        
    Note:
        This operation will cascade delete all associated results.
        
    Example:
        >>> success = delete_task("123e4567-e89b-12d3-a456-426614174000")
        >>> print(f"Task deletion: {'Success' if success else 'Failed'}")
    """
    with get_db() as db:
        task = get_task(db, task_id)
        if task:
            db.delete(task)
            db.commit()
            return True
        return False

# --- RESULT CRUD ---
def create_result(task_id: str, category: str, value: float) -> Result:
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
    with get_db() as db:
        result = Result(task_id=task_id, category=category, value=value)
        db.add(result)
        db.commit()
        db.refresh(result)
        return result

def get_result(result_id: Optional[str] = None) -> list[Result]:
    """
    Retrieve result(s) from the database.
    
    Args:
        result_id (Optional[str]): The specific result ID to retrieve. If None, returns all results.
        
    Returns:
        list[Result]: List of Result objects. If result_id is provided, returns a list with one result.
        
    Example:
        >>> all_results = get_result()  # Get all results
        >>> specific_result = get_result("123e4567-e89b-12d3-a456-426614174000")  # Get specific result
    """
    with get_db() as db:
        if result_id:
            return db.query(Result).options(joinedload(Task.model)).filter(Result.result_id == result_id)

        return db.query(Result).all()

def update_result_value(result_id: str, new_value: float) -> Result:
    """
    Update the value of an existing result.
    
    Args:
        result_id (str): The ID of the result to update.
        new_value (float): The new numerical value for the result.
        
    Returns:
        Result: The updated result object, or None if result not found.
        
    Example:
        >>> updated_result = update_result_value("123e4567-e89b-12d3-a456-426614174000", 98.7)
        >>> print(f"Result value updated to: {updated_result.value}")
    """
    with get_db() as db:
        result = get_result(db, result_id)
        if result:
            result.value = new_value
            db.commit()
            db.refresh(result)
        return result

def delete_result(result_id: str) -> bool:
    """
    Delete a result from the database.
    
    Args:
        result_id (str): The ID of the result to delete.
        
    Returns:
        bool: True if the result was successfully deleted, False if result not found.
        
    Example:
        >>> success = delete_result("123e4567-e89b-12d3-a456-426614174000")
        >>> print(f"Result deletion: {'Success' if success else 'Failed'}")
    """
    with get_db() as db:
        result = get_result(db, result_id)
        if result:
            db.delete(result)
            db.commit()
            return True
        return False

if __name__ == "__main__":
    # Drop all tables
    Base.metadata.drop_all(engine)

    # Recreate all tables
    Base.metadata.create_all(engine)

    # # Create models
    m1 = create_model('model_a')
    m2 = create_model('model_b')

    # Create datasets
    d1 = create_dataset('dataset_a')
    d2 = create_dataset('dataset_b')
    d3 = create_dataset('dataset_c')
    d4 = create_dataset('dataset_d')

    # Create tasks
    task1 = create_task(m1.model_id, [d1.dataset_id, d2.dataset_id], TaskStatus.SUCCESS)
    task2 = create_task(m2.model_id, [d1.dataset_id, d2.dataset_id], TaskStatus.SUCCESS)
    task3 = create_task(m2.model_id, [d3.dataset_id, d4.dataset_id], TaskStatus.RUNNING)

    # Create Results
    create_result(task1.task_id, 'dog', 90.9)
    create_result(task1.task_id, 'cat', 78.9)
    create_result(task1.task_id, 'bird', 34.9)

    create_result(task2.task_id, 'dog', 60.9)
    create_result(task2.task_id, 'cat', 98.9)
    create_result(task2.task_id, 'bird', 88.9)