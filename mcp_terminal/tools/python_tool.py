import io
import sys
from textwrap import dedent
from typing import Dict, Optional
import altair as alt
from vega_datasets import data
import pandas as pd

class PythonTools:
    def __init__(self):
        pass

    def run_python_code(self, code, data: pd.DataFrame) -> str:
        """This function runs Python code in the current environment.  This function only has access to the altair and vega_datasets libraries.
        If successful, returns the output of the code.
        If failed, returns an error message which will include ERROR: at the start.

        Returns the value of `variable_to_return` if successful, otherwise returns an error message.

        :param code: The code to run.
        :return: value of `variable_to_return` if successful, otherwise returns an error message.
        """
        # Redirect stdout to capture print outputs
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            result = {}
            safe_globals = {"alt": alt, "pd": pd}
            safe_locals = {"data": data, "result": result}
            output = exec(code, safe_globals, safe_locals)

            # Retrieve the printed output
            # output = new_stdout.getvalue()

            # Reset stdout
            # sys.stdout = old_stdout

            return output or "No output captured"
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
        chart.save('chart.html')
        return "chart saved to chart.html"
    """)

    # globals = {}
    # globals["alt"] = alt
    # globals["data"] = data
    output = tool.run_python_code(code="""return "hello" """, data=data.barley())
    print(output)