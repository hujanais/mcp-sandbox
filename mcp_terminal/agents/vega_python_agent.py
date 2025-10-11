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
You are an expert Vega-Altair developer that will be able to write concise code to creatively visualize Pandas dataframe input.
When answering, just return the generated response without any further explanation or text.

The variable 'jsonData' will always contain the provided dataframe so there is no need to recreate it in code.  The data will be injected into the code in an exec function.

Here are some chart code examples.
# General expected code structure
```python
import json
import altair as alt
import pandas as pd
import math

# Input Dataframe: this data is always defined outside this function
df = pd.DataFrame(json.loads(jsonData))

# Create Altair Chart

# Always assign the final chart html output to the variable 'result'
result = <altair_chart>.to_html()
```

# Example charts
# Simple Scatter Plot with Tooltips
```python
import altair as alt

source = df # this data is always defined outside this function

result = alt.Chart(source).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).to_html()
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
).to_html()
```

# Radar Chart
```python
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "description": "A radar chart example, showing multiple dimensions in a radial layout.",
  "width": 400,
  "height": 400,
  "padding": 40,
  "autosize": {"type": "none", "contains": "padding"},

  "signals": [
    {"name": "radius", "update": "width / 2"}
  ],

  "data": [
    {
      "name": "table",
      "values": [
        {"key": "key-0", "value": 19, "category": 0},
        {"key": "key-1", "value": 22, "category": 0},
        {"key": "key-2", "value": 14, "category": 0},
        {"key": "key-3", "value": 38, "category": 0},
        {"key": "key-4", "value": 23, "category": 0},
        {"key": "key-5", "value": 5, "category": 0},
        {"key": "key-6", "value": 27, "category": 0},
        {"key": "key-0", "value": 13, "category": 1},
        {"key": "key-1", "value": 12, "category": 1},
        {"key": "key-2", "value": 42, "category": 1},
        {"key": "key-3", "value": 13, "category": 1},
        {"key": "key-4", "value": 6, "category": 1},
        {"key": "key-5", "value": 15, "category": 1},
        {"key": "key-6", "value": 8, "category": 1}
      ]
    },
    {
      "name": "keys",
      "source": "table",
      "transform": [
        {
          "type": "aggregate",
          "groupby": ["key"]
        }
      ]
    }
  ],

  "scales": [
    {
      "name": "angular",
      "type": "point",
      "range": {"signal": "[-PI, PI]"},
      "padding": 0.5,
      "domain": {"data": "table", "field": "key"}
    },
    {
      "name": "radial",
      "type": "linear",
      "range": {"signal": "[0, radius]"},
      "zero": true,
      "nice": false,
      "domain": {"data": "table", "field": "value"},
      "domainMin": 0
    },
    {
      "name": "color",
      "type": "ordinal",
      "domain": {"data": "table", "field": "category"},
      "range": {"scheme": "category10"}
    }
  ],

  "encode": {
    "enter": {
      "x": {"signal": "radius"},
      "y": {"signal": "radius"}
    }
  },

  "marks": [
    {
      "type": "group",
      "name": "categories",
      "zindex": 1,
      "from": {
        "facet": {"data": "table", "name": "facet", "groupby": ["category"]}
      },
      "marks": [
        {
          "type": "line",
          "name": "category-line",
          "from": {"data": "facet"},
          "encode": {
            "enter": {
              "interpolate": {"value": "linear-closed"},
              "x": {"signal": "scale('radial', datum.value) * cos(scale('angular', datum.key))"},
              "y": {"signal": "scale('radial', datum.value) * sin(scale('angular', datum.key))"},
              "stroke": {"scale": "color", "field": "category"},
              "strokeWidth": {"value": 1},
              "fill": {"scale": "color", "field": "category"},
              "fillOpacity": {"value": 0.1}
            }
          }
        },
        {
          "type": "text",
          "name": "value-text",
          "from": {"data": "category-line"},
          "encode": {
            "enter": {
              "x": {"signal": "datum.x"},
              "y": {"signal": "datum.y"},
              "text": {"signal": "datum.datum.value"},
              "align": {"value": "center"},
              "baseline": {"value": "middle"},
              "fill": {"value": "black"}
            }
          }
        }
      ]
    },
    {
      "type": "rule",
      "name": "radial-grid",
      "from": {"data": "keys"},
      "zindex": 0,
      "encode": {
        "enter": {
          "x": {"value": 0},
          "y": {"value": 0},
          "x2": {"signal": "radius * cos(scale('angular', datum.key))"},
          "y2": {"signal": "radius * sin(scale('angular', datum.key))"},
          "stroke": {"value": "lightgray"},
          "strokeWidth": {"value": 1}
        }
      }
    },
    {
      "type": "text",
      "name": "key-label",
      "from": {"data": "keys"},
      "zindex": 1,
      "encode": {
        "enter": {
          "x": {"signal": "(radius + 5) * cos(scale('angular', datum.key))"},
          "y": {"signal": "(radius + 5) * sin(scale('angular', datum.key))"},
          "text": {"field": "key"},
          "align": [
            {
              "test": "abs(scale('angular', datum.key)) > PI / 2",
              "value": "right"
            },
            {
              "value": "left"
            }
          ],
          "baseline": [
            {
              "test": "scale('angular', datum.key) > 0", "value": "top"
            },
            {
              "test": "scale('angular', datum.key) == 0", "value": "middle"
            },
            {
              "value": "bottom"
            }
          ],
          "fill": {"value": "black"},
          "fontWeight": {"value": "bold"}
        }
      }
    },
    {
      "type": "line",
      "name": "outer-line",
      "from": {"data": "radial-grid"},
      "encode": {
        "enter": {
          "interpolate": {"value": "linear-closed"},
          "x": {"field": "x2"},
          "y": {"field": "y2"},
          "stroke": {"value": "lightgray"},
          "strokeWidth": {"value": 1}
        }
      }
    }
  ]
}
```

# Horizontal Grouped Bar Chart
```python
import altair as alt
from vega_datasets import data
import pandas as pd

df = pd.DataFrame({
    'yield': [29.86667, 32.00000, 32.96667, 58.80000, 43.76667, 22.13333, 38.50000, 29.13333, 24.93334, 31.36667],
    'variety': ['Peatland', 'Peatland', 'Manchuria', 'Wisconsin No. 38', 'Trebi', 'Manchuria', 'Svansota', 'Glabron', 'No. 462', 'Peatland'],
    'year': [1931, 1931, 1931, 1931, 1931, 1932, 1932, 1931, 1931, 1932],
    'site': ['Morris', 'Duluth', 'Grand Rapids', 'Waseca', 'Morris', 'Grand Rapids', 'Waseca', 'Grand Rapids', 'Grand Rapids', 'Duluth']
})

alt.Chart(df).mark_bar().encode(
    x='sum(yield):Q',
    y='year:O',
    
    color='year:N',
    row='site:N'
)
```
"""
agent = Agent(
    model=openai_model,
    system_message=systemPrompt,
    reasoning=True)

agent.print_response("Tell me a joke about a sunny day.", stream=True)

# agent = Agent(
#     model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
#     system_message=systemPrompt,
#     reasoning=True)

# agent.print_response(f"""Visualize the 2 players on a single horizontal groups bar chart.       
#    [{"Name: Alexander Isak, OVR: 85, PAC: 85, SHO: 84, PAS: 73, DRI: 86, DEF: 39, PHY: 74"}, {"Name: Erling Haaland, OVR: 91, PAC: 88, SHO: 92, PAS: 70, DRI: 81, DEF: 45, PHY: 88"}]
# """, stream=True)