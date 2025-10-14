import json
from typing import Dict, Optional
import os
from typing import Any, List, Union
from fuzzywuzzy import fuzz

import pandas as pd
from pydantic import BaseModel, Field
from agno.tools import Toolkit

# https://www.kaggle.com/datasets/nyagami/ea-sports-fc-25-database-ratings-and-stats?resource=download

class Player(BaseModel):
    rank: Optional[int] = Field(None, alias="Rank", description="Player’s ranking based on overall rating (OVR) within the FC 25 group.")
    name: Optional[str] = Field(None, alias="Name", description="The full name of the player.")
    age: Optional[int] = Field(None, alias="Age", description="The player’s age.")
    nation: Optional[str] = Field(None, alias="Nation", description="The country the player represents in international competitions.")
    league: Optional[str] = Field(None, alias="League", description="The football league in which the player currently plays.")
    team: Optional[str] = Field(None, alias="Team", description="The club team the player is part of.")
    play_style: Optional[str] = Field(None, alias="play style", description="Specific gameplay traits or tendencies that define the player’s behavior and skillset on the field.")
    
    # Player Attributes
    overall_rating: Optional[int] = Field(None, alias="OVR", description="Overall rating of the player.")
    pace: Optional[int] = Field(None, alias="PAC", description="The player's speed and ability to outrun opponents.")
    shooting: Optional[int] = Field(None, alias="SHO", description="The player’s ability to shoot accurately.")
    passing: Optional[int] = Field(None, alias="PAS", description="The player’s passing ability.")
    dribbling: Optional[int] = Field(None, alias="DRI", description="The player’s ball control and ability to maneuver.")
    defending: Optional[int] = Field(None, alias="DEF", description="The player's defensive capabilities.")
    physical: Optional[int] = Field(None, alias="PHY", description="The player's physical strength and endurance.")
    
    # Extras
    acceleration: Optional[int] = Field(None, alias="Acceleration", description="The player’s ability to reach maximum speed quickly.")
    sprint_speed: Optional[int] = Field(None, alias="Sprint Speed", description="The top speed the player can achieve when sprinting.")
    positioning: Optional[int] = Field(None, alias="Positioning", description="The player's awareness and positioning in attack.")
    finishing: Optional[int] = Field(None, alias="Finishing", description="The player’s ability to convert scoring chances into goals.")
    shot_power: Optional[int] = Field(None, alias="Shot Power", description="The strength of the player’s shots on goal.")
    long_shots: Optional[int] = Field(None, alias="Long Shots", description="The accuracy and power of shots taken from outside the penalty area.")
    volleys: Optional[int] = Field(None, alias="Volleys", description="The player’s ability to strike the ball cleanly from mid-air.")
    penalties: Optional[int] = Field(None, alias="Penalties", description="The player's skill at taking penalty kicks.")
    
    vision: Optional[int] = Field(None, alias="Vision", description="The player's ability to make accurate passes and see plays develop.")
    crossing: Optional[int] = Field(None, alias="Crossing", description="The ability to deliver accurate crosses from wide areas.")
    free_kick_accuracy: Optional[int] = Field(None, alias="Free Kick Accuracy", description="The player’s precision when taking free kicks.")
    short_passing: Optional[int] = Field(None, alias="Short Passing", description="The accuracy and skill in making short-distance passes.")
    long_passing: Optional[int] = Field(None, alias="Long Passing", description="The ability to deliver accurate long-range passes.")
    curve: Optional[int] = Field(None, alias="Curve", description="The player’s ability to bend the ball during passes or shots.")
    
    # Dribbling and Agility
    dribbling: Optional[int] = Field(None, alias="Dribbling", description="The player’s ball control and ability to maneuver in tight spaces.")
    agility: Optional[int] = Field(None, alias="Agility", description="How quickly and smoothly the player can change direction.")
    balance: Optional[int] = Field(None, alias="Balance", description="The player’s stability and ability to stay on their feet under pressure.")
    reactions: Optional[int] = Field(None, alias="Reactions", description="The player’s responsiveness to unpredictable events during the game.")
    ball_control: Optional[int] = Field(None, alias="Ball Control", description="How well the player controls the ball while moving.")
    
    # Mentality and Defense
    composure: Optional[int] = Field(None, alias="Composure", description="The player’s calmness under pressure.")
    interceptions: Optional[int] = Field(None, alias="Interceptions", description="The player’s ability to read and intercept passes.")
    heading_accuracy: Optional[int] = Field(None, alias="Heading Accuracy", description="The player's precision when attempting to head the ball.")
    defensive_awareness: Optional[int] = Field(None, alias="Def Awareness", description="The player’s positioning and ability to anticipate defensive situations.")
    standing_tackle: Optional[int] = Field(None, alias="Standing Tackle", description="The player’s ability to win the ball with a standing tackle.")
    sliding_tackle: Optional[int] = Field(None, alias="Sliding Tackle", description="The skill and accuracy of the player’s sliding tackles.")
    
    # Physical Attributes
    jumping: Optional[int] = Field(None, alias="Jumping", description="The player’s ability to jump high during headers or challenges.")
    stamina: Optional[int] = Field(None, alias="Stamina", description="The player’s endurance and ability to perform at a high level throughout the match.")
    strength: Optional[int] = Field(None, alias="Strength", description="The player’s physical power and ability to win physical challenges.")
    aggression: Optional[int] = Field(None, alias="Aggression", description="The player’s determination and intensity in winning challenges and duels.")
    
    # Technical Skills
    weak_foot: Optional[int] = Field(None, alias="Weak foot", description="The player’s proficiency with their non-dominant foot (rated from 1 to 5 stars).")
    skill_moves: Optional[int] = Field(None, alias="Skill moves", description="The player’s ability to perform advanced dribbling moves (rated from 1 to 5 stars).")
    preferred_foot: Optional[str] = Field(None, alias="Preferred foot", description="Indicates whether the player prefers using their left or right foot.")
    
    # Goalkeeping Attributes (if applicable)
    gk_diving: Optional[int] = Field(None, alias="GK Diving", description="The goalkeeper’s ability to dive and make saves.")
    gk_handling: Optional[int] = Field(None, alias="GK Handling", description="The goalkeeper’s skill in catching or holding onto the ball.")
    gk_kicking: Optional[int] = Field(None, alias="GK Kicking", description="The accuracy and power of the goalkeeper’s kicks when distributing the ball.")
    gk_positioning: Optional[int] = Field(None, alias="GK Positioning", description="The goalkeeper’s ability to position themselves effectively during defensive situations.")
    gk_reflexes: Optional[int] = Field(None, alias="GK Reflexes", description="The goalkeeper’s quickness in reacting to shots.")


