import asyncio
from playwright_client import PlaywrightClient


async def main():
    mcpClient = PlaywrightClient()
    await mcpClient.connect()

    try:
        while True:
            user_input = input("Enter your prompt (or type 'exit()' to quit): ")
            user_input = user_input.strip()
            if user_input == "exit()":
                print("Exiting...")
                break
            if "exit" in user_input:
                print("Do you mean to exit? Please type 'exit()' to quit.")
                break
            resp = await mcpClient.process_query(user_input)
            print(resp)

    except KeyboardInterrupt:
        await mcpClient.cleanup()
        print("\nExiting...")


if __name__ == "__main__":
    asyncio.run(main())
