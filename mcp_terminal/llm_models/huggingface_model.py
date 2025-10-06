import os
from agno.models.huggingface import HuggingFace
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("HUGGINGFACE_BASE_URL")
api_key = os.getenv("HUGGINGFACE_API_KEY")

hf_model = HuggingFace(base_url=url, api_key=api_key)