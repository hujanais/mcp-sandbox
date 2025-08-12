import json
from tools.definitions import weather_tool
from tools.definitions.weather_tool import weather_tool_definition

from services.llama_client import LlamaClient

client = LlamaClient(base_url="http://127.0.0.1:8080/v1/chat/completions")

def simple_llama_chat():
    tools = [weather_tool_definition]
    messages = [
        {
            "role": "user",
            "content": "What is green + blue? What is the wind condition at Kuala Lumpur, Malaysia. 3.1319° N, 101.6841° E?",
        }
    ]

    response = client.chat(
        messages=messages,
        tools=tools,
    )

    print(response)

    # collect tool calls
    if 'tool_calls' not in response or not response['tool_calls']:
        print("no tool calls found")
        return

    for tool_call in response['tool_calls']:
        name = tool_call['function']['name']
        args = json.loads(tool_call['function']['arguments'])

        print(name, args)

        result = call_function(name, args)
        messages.append(response.choices[0].message)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "name": name,
                "content": str(result),
            }
        )

    print(response)

def call_function(name, args):
    if name == "get_weather":
        latitude = args["latitude"]
        longitude = args["longitude"]

        return weather_tool(latitude, longitude)

if __name__ == "__main__":
    simple_llama_chat()
    # simple_tools()
