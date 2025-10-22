import json
from tools.definitions.weather_tool import weather_tool_definition

from tools.resources.weather_api import weather_tool

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def simple_chat():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {
                "role": "assistant",
                "content": "The Los Angeles Dodgers won the World Series in 2020.",
            },
            {"role": "user", "content": "Where was it played?"},
        ],
    )

    print(response)


def simple_tools():
    tools = [weather_tool_definition]
    messages = [
        {
            "role": "user",
            "content": "What is green + blue? and tell the sailing conditions in Seine River, Paris?",
        }
    ]

    # Initial prompts
    completion = client.chat.completions.create(model="o4-mini", messages=messages, tools=tools)

    # collect tool calls
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        result = call_function(name, args)
        messages.append(completion.choices[0].message)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": str(result),
            }
        )

    # send tool results back to llm.
    completion = client.chat.completions.create(model="o4-mini", messages=messages, tools=tools)

    print(completion)


def call_function(name, args):
    if name == "get_weather":
        latitude = args["latitude"]
        longitude = args["longitude"]

        return weather_tool(latitude, longitude)


if __name__ == "__main__":
    # simple_chat()
    simple_tools()
