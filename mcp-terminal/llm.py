from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def chat(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    print(response.choices[0].message.content)

if __name__ == "__main__":
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
            chat(user_input)
    except KeyboardInterrupt:
        print("\nExiting...")


