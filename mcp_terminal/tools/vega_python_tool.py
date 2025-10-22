import json
from typing import Any, List
import pandas as pd
import altair as alt
import math
from agno.tools import Toolkit


class AltairVegaTools(Toolkit):
    """AltairVegaTools that will be able to run Altair and Vega python code to the chart html."""

    def __init__(self, **kwargs):
        tools: List[Any] = [self.run_python_code]
        super().__init__(name="Altair_Vega_Python_Tool", tools=tools, **kwargs)

    def run_python_code(code: str, jsonData: str) -> str:
        """
        Executes the provided Python code in a restricted environment.

        If successful, returns the output of the code.
        If failed, returns an error message which will include ERROR: at the start.

        :param code: The code to run.
        :param jsonData: json string of the object to visualize
        :return: the result from the python code if successful, otherwise returns an error message.
        """
        try:
            result = {}
            df = pd.DataFrame(json.loads(jsonData))
            safe_globals = {"alt": alt, "pd": pd, "math": math, "json": json}
            safe_locals = {"df": df, "result": result}
            exec(code, safe_globals, safe_locals)

            output = safe_locals.get("result", None)

            return output or "No result"
        except Exception as e:
            return f"ERROR: {str(e)}"
