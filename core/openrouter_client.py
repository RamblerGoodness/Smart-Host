import os
import requests
from .base_client import BaseClient

class OpenRouterClient(BaseClient):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = 'https://openrouter.ai/api/v1/'

    def chat(self, messages, model="openrouter/gpt-3.5-turbo", **kwargs):
        url = self.base_url + 'chat/completions'
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"model": model, "messages": messages}
        data.update(kwargs)
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def embed(self, input, model="openrouter/text-embedding-ada-002", **kwargs):
        url = self.base_url + 'embeddings'
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"model": model, "input": input}
        data.update(kwargs)
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def image(self, prompt, **kwargs):
        # OpenRouter may not support image generation; raise NotImplementedError
        raise NotImplementedError("Image generation not supported by OpenRouter.")
