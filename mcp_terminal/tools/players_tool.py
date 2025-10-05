from typing import Dict
import os
from typing import Any, List, Union

import pandas as pd
from agno.tools import Toolkit

# https://www.kaggle.com/datasets/nyagami/ea-sports-fc-25-database-ratings-and-stats?resource=download

class PlayerDatabaseTool(Toolkit):
    """PlayerDatabaseTool that retrieves player information."""
    def __init__(self, **kwargs):
        tools: List[Any] = [self.get_player_rating]
        self.dfs = pd.read_csv("./data/all_players.csv")
        super().__init__(name="PlayerDatabaseTool", tools=tools, **kwargs)

    def get_player_rating(self, name: str) -> List[Dict[str, Union[str, int]]]:
        """Retrieves player attributes based on the player name.

        :param name: The name of the player.
        :return: A DataFram containing player ratings information.  If no player is found, returns empty dataframe. The dataframe may contain multiple players if the name is not unique.
        
        Schema of the DataFrame:
            Rank: Player’s ranking based on overall rating (OVR) within the FC 25 group.
            Name: The full name of the player.
            Height: The player’s height
            Weight: The player’s weight
            Position: The primary position the player plays on the field
            Alternative positions: Other positions the player is capable of playing effectively.
            Age: The player’s age.
            Nation: The country the player represents in international competitions.
            League: The football league in which the player currently plays.
            Team: The club team the player is part of.
            Play style: Specific gameplay traits or tendencies that define the player’s behavior and skillset on the field (e.g., "Quick Step", "Finesse Shot").
            URL: A link to the player's detailed profile.
            Player Attributes
            Acceleration: The player’s ability to reach maximum speed quickly.
            Sprint Speed: The top speed the player can achieve when sprinting.
            Positioning: The player's awareness and positioning in attack.
            Finishing: The player’s ability to convert scoring chances into goals.
            Shot Power: The strength of the player’s shots on goal.
            Long Shots: The accuracy and power of shots taken from outside the penalty area.
            Volleys: The player’s ability to strike the ball cleanly from mid-air.
            Penalties: The player's skill at taking penalty kicks.
            Passing and Vision
            Vision: The player's ability to make accurate passes and see plays develop.
            Crossing: The ability to deliver accurate crosses from wide areas.
            Free Kick Accuracy: The player’s precision when taking free kicks.
            Short Passing: The accuracy and skill in making short-distance passes.
            Long Passing: The ability to deliver accurate long-range passes.
            Curve: The player’s ability to bend the ball during passes or shots.
            Dribbling and Agility
            Dribbling: The player’s ball control and ability to maneuver in tight spaces.
            Agility: How quickly and smoothly the player can change direction.
            Balance: The player’s stability and ability to stay on their feet under pressure.
            Reactions: The player’s responsiveness to unpredictable events during the game.
            Ball Control: How well the player controls the ball while moving.
            Mentality and Defense
            Composure: The player’s calmness under pressure.
            Interceptions: The player’s ability to read and intercept passes.
            Heading Accuracy: The player's precision when attempting to head the ball.
            Defensive Awareness (Def Awareness): The player’s positioning and ability to anticipate defensive situations.
            Standing Tackle: The player’s ability to win the ball with a standing tackle.
            Sliding Tackle: The skill and accuracy of the player’s sliding tackles.
            Physical Attributes
            Jumping: The player’s ability to jump high during headers or challenges.
            Stamina: The player’s endurance and ability to perform at a high level throughout the match.
            Strength: The player’s physical power and ability to win physical challenges.
            Aggression: The player’s determination and intensity in winning challenges and duels.
            Technical Skills
            Weak foot: The player’s proficiency with their non-dominant foot (rated from 1 to 5 stars).
            Skill moves: The player’s ability to perform advanced dribbling moves (rated from 1 to 5 stars).
            Preferred foot: Indicates whether the player prefers using their left or right foot.
            Goalkeeping Attributes (if applicable)
            GK Diving: The goalkeeper’s ability to dive and make saves.
            GK Handling: The goalkeeper’s skill in catching or holding onto the ball.
            GK Kicking: The accuracy and power of the goalkeeper’s kicks when distributing the ball.
            GK Positioning: The goalkeeper’s ability to position themselves effectively during defensive situations.
            GK Reflexes: The goalkeeper’s quickness in reacting to shots.

        """
        return self.dfs[self.dfs["Name"].str.contains(name, case=False)].to_json()
 
if __name__ == "__main__":
    tool = PlayerDatabaseTool()
    dfs = tool.get_player_rating("shitto")
    print(dfs)

