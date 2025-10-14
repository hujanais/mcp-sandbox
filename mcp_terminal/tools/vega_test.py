import json
from textwrap import dedent
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

    # df = pd.DataFrame({
    #     'yield': [29.86667, 32.00000, 32.96667, 58.80000, 43.76667, 22.13333, 38.50000, 29.13333, 24.93334, 31.36667],
    #     'variety': ['Peatland', 'Peatland', 'Manchuria', 'Wisconsin No. 38', 'Trebi', 'Manchuria', 'Svansota', 'Glabron', 'No. 462', 'Peatland'],
    #     'year': [1931, 1931, 1931, 1931, 1931, 1932, 1932, 1931, 1931, 1932],
    #     'site': ['Morris', 'Duluth', 'Grand Rapids', 'Waseca', 'Morris', 'Grand Rapids', 'Waseca', 'Grand Rapids', 'Grand Rapids', 'Duluth']
    # })


    # Input Dataframe: this data is always defined outside this function
    # The input data is of type json string.                                                                                                                        
    # jsonData = '{"Rank":25,"Name":"Lionel Messi","OVR":88,"PAC":79,"SHO":85,"PAS":87,"DRI":92,"DEF":33,"PHY":64,"Acceleration":86,"Sprint Speed":73,"Positioning":89,"Finishing":85,"Shot Power":83,"Long Shots":87,"Volleys":86,"Penalties":75,"Vision":90,"Crossing":80,"Free Kick Accuracy":92,"Short Passing":87,"Long Passing":86,"Curve":93,"Dribbling":93,"Agility":90,"Balance":95,"Reactions":85,"Ball Control":93,"Composure":94,"Interceptions":40,"Heading Accuracy":60,"Def Awareness":20,"Standing Tackle":35,"Sliding Tackle":24,"Jumping":71,"Stamina":70,"Strength":68,"Aggression":44,"Position":"RW","Weak foot":4,"Skill moves":4,"Preferred foot":"Left","Alternative positions":"ST, CAM, RM","Age":37,"Nation":"Argentina","League":"MLS","Team":"Inter Miami CF","play style":"Technical+, Dead Ball, Finesse Shot, Incisive Pass, Quick Step, Tiki Taka, Trivela","GK Diving":null,"GK Handling":null,"GK Kicking":null,"GK Positioning":null,"GK Reflexes":null}'
    jsonData = """{"Rank":25,"Name":"Lionel Messi","OVR":88,"PAC":79,"SHO":85,"PAS":87,"DRI":92,"DEF":33,"PHY":64,"Acceleration":86,"Sprint
        Speed":73,"Positioning":89,"Finishing":85,"Shot Power":83,"Long Shots":87,"Volleys":86,"Penalties":75,"Vision":90,"Crossing":80,"Free Kick Accuracy":92,"Short
        Passing":87,"Long Passing":86,"Curve":93,"Dribbling":93,"Agility":90,"Balance":95,"Reactions":85,"Ball Control":93,"Composure":94,"Interceptions":40,"Heading   
        Accuracy":60,"Def Awareness":20,"Standing Tackle":35,"Sliding Tackle":24,"Jumping":71,"Stamina":70,"Strength":68,"Aggression":44,"Position":"RW","Weak          
        foot":4,"Skill moves":4,"Preferred foot":"Left","Alternative positions":"ST, CAM, RM","Age":37,"Nation":"Argentina","League":"MLS","Team":"Inter Miami          
        CF","play style":"Technical+, Dead Ball, Finesse Shot, Incisive Pass, Quick Step, Tiki Taka, Trivela"}
    """

    # Load JSON data into a DataFrame
    df = pd.DataFrame([json.loads(jsonData)])  # Wrap json.loads in a list to create a single-row DataFrame
                                                                                                                                                                                                                                                                               
    # chart = Chart for visualizing Messi’s attributes                                                                                                              
    chart = alt.Chart(df).transform_fold(                                                                                                                           
        ['PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY', 'Acceleration', 'Sprint Speed', 'Positioning', 'Finishing',                                                      
        'Shot Power', 'Long Shots', 'Volleys', 'Penalties', 'Vision', 'Crossing', 'Free Kick Accuracy',                                                            
        'Short Passing', 'Long Passing', 'Curve', 'Dribbling', 'Agility', 'Balance', 'Reactions',                                                                  
        'Ball Control', 'Composure', 'Interceptions', 'Heading Accuracy', 'Def Awareness',                                                                         
        'Standing Tackle', 'Sliding Tackle', 'Jumping', 'Stamina', 'Strength', 'Aggression'],                                                                      
        as_=['Attribute', 'Value']                                                                                                                                  
    ).mark_bar().encode(                                                                                                                                            
        x=alt.X('Attribute:N', sort='-y'),                                                                                                                          
        y='Value:Q',                                                                                                                                                
        color='Attribute:N'                                                                                                                                         
    ).properties(                                                                                                                                                   
        title='Messi’s Attributes Overview',                                                                                                                        
        height=400,                                                                                                                                                 
        width=800                                                                                                                                                   
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