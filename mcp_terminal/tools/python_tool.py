import io
import sys
from textwrap import dedent
import altair as alt
import math
from vega_datasets import data
import pandas as pd

class PythonTools:
    def __init__(self):
        self.counter = 0
        pass

    def add_counter(self) -> int:
        """A simple function that adds 1 to a counter and returns the new value.
        
        :return: the new value of the counter.
        """
        self.counter += 1
        return self.counter

    def run_python_code(self, code, df: pd.DataFrame) -> str:
        """This function runs Python code in the current environment.  This function only has access to the altair and vega_datasets libraries.
        If successful, returns the output of the code.
        If failed, returns an error message which will include ERROR: at the start.

        Returns the value of `result` if successful, otherwise returns an error message.

        :param code: The code to run.
        :return: value of `result` if successful, otherwise returns an error message.
        """
        try:
            result = {}
            safe_globals = {"alt": alt, "pd": pd, "math": math}
            safe_locals = {"df": df, "result": result}
            exec(code, safe_globals, safe_locals)

            output = safe_locals.get('result', None)

            return output or "No result"
        except Exception as e:
            return f"ERROR: {str(e)}"
        
if __name__ == "__main__":
    tool = PythonTools()
    code = dedent("""
        import altair as alt
        import pandas as pd

        # Use the corrected DataFrame
        df = pd.DataFrame({
            'year': [2020, 2021, 2022, 2023, 2024, 2025],
            'avgValue': [1.53, 1.66, 1.75, 0.9, 2.5, 2.1]
        })

        # Create a chart with both lines and points
        chart = alt.Chart(df).mark_line().encode(
            x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('avgValue:Q', title='Average Value', scale=alt.Scale(domain=[0, 3])),
            order='year'  # Ensure proper line ordering
        )

        # Add points on top to highlight individual data points
        points = alt.Chart(df).mark_circle(size=80).encode(
            x='year:O',
            y='avgValue:Q',
            tooltip=['year', 'avgValue']
        )

        # Combine the two layers
        result = (chart + points).properties(
            title='Average Values by Year (2020-2025)',
            width=500,
            height=300
        )
                  
        result.save('chart.html')
    """)

    # safe_globals = {"alt": alt, "pd": pd}
    # safe_locals = {"data": data.barley()}
    # exec(code, safe_globals, safe_locals)
    # print(safe_locals.get('result'))

    result = tool.run_python_code(code, data.barley())
    print(result)
