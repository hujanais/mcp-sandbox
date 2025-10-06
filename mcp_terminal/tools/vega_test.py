import altair as alt
import pandas as pd                                                                                                                                                                     
import numpy as np                                                                                                                                                                      
from vega_datasets import data

if __name__ == "__main__":                                                                                                                                                                  
    # df = data.barley()
    # shuffled_df = df.sample(frac=1, random_state=42)

    # # Reset the index to maintain a clean, sequential index after shuffling
    # shuffled_df = shuffled_df.reset_index(drop=True)

    # print(shuffled_df.head(10))

    df = pd.DataFrame({                                                                                                                                                                                       
        'Attribute': ['OVR', 'PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY'],                                                                                                                                       
        'Alexander Isak': [85, 85, 84, 73, 86, 39, 74],                                                                                                                                                       
        'Erling Haaland': [91, 88, 92, 70, 81, 45, 88]                                                                                                                                                        
    })                                                                                                                                                                                                        
                                                                                                                                                                                                            
    # Create a single horizontal grouped bar chart                                                                                                                                                                   
    result = alt.Chart(df).mark_bar().encode(                                                                                                                                                                 
        x=alt.X('value:Q', title='Rating'),                                                                                                                                                                   
        y=alt.Y('Attribute:N', title='Attributes'),                                                                                                                                                           
        color=alt.Color('Player:N', title='Player', 
                    scale=alt.Scale(domain=['Alexander Isak', 'Erling Haaland'], 
                                    range=['steelblue', 'orange']))                                                                                                        
    ).transform_fold(                                                                                                                                                                                         
        ['Alexander Isak', 'Erling Haaland'],                                                                                                                                                                 
        as_=['Player', 'value']                                                                                                                                                                               
    ).properties(
        width=600,
        height=300,
        title="Player Attribute Comparison"
    ).save('chart.html')