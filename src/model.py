import os
from langchain_ollama import ChatOllama

from dotenv import load_dotenv

load_dotenv()


protocol = "https"
hostname = "dev.chat.cosy.bio"
host = f"{protocol}://{hostname}"
api_url = f"{host}/ollama"

api_key = os.getenv("OLLAMA_COSY_API_KEY")
headers = {"Authorization": "Bearer " + api_key}

class CosyChatOllama(ChatOllama):
    def __init__(self, model: str = "medllama2:latest", temperature: float = 0.0,
                 format: str = "json", num_predict=256, num_ctx=2048) -> None:
        super().__init__(base_url=api_url, model=model, temperature=temperature,
                         format=format, num_predict=num_predict, num_ctx=num_ctx, client_kwargs={'headers': headers})

