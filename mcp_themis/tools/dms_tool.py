from typing import Any, List
from agno.tools import Toolkit

from models.model_tools import get_model

class DMSTool(Toolkit):
    """DMSTool."""
    def __init__(self, **kwargs):
        tools: List[Any] = [get_model]
        super().__init__(name="DMSTools", tools=tools, **kwargs)