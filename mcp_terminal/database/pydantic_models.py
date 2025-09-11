from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PyResponse[T](BaseModel):
    """A generic response model wrapping the actual data.
    Attributes:
        status (bool): Indicates if the operation was successful.
        message (Optional[str]): An optional message providing additional information.
        data (Optional[T]): The actual data returned by the operation, if any.
    """
    status: bool = Field(..., description="Indicates if the operation was successful.")
    message: Optional[str] = Field(None, description="An optional message providing additional information if status = false.")
    data: Optional[T]= Field(None, description="The actual data returned by the operation, if any.")

class PyModel(BaseModel):
    """A Pydantic model representing a machine learning model in the database.
    Attributes:
        model_id (int): The unique identifier for the model.
        model_name (str): The name of the model.
    """
    model_id: int = Field(..., description="The unique identifier for the model.")
    model_name: str = Field(..., description="The name of the model.")

    model_config = ConfigDict(from_attributes=True)