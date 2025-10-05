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

        source = pd.DataFrame({"year": [2000, 2001, 2002, 2003], "close": [1223, 1243, 1000, 2432]})                                                                                                                         

        result = alt.Chart(source).mark_line().encode(                                                                                                                                                                       
            x='year:O',                                                                                                                                                                                                      
            y='close:Q'                                                                                                                                                                                                      
        ).to_html()                                   
    """)

    # safe_globals = {"alt": alt, "pd": pd}
    # safe_locals = {"data": data.barley()}
    # exec(code, safe_globals, safe_locals)
    # print(safe_locals.get('result'))

    df = pd.DataFrame({"year": [2000, 2001, 2002, 2003], "close": [1223, 1243, 1000, 2432]})
    result = tool.run_python_code(code, df)
    print(result)
