import os
import sys
from agno.agent import Agent
from agno.team import Team
from agno.tools.mcp import MCPTools
from agno.workflow import Step, Steps, Workflow

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from llm_models.llm_models import openai_model
from tools.players_tool import PlayerDatabaseTool

# Define agents
datastore_agent = Agent(
    name="Data Store Agent",
    model=openai_model,
    tools=[PlayerDatabaseTool()],
    system_message="""
        You shall determine the name of the player queried and then just use the PlayerDatabaseTool to get the player attributes and return it without any further modifications or explanations.    
    """,
    role="Get latest player stats from the player datastore.",
    debug_mode=True,
)

analysis_agent = Agent(
    name="Analysis Agent",
    model=openai_model,
    system_message="""
        You are an expert soccer scout working in player development in a Premier League Club.  Your job is to always look objectively at the player attributes given to you and generate a research report on the player based on questions asked.  Don't rely on any stats in your
        memory but rather only use data that is given to you.  If nothing is given or missing attributes, let the user know.
        This is the schema of the data that you should expect: 
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
    """,
    debug_mode=True,
)

chart_agent = Agent(
    name="Chart Agent",
    model=openai_model,
    tools=[MCPTools(transport='sse', url='http://localhost:1122/sse')],
    system_message="""
        You are a chart expert and your only job is deliver the best chart possible for the data provided.  You shall think about the data and what was asked for before choosing the best chart format.
        You shall always first convert all data into a json format to be usable by the tool.
    """,
    debug_mode=True)

vega_agent = Agent(
    name="Vega Agent",
    model=openai_model,
    role="You are an expert writing python code for Vega Altair charts.",
    system_message="""
        You are a helpful coding assistant that is an expert in using the Vega-Altair python charting package used to build clear, and informative professional charts to best describe the data.

        You shall expect to receive a json string of data to be visualized with the following schema:
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

        Obviously for charting purposes, you should just drop any non-numeric columns like Name, Position, Nation, League, Team, play style, Preferred foot, Alternative positions.
        You shall return only the code without any explanations. The format to return is very specific and needs to be in the following boilerplate template:

        ```python
        import json
        import altair as alt
        import pandas as pd
        import math

        # The input data is of type json string.       
        jsonData = {"Name": "Lionel Messi", "PAC": 96, "SHO": 92, "PAS": 91, ... }
        df = pd.DataFrame(json.loads(jsonData))

        # chart = <The implementation of the chart code>

        # Always assign the final chart html output to the variable 'result'
        result = chart.to_html()
    """,
    debug_mode=True,
)

scout_team = Team(
    name="Scout Agent",
    model=openai_model,
    members=[datastore_agent, analysis_agent, chart_agent],
    system_message="""
        Delegate work to other agents before compiling the a final report.  
        Get real data from the player datastore and use the analysis agent to generate the research opinion.
        If you think you can use visualization for the report, you can use the vega agent to generate charts and just show the raw output without anymore processing for the charts part.
        Then package the final report.
    """,
    debug_mode=True,
)

# Define research team for complex analysis
research_team = Team(
    name="Research Team",
    members=[datastore_agent, vega_agent],
    instructions=[
        "Generate a comprehensive research report on given player or comparison between players using vega charts."
        "Ensure that the report is well-structured and includes relevant charts."
    ],
)

# if __name__ == "__main__":
#     # research_team.print_response("Analyze Lionel Messi.")
#     vega_agent.print_response("Get me the player attributes for Lionel Messi.")

# # content_planner = Agent(
# #     name="Content Planner",
# #     model=OpenAIChat(id="gpt-4o"),
# #     instructions=[
# #         "Plan a content schedule over 4 weeks for the provided topic and research content",
# #         "Ensure that I have posts for 3 posts per week",
# #     ],
# # )

# datastore_step = Step(
#     name="DataStore Step",
#     agent=datastore_agent)

# vega_code_step = Step(
#     name="Vega Code Step",
#     agent=vega_agent)

# def run_python_code(step_input: StepInput) -> StepOutput:
#     code = step_input.to_dict()['previous_step_content']
#     return StepOutput(AltairVegaTools().run_python_code(code=code, jsonData=step_input.to_dict()['datastore_step_content']))

# vega_html_step = Step(
#     name="Vega HTML Step",
#     executor=run_python_code)

# # step_2 = Step(
# #     name="Step 2",
# #     executor=lambda input: StepOutput(content=input.to_dict()['previous_step_content'].upper()))


# Define steps
step1 = Step(
    name="Get Data Step",
    agent=datastore_agent,
)

step2 = Step(
    name="Analyze Data",
    agent=analysis_agent,
)

# Create a Steps sequence that chains these above steps together
main_sequence = Steps(
    name="workflow",
    description="Workflow example",
    steps=[step1, step2],
)

# Create and use workflow
if __name__ == "__main__":
    # try:
    #     while True:
    #         user_input = input("Enter your prompt (or type 'exit()' to quit): ")
    #         user_input = user_input.strip()
    #         if user_input == "exit()":
    #             print("Exiting...")
    #             break
    #         if "exit" in user_input:
    #             print("Do you mean to exit? Please type 'exit()' to quit.")
    #             break

    #         scout_team.print_response(user_input)

    # except KeyboardInterrupt:
    #     print("\nExiting...")

    main_workflow = Workflow(
        name="Main Analysis Workflow",
        description="Automated workflow for getting player data and generating analysis.",
        steps=[main_sequence],
    )

    main_workflow.print_response(
        input="Compare Firmino and Isak's attacking attributes."
    )
