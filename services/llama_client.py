import requests


class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class LlamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def chat(self, messages: list[Message], tools: list[dict[str, any]]):
        try:
            reqBody = {"messages": messages, "tools": tools}

            resp = requests.post(self.base_url, json=reqBody)
            resp.raise_for_status()
            jsonResp = resp.json()
            return jsonResp["choices"][0]["message"]
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
