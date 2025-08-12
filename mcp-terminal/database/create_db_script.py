from ctypes import Union
from typing import Optional
from uuid import uuid4
from requests import Session
from sqlalchemy import (
    create_engine, Column, String, Float, Enum, ForeignKey, Table
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.orm import joinedload
from dotenv import load_dotenv
import enum
import os

# Load environment variables from .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()

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
    Column("task_id", String, ForeignKey("task.task_id", ondelete="CASCADE"), primary_key=True),
    Column("dataset_id", String, ForeignKey("dataset.dataset_id", ondelete="CASCADE"), primary_key=True)
)

class Model(Base):
    __tablename__ = "model"
    model_id = Column(String, primary_key=True)
    model_name = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="model", cascade="all, delete")

class Dataset(Base):
    __tablename__ = "dataset"
    dataset_id = Column(String, primary_key=True)
    dataset_name = Column(String, nullable=False)

    tasks = relationship(
        "Task",
        secondary=task_dataset_association,
        back_populates="datasets"
    )

class Task(Base):
    __tablename__ = "task"
    task_id = Column(String, primary_key=True)
    model_id = Column(String, ForeignKey("model.model_id", ondelete="CASCADE"), nullable=False)
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
    result_id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("task.task_id", ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable=False)

    task = relationship("Task", back_populates="result")


# --- MODEL CRUD ---
def create_model(db: Session, model_name: str) -> Model:
    model = Model(model_id=str(uuid4()), model_name=model_name)
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

def get_model(db: Session, model_id: Optional[str] = None) -> list[Model]:
    if model_id:
        return db.query(Model).filter(Model.model_id == model_id)
    
    return db.query(Model).all()

def update_model(db: Session, model_id: str, new_name: str) -> Model:
    model = get_model(db, model_id)
    if model:
        model.model_name = new_name
        db.commit()
        db.refresh(model)
    return model

def delete_model(db: Session, model_id: str) -> bool:
    model = get_model(db, model_id)
    if model:
        db.delete(model)
        db.commit()
        return True
    return False

# --- DATASET CRUD ---
def create_dataset(db: Session, dataset_name: str) -> Dataset:
    dataset = Dataset(dataset_id=str(uuid4()), dataset_name=dataset_name)
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset

def get_dataset(db: Session, dataset_id: Optional[str] = None) -> list[Dataset]:
    if dataset_id:
        return db.query(Dataset).filter(Dataset.dataset_id == dataset_id)
    
    return db.query(Dataset).all()

def update_dataset(db: Session, dataset_id: str, new_name: str) -> Dataset:
    dataset = get_dataset(db, dataset_id)
    if dataset:
        dataset.dataset_name = new_name
        db.commit()
        db.refresh(dataset)
    return dataset

def delete_dataset(db: Session, dataset_id: str) -> bool:
    dataset = get_dataset(db, dataset_id)
    if dataset:
        db.delete(dataset)
        db.commit()
        return True
    return False

# --- TASK CRUD ---
def create_task(db: Session, model_id: str, dataset_ids: list[str], status: TaskStatus) -> Task:
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


def get_task(db: Session, task_id: Optional[str] = None) -> list[Task]:
    query = db.query(Task).options(
        joinedload(Task.model),
        joinedload(Task.datasets)
    )
    if task_id:
        return query.filter(Task.task_id == task_id)

    return query.all()

def update_task_status(db: Session, task_id: str, new_status: TaskStatus) -> Task:
    task = get_task(db, task_id)
    if task:
        task.status = new_status
        db.commit()
        db.refresh(task)
    return task

def delete_task(db: Session, task_id: str) -> bool:
    task = get_task(db, task_id)
    if task:
        db.delete(task)
        db.commit()
        return True
    return False

# --- RESULT CRUD ---
def create_result(db: Session, task_id: str, value: float) -> Result:
    result = Result(result_id=str(uuid4()), task_id=task_id, value=value)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

def get_result(db: Session, result_id: Optional[str] = None) -> list[Result]:
    if result_id:
        return db.query(Result).options(joinedload(Task.model)).filter(Result.result_id == result_id)

    return db.query(Result).all()

def update_result_value(db: Session, result_id: str, new_value: float) -> Result:
    result = get_result(db, result_id)
    if result:
        result.value = new_value
        db.commit()
        db.refresh(result)
    return result

def delete_result(db: Session, result_id: str) -> bool:
    result = get_result(db, result_id)
    if result:
        db.delete(result)
        db.commit()
        return True
    return False

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    # Base.metadata.create_all(engine)

    # Optional: Create a session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    Base.metadata.create_all(engine)

    # # Create model
    # m = create_model(session, "model_b")
    # print("Created Model:", m.model_id, m.model_name)

    # # # Create datasets
    # d1 = create_dataset(session, "Dataset C")
    # d2 = create_dataset(session, "Dataset D")

    # # # Create task
    # t = create_task(session, m.model_id, [d1.dataset_id, d2.dataset_id], TaskStatus.QUEUED)
    # print("Created Task:", t.task_id, t.status)

    # # Create result
    # r = create_result(session, t.task_id, 95.5)
    # print("Created Result:", r.result_id, r.value)

    tasks = get_task(session, task_id='3d8a6793-2aad-477d-ad8c-0b7a0a7eade7')
    # tasks = get_task(session)
    for task in tasks:
        print('task', task.task_id, task.status, task.model.model_name)

    models = get_model(session)
    for model in models:
        print('model', model.model_id, model.model_name)

    results = get_result(session)
    for result in results:
        print('result', result.result_id, result.value, result.task.task_id)