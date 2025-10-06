import altair as alt
import pandas as pd                                                                                                                                                                     
import numpy as np                                                                                                                                                                      

if __name__ == "__main__":                                                                                                                                                                  
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
                                                                                                                                                                                            
    # Melt the DataFrame to long format for easier plotting                                                                                                                                 
    df_melted = df.melt(id_vars='Name', var_name='Attribute', value_name='Value')                                                                                                           
                                                                                                                                                                                            
    result = alt.Chart(df_melted).mark_bar().encode(                                                                                                                                        
        x='Value:Q',                                                                                                                                                                        
        y=alt.Y('Attribute:N', sort='-x'),                                                                                                                                                  
        color='Name:N',                                                                                                                                                                     
        column='Name:N'                                                                                                                                                                     
    ).save('chart.html')