from typing import Dict, Optional
import os
from typing import Any, List, Union

import pandas as pd
from pydantic import BaseModel, Field
from agno.tools import Toolkit

# https://www.kaggle.com/datasets/nyagami/ea-sports-fc-25-database-ratings-and-stats?resource=download

class Player(BaseModel):
    rank: Optional[int] = Field(None, description="Player’s ranking based on overall rating (OVR) within the FC 25 group.")
    name: Optional[str] = Field(None, description="The full name of the player.")
    height: Optional[int] = Field(None, description="The player’s height.")
    weight: Optional[int] = Field(None, description="The player’s weight.")
    position: Optional[str] = Field(None, description="The primary position the player plays on the field.")
    alternative_positions: Optional[str] = Field(None, description="Other positions the player is capable of playing effectively.")
    age: Optional[int] = Field(None, description="The player’s age.")
    nation: Optional[str] = Field(None, description="The country the player represents in international competitions.")
    league: Optional[str] = Field(None, description="The football league in which the player currently plays.")
    team: Optional[str] = Field(None, description="The club team the player is part of.")
    play_style: Optional[str] = Field(None, description="Specific gameplay traits or tendencies that define the player’s behavior and skillset on the field.")
    url: Optional[str] = Field(None, description="A link to the player's detailed profile.")
    
    # Player Attributes
    acceleration: Optional[int] = Field(None, description="The player’s ability to reach maximum speed quickly.")
    sprint_speed: Optional[int] = Field(None, description="The top speed the player can achieve when sprinting.")
    positioning: Optional[int] = Field(None, description="The player's awareness and positioning in attack.")
    finishing: Optional[int] = Field(None, description="The player’s ability to convert scoring chances into goals.")
    shot_power: Optional[int] = Field(None, description="The strength of the player’s shots on goal.")
    long_shots: Optional[int] = Field(None, description="The accuracy and power of shots taken from outside the penalty area.")
    volleys: Optional[int] = Field(None, description="The player’s ability to strike the ball cleanly from mid-air.")
    penalties: Optional[int] = Field(None, description="The player's skill at taking penalty kicks.")
    
    # Passing and Vision
    vision: Optional[int] = Field(None, description="The player's ability to make accurate passes and see plays develop.")
    crossing: Optional[int] = Field(None, description="The ability to deliver accurate crosses from wide areas.")
    free_kick_accuracy: Optional[int] = Field(None, description="The player’s precision when taking free kicks.")
    short_passing: Optional[int] = Field(None, description="The accuracy and skill in making short-distance passes.")
    long_passing: Optional[int] = Field(None, description="The ability to deliver accurate long-range passes.")
    curve: Optional[int] = Field(None, description="The player’s ability to bend the ball during passes or shots.")
    
    # Dribbling and Agility
    dribbling: Optional[int] = Field(None, description="The player’s ball control and ability to maneuver in tight spaces.")
    agility: Optional[int] = Field(None, description="How quickly and smoothly the player can change direction.")
    balance: Optional[int] = Field(None, description="The player’s stability and ability to stay on their feet under pressure.")
    reactions: Optional[int] = Field(None, description="The player’s responsiveness to unpredictable events during the game.")
    ball_control: Optional[int] = Field(None, description="How well the player controls the ball while moving.")
    
    # Mentality and Defense
    composure: Optional[int] = Field(None, description="The player’s calmness under pressure.")
    interceptions: Optional[int] = Field(None, description="The player’s ability to read and intercept passes.")
    heading_accuracy: Optional[int] = Field(None, description="The player's precision when attempting to head the ball.")
    defensive_awareness: Optional[int] = Field(None, alias="Def Awareness", description="The player’s positioning and ability to anticipate defensive situations.")
    standing_tackle: Optional[int] = Field(None, description="The player’s ability to win the ball with a standing tackle.")
    sliding_tackle: Optional[int] = Field(None, description="The skill and accuracy of the player’s sliding tackles.")
    
    # Physical Attributes
    jumping: Optional[int] = Field(None, description="The player’s ability to jump high during headers or challenges.")
    stamina: Optional[int] = Field(None, description="The player’s endurance and ability to perform at a high level throughout the match.")
    strength: Optional[int] = Field(None, description="The player’s physical power and ability to win physical challenges.")
    aggression: Optional[int] = Field(None, description="The player’s determination and intensity in winning challenges and duels.")
    
    # Technical Skills
    weak_foot: Optional[int] = Field(None, description="The player’s proficiency with their non-dominant foot (rated from 1 to 5 stars).")
    skill_moves: Optional[int] = Field(None, description="The player’s ability to perform advanced dribbling moves (rated from 1 to 5 stars).")
    preferred_foot: Optional[str] = Field(None, description="Indicates whether the player prefers using their left or right foot.")
    
    # Goalkeeping Attributes (if applicable)
    gk_diving: Optional[int] = Field(None, description="The goalkeeper’s ability to dive and make saves.")
    gk_handling: Optional[int] = Field(None, description="The goalkeeper’s skill in catching or holding onto the ball.")
    gk_kicking: Optional[int] = Field(None, description="The accuracy and power of the goalkeeper’s kicks when distributing the ball.")
    gk_positioning: Optional[int] = Field(None, description="The goalkeeper’s ability to position themselves effectively during defensive situations.")
    gk_reflexes: Optional[int] = Field(None, description="The goalkeeper’s quickness in reacting to shots.")


class PlayerDatabaseTool(Toolkit):
    """PlayerDatabaseTool that retrieves player information."""
    def __init__(self, **kwargs):
        tools: List[Any] = [self.get_player_rating]
        self.dfs = pd.read_csv("./data/all_players.csv")
        self.dfs = self.dfs.iloc[:, 2:] # drop the first two columns
        super().__init__(name="PlayerDatabaseTool", tools=tools, **kwargs)

    def get_player_rating(self, name: str) -> str:
        """Retrieves player attributes based on the player name.

        :param name: The name of the player.
        :return: json representation of the player attributes.
        """
        filtered_dfs = self.dfs[self.match_exact_name(self.dfs['Name'], name)]
        return filtered_dfs.to_json(orient="records")

    def match_exact_name(self, name_series, name_to_match: str) -> List[bool]:
        return name_series.apply(lambda x: name_to_match.lower() in [word.lower() for word in x.split()])


if __name__ == "__main__":
    tool = PlayerDatabaseTool()
    player = tool.get_player_rating("messi")
    print(player)

