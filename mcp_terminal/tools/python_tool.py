from ast import List
import io
import json
import sys
from textwrap import dedent
from typing import Dict
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

    def run_python_code(self, code, jsonData: str) -> str:
        """This function runs Python code in the current environment.  This function only has access to the altair and vega_datasets libraries.
        If successful, returns the output of the code.
        If failed, returns an error message which will include ERROR: at the start.

        Returns the value of `result` if successful, otherwise returns an error message.

        :param code: The code to run.
        :param jsonData: The JSON data to be used in the code to run.
        :return: value of `result` if successful, otherwise returns an error message.
        """
        try:
            result = {}
            df = pd.DataFrame(json.loads(jsonData))
            safe_globals = {"alt": alt, "pd": pd, "math": math, "json": json}
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
 import numpy as np                                                                                                                                                                                   
                                                                                                                                                                                                      
 # Input Dataframe                                                                                                                                                                                    
 data = {                                                                                                                                                                                             
     'Name': ['Alexander Isak', 'Erling Haaland'],                                                                                                                                                    
     'OVR': [85, 91],                                                                                                                                                                                 
     'PAC': [85, 88],                                                                                                                                                                                 
     'SHO': [84, 92],                                                                                                                                                                                 
     'PAS': [73, 70],                                                                                                                                                                                 
     'DRI': [86, 81],                                                                                                                                                                                 
     'DEF': [39, 45],                                                                                                                                                                                 
     'PHY': [74, 88]                                                                                                                                                                                  
 }                                                                                                                                                                                                    
 df = pd.DataFrame(data)                                                                                                                                                                              
                                                                                                                                                                                                      
 # Prepare the radar chart                                                                                                                                                                            
 categories = list(df.columns[1:])                                                                                                                                                                    
 num_vars = len(categories)                                                                                                                                                                           
                                                                                                                                                                                                      
 # Create the angle for each axis                                                                                                                                                                     
 angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()                                                                                                                                
                                                                                                                                                                                                      
 # The plot is made in a circular, complete path                                                                                                                                                      
 df = df.append(df.iloc[0])  # Repeat the first row as a circular path                                                                                                                                
 angles += angles[:1]  # Repeat the first angle                                                                                                                                                       
                                                                                                                                                                                                      
 # Set up the base chart                                                                                                                                                                              
 base = alt.Chart(pd.DataFrame({'angles': angles, 'Name': [''] * len(angles), 'value': [0] * len(angles)})).encode(                                                                                   
     theta=alt.Theta('angles:Q'),                                                                                                                                                                     
     radius=alt.Radius('value:Q')                                                                                                                                                                     
 )                                                                                                                                                                                                    
                                                                                                                                                                                                      
 # Create a layer for each player                                                                                                                                                                     
 layers = []                                                                                                                                                                                          
 for i in range(len(df)):                                                                                                                                                                             
     layers.append(                                                                                                                                                                                   
         base.transform_calculate(value=f'datum.{categories[0]}').transform_filter(alt.datum.Name == df.iloc["Name"]).mark_line(interpolate='monotone').encode(                                       
             radius=alt.Radius('value:Q', scale=alt.Scale(domain=[0, df.max().max()])),                                                                                                               
             stroke=alt.value('red' if i == 0 else 'blue'),                                                                                                                                           
             tooltip= +                                                                                                                                                                               
         )                                                                                                                                                                                            
     )                                                                                                                                                                                                
                                                                                                                                                                                                      
 # Combine layers                                                                                                                                                                                     
 result = alt.layer(*layers).properties(                                                                                                                                                              
     title='Player Attributes Radar Chart',                                                                                                                                                           
     width=400,                                                                                                                                                                                       
     height=400                                                                                                                                                                                       
 ).save('chart.json')                                             
    """)

    # safe_globals = {"alt": alt, "pd": pd}
    # safe_locals = {"data": data.barley()}
    # exec(code, safe_globals, safe_locals)
    # print(safe_locals.get('result'))

    jsonStr = [{"Name: Alexander Isak, OVR: 85, PAC: 85, SHO: 84, PAS: 73, DRI: 86, DEF: 39, PHY: 74"}, {"Name: Erling Haaland, OVR: 91, PAC: 88, SHO: 92, PAS: 70, DRI: 81, DEF: 45, PHY: 88"}]
    result = tool.run_python_code(code, jsonStr)
    print(result)
