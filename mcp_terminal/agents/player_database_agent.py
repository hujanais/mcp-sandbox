import os
import sys
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.players_tool import PlayerDatabaseTool

load_dotenv()

systemPrompt = """
   You have detailed information about soccer players in a database.  When given a player's name, you can retrieve their attributes and statistics from the database.
   When asked about players or comparing players, you will always use the PlayerDatabaseTool to get the player attributes before answering.  Do not make up any player attributes since we have the 
   data in the database.  You are not responsible for analyzing and commenting on the players but rather just reporting the facts based on the data you retrieve.  

   Your final output will always just be a JSON array of player attributes.
"""
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    tools=[PlayerDatabaseTool()],
    system_message=systemPrompt,
    reasoning=True,
    tool_call_limit=5,
)

agent.print_response("Get info for Haaland", stream=True)
