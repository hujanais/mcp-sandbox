import altair as alt
import pandas as pd                                                                                                                                                                     
import numpy as np                                                                                                                                                                      

if __name__ == "__main__":                                                                                                                                                                                            
    # Input Dataframe: this data is always defined outside this function                                                                                                                    
    df = pd.DataFrame({                                                                                                                                                                     
        'Name': ['Alexander Isak', 'Erling Haaland'],                                                                                                                                       
        'OVR': [85, 91],                                                                                                                                                                    
        'PAC': [85, 88],                                                                                                                                                                    
        'SHO': [84, 92],                                                                                                                                                                    
        'PAS': [73, 70],                                                                                                                                                                    
        'DRI': [86, 81],                                                                                                                                                                    
        'DEF': [39, 45],                                                                                                                                                                    
        'PHY': [74, 88]                                                                                                                                                                     
    })                                                                                                                                                                                      
                                                                                                                                                                                            
    # Prepare data for radar chart                                                                                                                                                          
    categories = list(df.columns[1:])                                                                                                                                                       
    num_vars = len(categories)                                                                                                                                                              
                                                                                                                                                                                            
    # Create a radar chart                                                                                                                                                                  
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()                                                                                                                   
                                                                                                                                                                                            
    # The plot is circular, needs to be 'closed'                                                                                                                                            
    values = df.loc[0, categories].tolist()                                                                                                                                                 
    values += values[:1]                                                                                                                                                                    
                                                                                                                                                                                            
    values_h = df.loc[1, categories].tolist()                                                                                                                                               
    values_h += values_h[:1]                                                                                                                                                                
                                                                                                                                                                                            
    data = pd.DataFrame({                                                                                                                                                                   
        'angle': angles,                                                                                                                                                                    
        'Isak': values,                                                                                                                                                                     
        'Haaland': values_h                                                                                                                                                                 
    })                                                                                                                                                                                      
                                                                                                                                                                                            
    # Radar chart for two players                                                                                                                                                           
    base = alt.Chart(data).encode(                                                                                                                                                          
        theta='angle:Q',                                                                                                                                                                    
        radius=alt.Radius('Isak:Q', scale=alt.Scale(domain=[0, 100])),                                                                                                                      
    ).mark_area(fill='blue', opacity=0.5).properties(width=400, height=400)                                                                                                                 
                                                                                                                                                                                            
    layer_h = alt.Chart(data).encode(                                                                                                                                                       
        theta='angle:Q',                                                                                                                                                                    
        radius=alt.Radius('Haaland:Q', scale=alt.Scale(domain=[0, 100])),                                                                                                                   
    ).mark_area(fill='orange', opacity=0.5)                                                                                                                                                 
                                                                                                                                                                                            
    result = alt.layer(base, layer_h).properties(title='Player Comparison: Isak vs Haaland').to_html()