class PlayerDatabaseTool(Toolkit):
    """PlayerDatabaseTool that retrieves player information."""
    
    def __init__(self, **kwargs):
        tools: List[Any] = [self.get_player_rating]
        self.dfs = pd.read_csv("./data/all_players.csv")
        self.dfs = self.dfs.iloc[:, 2:]  # drop the first two columns
        self.dfs = self.dfs.drop(columns=['url', 'Height', "Weight"])
        super().__init__(name="PlayerDatabaseTool", tools=tools, **kwargs)

    def get_player_rating(self, name: str) -> str | None:
        """Retrieves player attributes based on the player name.

        :param name: The name of the player.
        :return: json representation of the player attributes or None if not found.
        """
        # Use str.lower() and str.strip() for the column names
        filtered_dfs = self.dfs[self.match_name(self.dfs['Name'], name)]
        if filtered_dfs.iloc is None or filtered_dfs.empty:
            return None

        player_series = filtered_dfs.iloc[0]

        # Convert NaN to None, and then convert the Series to a dictionary
        player_dict = {key: (value if pd.notna(value) else None) for key, value in player_series.to_dict().items()}

        player = Player(**player_dict)
        json_output = player.model_dump_json()
        return json_output

    def match_name(self, name_series: pd.Series, name_to_match: str) -> pd.Series:
        """Matches player names and returns a boolean series of matches.

        :param name_series: The series of player names.
        :param name_to_match: The name to be matched.
        :return: Boolean series for matches.
        """
        name_to_match = name_to_match.lower().strip()
        match_scores = name_series.apply(lambda x: self.calculate_match_score(x.lower().strip(), name_to_match))

        # Return a boolean series for matches where score is greater than 0
        return match_scores > 90  # Returns True for matches

    def calculate_match_score(self, candidate_name: str, target_name: str) -> int:
        """Calculates the match score between two names.

        :param candidate_name: A candidate name to check against.
        :param target_name: The target name to match.
        :return: An integer match score.
        """
        # Check for exact match
        if candidate_name == target_name:
            return 100
        # Check for close match
        elif fuzz.token_sort_ratio(candidate_name, target_name) >= 80:  # Adjust the threshold as needed
            return fuzz.token_sort_ratio(candidate_name, target_name)
        # Check for some match using partial ratio if needed
        elif fuzz.partial_ratio(candidate_name, target_name) > 0:
            return fuzz.partial_ratio(candidate_name, target_name)
        
        return 0  # No match


if __name__ == "__main__":
    tool = PlayerDatabaseTool()
    player = tool.get_player_rating("isak")
    print(player)

