import io
import sys
from textwrap import dedent
from typing import Dict, Optional
import altair as alt
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

    def run_python_code(self, code, data: pd.DataFrame) -> str:
        """This function runs Python code in the current environment.  This function only has access to the altair and vega_datasets libraries.
        If successful, returns the output of the code.
        If failed, returns an error message which will include ERROR: at the start.

        Returns the value of `variable_to_return` if successful, otherwise returns an error message.

        :param code: The code to run.
        :return: value of `variable_to_return` if successful, otherwise returns an error message.
        """
        try:
            result = {}
            safe_globals = {"alt": alt, "pd": pd}
            safe_locals = {"data": data, "result": result}
            exec(code, safe_globals, safe_locals)

            output = safe_locals.get('result', None)

            return output or "No result"
        except Exception as e:
            return f"ERROR: {str(e)}"
        
if __name__ == "__main__":
    tool = PythonTools()
    code = dedent("""
        # import altair as alt
        # from vega_datasets import data

        source = data

        points = alt.Chart(source).mark_point(
            filled=True,
            color='black'
        ).encode(
            x=alt.X('mean(yield)').title('Barley Yield'),
            y=alt.Y('variety').sort(
                field='yield',
                op='mean',
                order='descending'
            )
        ).properties(
            width=400,
            height=250
        )

        error_bars = points.mark_rule().encode(
            x='ci0(yield)',
            x2='ci1(yield)',
        )

        chart = points + error_bars
        html_string = chart.to_html()
        result = html_string
    """)

    # safe_globals = {"alt": alt, "pd": pd}
    # safe_locals = {"data": data.barley()}
    # exec(code, safe_globals, safe_locals)
    # print(safe_locals.get('result'))

    result = tool.run_python_code(code, data.barley())
    print(result)
