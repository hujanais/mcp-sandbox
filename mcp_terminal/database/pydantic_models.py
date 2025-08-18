from pydantic import BaseModel

from models import Model

class PyModel(BaseModel):
    def __init__(self):
        self.model_id: str
        self.model_name: str

    def from_model(self, model: Model):
        self.model_id = model.model_id
        self.model_name = model.model_name
        