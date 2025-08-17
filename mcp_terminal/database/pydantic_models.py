from pydantic import BaseModel

class PyModel(BaseModel):
    def __init__(self, model_id: str, model_name: str):
        model_id: str
        model_name: str