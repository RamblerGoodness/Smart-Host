import os
import requests
from .base_client import BaseClient

class OllamaClient(BaseClient):
    def __init__(self, host=None):
        self.host = host or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        # Remove trailing slash if present to avoid double slashes in URLs
        self.host = self.host.rstrip('/')

    def chat(self, messages, model="llama2", **kwargs):
        url = f"{self.host}/api/chat"
        data = {"model": model, "messages": messages}
        data.update(kwargs)
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def embed(self, input, model="llama2", **kwargs):
        url = f"{self.host}/api/embeddings"
        data = {"model": model, "input": input}
        data.update(kwargs)
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def image(self, prompt, **kwargs):
        # Ollama does not support image generation
        raise NotImplementedError("Image generation not supported by Ollama.")
