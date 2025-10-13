import os
import sys
from agno.workflow import Workflow, Step, Steps, StepInput, StepOutput
from agno.agent import Agent
from agno.team import Team

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from llm_models.llm_models import hf_model, openai_model
from tools.players_tool import PlayerDatabaseTool
from tools.vega_python_tool import AltairVegaTools

# Define agents
datastore_agent = Agent(
    name="Data Store Agent",
    model=openai_model,
    tools=[PlayerDatabaseTool()],
    system_message = """
        You shall determine the name of the player queried and then just use the PlayerDatabaseTool to get the player attributes and return it without any further modifications or explanations.    
    """,
    role="Get latest player stats from the player datastore.",
    debug_mode=True,
)

vega_agent = Agent(
    name="Vega Agent",
    model=openai_model,
    role="You are an expert writing python code for Vega Altair charts.",
    system_message = """
        You are a helpful coding assistant that is an expert in using the Vega-Altair python charting package used to build clear, and informative professional charts to best describe the data.

        You shall return only the code without any explanations. The format to return is very specific and needs to be in the following boilerplate template:

        ```python
        import json
        import altair as alt
        import pandas as pd
        import math

        # Input Dataframe: this data is always defined outside this function
        df = pd.DataFrame(json.loads(jsonData))

        # chart = <The implementation of the chart code>

        # Always assign the final chart html output to the variable 'result'
        result = chart.to_html()
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

if __name__ == "__main__":
    # research_team.print_response("Analyze Lionel Messi.")
    vega_agent.print_response("Get me the player attributes for Lionel Messi.")

# content_planner = Agent(
#     name="Content Planner",
#     model=OpenAIChat(id="gpt-4o"),
#     instructions=[
#         "Plan a content schedule over 4 weeks for the provided topic and research content",
#         "Ensure that I have posts for 3 posts per week",
#     ],
# )

datastore_step = Step(
    name="DataStore Step",
    agent=datastore_agent)

vega_code_step = Step(
    name="Vega Code Step",
    agent=vega_agent)

def run_python_code(step_input: StepInput) -> StepOutput:
    code = step_input.to_dict()['previous_step_content']
    return StepOutput(AltairVegaTools().run_python_code(code=code, jsonData=step_input.to_dict()['datastore_step_content']))

vega_html_step = Step(
    name="Vega HTML Step",
    executor=run_python_code)

# step_2 = Step(
#     name="Step 2",
#     executor=lambda input: StepOutput(content=input.to_dict()['previous_step_content'].upper()))


# # Define steps
# research_step = Step(
#     name="Research Step",
#     team=research_team,
# )

# content_planning_step = Step(
#     name="Content Planning Step",
#     agent=content_planner,
# )

# Create a Steps sequence that chains these above steps together
main_sequence = Steps(
    name="article_creation",
    description="Complete article creation workflow from research to final edit",
    steps=[datastore_step, vega_code_step],
)

# Create and use workflow
if __name__ == "__main__":
    main_workflow = Workflow(
        name="Main Analysis Workflow",
        description="Automated workflow for getting player data and generating analysis with stats and graphs.",
        steps=[main_sequence],
    )

    main_workflow.print_response(
        input="Analyze Lionel Messi."
    )