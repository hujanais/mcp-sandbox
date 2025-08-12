weather_tool_definition = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather condition for provided location.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}
