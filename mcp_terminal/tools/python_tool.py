from textwrap import dedent
from typing import Dict, Optional
import altair as alt
from vega_datasets import data

class PythonTools:
    def __init__(self):
        pass

    def run_python_code(self, code, safe_globals: Optional[Dict] = None) -> str:
        return exec(code, safe_globals)

if __name__ == "__main__":
    tool = PythonTools()
    code = dedent("""
        # import altair as alt
        # from vega_datasets import data

        source = data.barley()

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
        return chart
    """)

    globals = {}
    globals["alt"] = alt
    globals["data"] = data
    tool.run_python_code(code, globals)