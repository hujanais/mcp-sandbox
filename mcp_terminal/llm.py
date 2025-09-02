from typing import List
from dotenv import load_dotenv
from openai import OpenAI

from mcp_terminal.services.qa_memory import QAMemory, RoleMessage

load_dotenv()

client = OpenAI()

def chat(prompt: str, chat_history: List[RoleMessage]) -> str:
    """
        Chat with OpenAI using the provided prompt and chat history.

        Args:
            prompt: The user's prompt.
            chat_history: The chat history as a list of RoleMessage.
    """
    messages = chat_history
    messages.append(RoleMessage("user", prompt))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        # messages=[
        #     {"role": "system", "content": "You are a helpful assistant."},
        #     {"role": "user", "content": prompt},
        # ],
        messages=messages, temperature=0.1
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    # prime the chat with some history
    qa_memory = QAMemory(system_prompt="You are a helpful assistant", depth=5)

    try:
        while True:
            user_input = input("Enter your prompt (or type 'exit()' to quit): ")
            user_input = user_input.strip()
            if user_input == "exit()":
                print("Exiting...")
                break
            if 'exit' in user_input:
                print("Do you mean to exit? Please type 'exit()' to quit.")
                break

            resp = chat(user_input, qa_memory.get_chat_history())

            qa_memory.add(user_input, resp)
            print(qa_memory.get_chat_history())

    except KeyboardInterrupt:
        print("\nExiting...")


