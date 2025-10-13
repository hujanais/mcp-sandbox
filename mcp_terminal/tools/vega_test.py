import json
from typing import List
import altair as alt
import pandas as pd                                                                                                                                                                     
import numpy as np                                                                                                                                                                      
from vega_datasets import data

def convertJsonToDataFrame(jsonData: List[dict]):
    items = []
    for item in jsonData:
        # Extract the string from the dictionary
        player_str = list(item.values())[0]
        
        # Split by commas and process each attribute
        attributes = player_str.split(', ')
        player_dict = {}
        
        for attr in attributes:
            key, value = attr.split(': ', 1)
            # Convert numeric values to integers
            if key != 'Name':
                player_dict[key] = int(value)
            else:
                player_dict[key] = value
        
        items.append(player_dict)
    
    df = pd.DataFrame(items)
    return df

if __name__ == "__main__":                                                                                                                                                                  
    # df = data.barley()
    # shuffled_df = df.sample(frac=1, random_state=42)

    # # # Reset the index to maintain a clean, sequential index after shuffling
    # shuffled_df = shuffled_df.reset_index(drop=True)

    # print(shuffled_df.head(10))

    df = pd.DataFrame({
        'yield': [29.86667, 32.00000, 32.96667, 58.80000, 43.76667, 22.13333, 38.50000, 29.13333, 24.93334, 31.36667],
        'variety': ['Peatland', 'Peatland', 'Manchuria', 'Wisconsin No. 38', 'Trebi', 'Manchuria', 'Svansota', 'Glabron', 'No. 462', 'Peatland'],
        'year': [1931, 1931, 1931, 1931, 1931, 1932, 1932, 1931, 1931, 1932],
        'site': ['Morris', 'Duluth', 'Grand Rapids', 'Waseca', 'Morris', 'Grand Rapids', 'Waseca', 'Grand Rapids', 'Grand Rapids', 'Duluth']
    })


    # Input Dataframe: this data is always defined outside this function
    jsonData = '[{"Name": "Alexander Isak", "OVR": 85, "PAC": 85, "SHO": 84, "PAS": 73, "DRI": 86, "DEF": 39, "PHY": 74}, {"Name": "Erling Haaland", "OVR": 91, "PAC": 88, "SHO": 92, "PAS": 70, "DRI": 81, "DEF": 45, "PHY": 88}]'
    df = pd.DataFrame(json.loads(jsonData))

    # chart = Altair grouped bar chart
    chart = alt.Chart(df).transform_fold(
        ['OVR', 'PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY'],
        as_=['Attribute', 'Value']
    ).mark_bar().encode(
        x=alt.X('Attribute:N', title='Attributes'),
        y=alt.Y('Value:Q', title='Scores', scale=alt.Scale(domain=[0, 100])),
        color='Name:N'
    ).properties(
        width=200,
        height=300,
        title='Player Attributes Comparison'
    ).facet(
        column='Name:N'
    ).configure_facet(
        spacing=10
    )

    # Always assign the final chart html output to the variable 'result'
    result = chart.to_html()
    chart.save('chart.html')

    # p1 = [{"Name":"Erling Haaland","OVR":91,"PAC":88,"SHO":92,"PAS":70,"DRI":81,"DEF":45,"PHY":88}]
    # p2 = [{"Name":"Alexander Isak","OVR":85,"PAC":85,"SHO":84,"PAS":73,"DRI":86,"DEF":39,"PHY":74}]

    # items = p1+p2

    # source = pd.DataFrame(items)

    # alt.Chart(source).mark_bar().encode(
    #     x='sum(yield):Q',
    #     y='Name:O',
    #     color='Name:N',
    #     row='site:N'
    # ).save('chart.html')