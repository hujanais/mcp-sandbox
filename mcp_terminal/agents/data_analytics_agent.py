import os
import sys
import pandas as pd
from typing import Any, List
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import Toolkit
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.python_tool import PythonTools

load_dotenv()

class AltairVegaTools(Toolkit):
    """AltairVegaTools that will be able to run Altair and Vega python code to return charts."""
    def __init__(self, **kwargs):
        tools: List[Any] = [self.run_python_code]
        super().__init__(name="Altair_Vega_Tool", tools=tools, **kwargs)

    def run_python_code(code: str, data: pd.DataFrame) -> str:
        """
        Executes the provided Python code in a restricted environment.

        If successful, returns the output of the code.
        If failed, returns an error message which will include ERROR: at the start.

        :param code: The code to run.
        :param data: The pandas DataFrame to be used in the code to run.
        :return: the result from the python code if successful, otherwise returns an error message.
        """
        result = PythonTools().run_python_code(code, data)
        return result
  
systemPrompt = """
You are an expert Vega-Altair developer that will be able to write concise code to creatively visualize Pandas dataframe input.
When answering, just return the generated response without any further explanation or text.

The variable 'df' will always contain the provided dataframe so there is no need to recreate it in code.  The data will be injected into the code in an exec function.

Here are some chart code examples.
# Simple Scatter Plot with Tooltips
```python
import altair as alt

source = df # this data is always defined outside this function

result = alt.Chart(source).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
)
```
# Polar Bar Chart
```python
import math
import altair as alt
import pandas as pd

source = df # this data is always defined outside this function

polar_bars = alt.Chart(source).mark_arc(stroke='white', tooltip=True).encode(
    theta=alt.Theta("hour:O"),
    radius=alt.Radius('observations').scale(type='linear'),
    radius2=alt.datum(1),
)

# Create the circular axis lines for the number of observations
axis_rings = alt.Chart(pd.DataFrame({"ring": range(2, 11, 2)})).mark_arc(stroke='lightgrey', fill=None).encode(
    theta=alt.value(2 * math.pi),
    radius=alt.Radius('ring').stack(False)
)
axis_rings_labels = axis_rings.mark_text(color='grey', radiusOffset=5, align='left').encode(
    text="ring",
    theta=alt.value(math.pi / 4)
)

# Create the straight axis lines for the time of the day
axis_lines = alt.Chart(pd.DataFrame({
    "radius": 10,
    "theta": math.pi / 2,
    'hour': ['00:00', '06:00', '12:00', '18:00']
})).mark_arc(stroke='lightgrey', fill=None).encode(
    theta=alt.Theta('theta').stack(True),
    radius=alt.Radius('radius'),
    radius2=alt.datum(1),
)
axis_lines_labels = axis_lines.mark_text(
        color='grey',
        radiusOffset=5,
        thetaOffset=-math.pi / 4,
        # These adjustments could be left out with a larger radius offset, but they make the label positioning a bit clearner
        align=alt.expr('datum.hour == "18:00" ? "right" : datum.hour == "06:00" ? "left" : "center"'),
        baseline=alt.expr('datum.hour == "00:00" ? "bottom" : datum.hour == "12:00" ? "top" : "middle"'),
    ).encode(text="hour")

result = alt.layer(
    axis_rings,
    polar_bars,
    axis_rings_labels,
    axis_lines,
    axis_lines_labels,
    title=['Observations throughout the day', '']
)

Human: Visualize the following dataset df = {"sample": [1,2,3,4,5], "temperature": [23.1, 24.2, 25.3, 26.4, 27.5]}
Thinking: The human is asking to visualize a dataset so I should use my expertise to create the python code to create a visualization.
Observe: I have created the python code to visualize the dataset with the special stipulation that the dataframe called 'df' and just needs to be referenced in the code
and assign the variable 'result'.
Action: I will now send the visualization python code to the human with no further explanation.
```
"""
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    system_message=systemPrompt,
    markdown=True,
)
agent.print_response("""Visualize the following dataframe, df = {"year": [2000, 2001, 2002, 2003], "close": [1223, 1243, 1000. 2432]}""", stream=True)