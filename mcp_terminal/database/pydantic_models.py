from pydantic import BaseModel, Field

class PyModel(BaseModel):
    """A Pydantic model representing a machine learning model in the database.
    Attributes:
        model_id (int): The unique identifier for the model.
        model_name (str): The name of the model.
    """
    model_id: int = Field(..., description="The unique identifier for the model.")
    model_name: str = Field(..., description="The name of the model.")

    model_config = {"from_attributes": True}

class PyDataset(BaseModel):
    """A Pydantic model representing a dataset in the database.
    Attributes:
        dataset_id (int): The unique identifier for the dataset.
        dataset_name (str): The name of the dataset.
    """
    dataset_id: int = Field(..., description="The unique identifier for the dataset.")
    dataset_name: str = Field(..., description="The name of the dataset.")

    model_config = {"from_attributes": True}

class PyTask(BaseModel):
    """A Pydantic model representing a task in the database.
    Attributes:
        task_id (int): The unique identifier for the task.
        task_name (str): The name of the task.
        task_status (str): The status of the task.
    """
    task_id: int = Field(..., description="The unique identifier for the task.")
    status: str = Field(..., description="The status of the task.")

    model_id: int = Field(..., description="The unique identifier for the task.")
    datasets: list[PyDataset] = Field(..., description="The datasets associated with the task.")

    model_config = {"from_attributes": True}