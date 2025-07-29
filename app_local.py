from services.llama_client import LlamaClient
# from llama_stack_client import LlamaStackClient

client = LlamaClient(base_url="http://127.0.0.1:8080/v1/chat/completions")
# client = LlamaStackClient(base_url="http://localhost:8080")

def simple_llama_chat():
    response = client.chat(
    messages=[{"role": "user", "content": "what is the wind condition in Kuala Lumpur?"}])

    print(response)

if __name__ == "__main__":
    simple_llama_chat()
    # simple_tools()
