from core.openai_client import OpenAIClient
from core.openrouter_client import OpenRouterClient
from core.ollama_client import OllamaClient
from core.mcp_client import MCPClient
import json
import os
from memory.vector_store import InMemoryVectorStore

PROFILE_PATH = os.path.join(os.path.dirname(__file__), 'profiles', 'profiles.json')
with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
    PROFILES = json.load(f)

MEMORY_STORE = InMemoryVectorStore()

class Router:
    def __init__(self, provider):
        self.provider = provider.lower()
        self.clients = {
            'openai': OpenAIClient(),
            'openrouter': OpenRouterClient(),
            'ollama': OllamaClient(),
            'mcp': MCPClient(),
        }
        if self.provider not in self.clients:
            raise ValueError(f"Unknown provider: {self.provider}")
        self.client = self.clients[self.provider]

    def chat(self, messages, model=None, profile=None, chat_id=None, **kwargs):
        # Retrieve recent memory for this chat_id
        if chat_id:
            memory_entries = MEMORY_STORE.query(chat_id)
            for entry in memory_entries:
                if entry.get("metadata", {}).get("type") == "memory":
                    mem_msg = {"role": "system", "content": entry["vector"]}
                    messages = [mem_msg] + messages
        # Inject profile system message
        if profile:
            profile_data = PROFILES.get(profile)
            if profile_data and 'system' in profile_data:
                system_msg = {"role": "system", "content": profile_data['system']}
                messages = [system_msg] + messages
        # Call the client
        if model:
            response = self.client.chat(messages, model=model, **kwargs)
        else:
            response = self.client.chat(messages, **kwargs)
        # Store user message and model response in memory
        if chat_id:
            for msg in messages:
                if msg["role"] == "user":
                    MEMORY_STORE.add(chat_id, msg["content"], metadata={"type": "memory", "role": "user"})
            if isinstance(response, dict) and "choices" in response:
                for choice in response["choices"]:
                    content = choice.get("message", {}).get("content")
                    if content:
                        MEMORY_STORE.add(chat_id, content, metadata={"type": "memory", "role": "assistant"})
        return response

    def embed(self, *args, **kwargs):
        return self.client.embed(*args, **kwargs)

    def image(self, *args, **kwargs):
        return self.client.image(*args, **kwargs)
