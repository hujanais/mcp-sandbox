import json
from typing import List
import altair as alt
import pandas as pd


def convertJsonToDataFrame(jsonData: List[dict]):
    items = []
    for item in jsonData:
        # Extract the string from the dictionary
        player_str = list(item.values())[0]

        # Split by commas and process each attribute
        attributes = player_str.split(", ")
        player_dict = {}

        for attr in attributes:
            key, value = attr.split(": ", 1)
            # Convert numeric values to integers
            if key != "Name":
                player_dict[key] = int(value)
            else:
                player_dict[key] = value

        items.append(player_dict)

    df = pd.DataFrame(items)
    return df


if __name__ == "__main__":
    # Input data for the players
    jsonData = '[{"Name": "Erling Haaland", "PAC": 88, "SHO": 92, "PAS": 70, "DRI": 79}, {"Name": "Mohamed Salah", "PAC": 89, "SHO": 87, "PAS": 82, "DRI": 88}]'
    df = pd.DataFrame(json.loads(jsonData))

    # Melt the dataframe for long format
    df_melted = df.melt(id_vars=["Name"], var_name="Statistic", value_name="Value")

    # Create a comparison chart
    chart = (
        alt.Chart(df_melted)
        .mark_bar()
        .encode(x=alt.X("Statistic:N", title="Key Statistics"), y=alt.Y("Value:Q", title="Rating"), color="Name:N")
        .properties(title="Comparison of Key Statistics: Erling Haaland vs Mohamed Salah")
    )

    # Assign to result for output
    chart.save("chart.html")
