import os
import sys
import pandas as pd
from typing import Any, List
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.players_tool import PlayerDatabaseTool
from tools.python_tool import PythonTools

load_dotenv()
  
systemPrompt = """
   You have detailed information about soccer players in a database.  When given a player's name, you can retrieve their attributes and statistics from the database.
"""
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    tools=[PlayerDatabaseTool()],
    system_message=systemPrompt,
    tool_call_limit=1)

agent.print_response("Get data for Messi", stream=True)
