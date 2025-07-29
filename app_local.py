import json
from tools.definitions.weather_tool import weather_tool_definition

from services.llama_client import LlamaClient

client = LlamaClient(base_url="http://127.0.0.1:8080/v1/chat/completions")

def simple_llama_chat():
    tools = [weather_tool_definition]
    messages = [
        {
            "role": "user",
            "content": "What is green + blue? and tell the sailing conditions in Seine River, Paris?",
        }
    ]

    response = client.chat(
        messages=messages,
        tools=tools,
    )

    print(response)

    # collect tool calls
    for tool_call in response.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        print(name, args)

    #     result = call_function(name, args)
    #     messages.append(response.choices[0].message)
    #     messages.append(
    #         {
    #             "role": "tool",
    #             "tool_call_id": tool_call.id,
    #             "name": name,
    #             "content": str(result),
    #         }
    #     )

    # print(response)


if __name__ == "__main__":
    simple_llama_chat()
    # simple_tools()
