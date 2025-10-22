from collections import deque
from typing import List

from pydantic import BaseModel


class RoleMessage(BaseModel):
    role: str
    content: str

    def __init__(self, role: str, content: str):
        super().__init__(role=role, content=content)


class QAMemory:
    """
    A simple class to maintain a history of question-answer pairs for ChatGPT style interactions.
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response.choices[0].message.content}
        ],
    """

    def __init__(self, system_prompt: str, depth):
        self.depth = depth
        self.system_prompt = system_prompt
        self.history: deque[RoleMessage] = deque()

    def add(self, question, answer):
        """
        Add a question-answer pair to the history.

        Args:
            question: The user's question.
            answer: The AI's answer.
        """
        self.history.append(RoleMessage(role="user", content=question))
        self.history.append(RoleMessage(role="assistant", content=answer))

        numOfLines = len(self.history)
        if numOfLines > self.depth:
            self.history.popleft()

    def clear(self):
        """
        Clear the history.
        """
        self.history.clear()

    def get_chat_history(self) -> List[RoleMessage]:
        """
        Get the chat history formatted for OpenAI chat completions.

        Returns:
            A list of messages in OpenAI chat format.
        """
        messages = [RoleMessage(role="system", content=self.system_prompt)]
        for entry in self.history:
            messages.append(RoleMessage(role=entry.role, content=entry.content))

        return messages
