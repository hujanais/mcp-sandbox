from pydantic import BaseModel, ConfigDict

class PyModel(BaseModel):
    model_id: int
    model_name: str

    model_config = ConfigDict(from_attributes=True)