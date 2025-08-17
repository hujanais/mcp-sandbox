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
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("task.task_id", ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable=False)
    category = Column(String, nullable=True)

    task = relationship("Task", back_populates="result")