import os
import sys
from textwrap import dedent
import pandas as pd
from typing import Any, Dict, List
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.huggingface import HuggingFace
from agno.tools import Toolkit
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.python_tool import PythonTools
from llm_models.llm_models import hf_model, openai_model

load_dotenv()

class AltairVegaTools(Toolkit):
    """AltairVegaTools that will be able to run Altair and Vega python code to the chart html."""
    def __init__(self, **kwargs):
        tools: List[Any] = [self.run_python_code]
        super().__init__(name="Altair_Vega_Tool", tools=tools, **kwargs)

    def run_python_code(code: str, jsonData: str) -> str:
        """
        Executes the provided Python code in a restricted environment.

        If successful, returns the output of the code.
        If failed, returns an error message which will include ERROR: at the start.

        :param code: The code to run.
        :param jsonData: json string of the object to visualize
        :return: the result from the python code if successful, otherwise returns an error message.
        """
        result = PythonTools().run_python_code(code, jsonData)
        return result
  
systemPrompt = """
  You are a helpful coding assistant that is an expert in using the Vega-Altair python charting package used to build clear, and informative professional  charts to best describe the data.

  jsonData will be the input from the user containing the chart data in JSON format. 

  You shall return only the code without any explanations. The format to return is very specific and needs to be in the following boilerplate template:

  ```python
  import json
  import altair as alt
  import pandas as pd
  import math

  # Input Dataframe: this data is always defined outside this function
  df = pd.DataFrame(json.loads(jsonData))

  # chart = <The implementation of the chart code>

  # Always assign the final chart html output to the variable 'result'
  result = chart.to_html()
  ```

"""
# agent = Agent(
#     model=openai_model,
#     system_message=systemPrompt,
#     reasoning=True)

# agent.print_response("Tell me a joke about a sunny day.", stream=True)

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    system_message=systemPrompt,
    reasoning=True)

agent.print_response(f"""Visualize the 2 players on a single horizontal groups bar chart.       
   [{"Name: Alexander Isak, OVR: 85, PAC: 85, SHO: 84, PAS: 73, DRI: 86, DEF: 39, PHY: 74"}, {"Name: Erling Haaland, OVR: 91, PAC: 88, SHO: 92, PAS: 70, DRI: 81, DEF: 45, PHY: 88"}]
""", stream=True)