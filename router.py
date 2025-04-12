from core.openai_client import OpenAIClient
from core.openrouter_client import OpenRouterClient
from core.ollama_client import OllamaClient
import json
import os
import time
from memory.vector_store import InMemoryVectorStore
from utils import log_error, log_request, log_response

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
        }
        if self.provider not in self.clients:
            raise ValueError(f"Unknown provider: {self.provider}")
        self.client = self.clients[self.provider]

    def chat(self, messages, model=None, profile=None, chat_id=None, user_id=None, 
              include_user_memory=True, save_to_user_memory=False, **kwargs):
        start_time = time.time()
        try:
            # Log internal operation
            log_request(self.provider, "router.chat", {
                "model": model,
                "profile": profile,
                "chat_id": chat_id,
                "user_id": user_id,
                "include_user_memory": include_user_memory,
                "save_to_user_memory": save_to_user_memory,
                "messages_count": len(messages) if messages else 0
            })
            
            # Retrieve conversation-specific memory
            memory_entries = []
            if chat_id:
                memory_entries = MEMORY_STORE.query(chat_id, include_user_memory=False)
                
            # Add user-specific memory if requested and available
            if user_id and include_user_memory:
                user_memory = MEMORY_STORE.query(user_id, include_user_memory=True)
                # Prepend user memories before conversation memories
                memory_entries = user_memory + memory_entries
                
            # Add memory entries to messages
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
                else:
                    log_error(ValueError(f"Profile not found: {profile}"), {"profile_name": profile})
            
            # Call the client
            if model:
                response = self.client.chat(messages, model=model, **kwargs)
            else:
                response = self.client.chat(messages, **kwargs)
            
            # Store user message and model response in memory
            if chat_id or user_id:
                timestamp = time.time()
                
                for msg in messages:
                    if msg["role"] == "user":
                        if chat_id:
                            # Save to conversation memory
                            MEMORY_STORE.add(
                                chat_id, 
                                msg["content"], 
                                metadata={
                                    "type": "memory", 
                                    "role": "user",
                                    "timestamp": timestamp
                                },
                                memory_type="conversation"
                            )
                        
                        # Optionally save to user memory
                        if user_id and save_to_user_memory:
                            MEMORY_STORE.add(
                                user_id, 
                                msg["content"], 
                                metadata={
                                    "type": "memory", 
                                    "role": "user",
                                    "timestamp": timestamp
                                },
                                memory_type="user"
                            )
                
                if isinstance(response, dict) and "choices" in response:
                    for choice in response["choices"]:
                        content = choice.get("message", {}).get("content")
                        if content:
                            if chat_id:
                                # Save to conversation memory
                                MEMORY_STORE.add(
                                    chat_id, 
                                    content, 
                                    metadata={
                                        "type": "memory", 
                                        "role": "assistant",
                                        "timestamp": timestamp
                                    },
                                    memory_type="conversation"
                                )
                            
                            # Optionally save to user memory
                            if user_id and save_to_user_memory:
                                MEMORY_STORE.add(
                                    user_id, 
                                    content, 
                                    metadata={
                                        "type": "memory", 
                                        "role": "assistant",
                                        "timestamp": timestamp
                                    },
                                    memory_type="user"
                                )
            
            # Log successful operation
            log_response(self.provider, "router.chat", 200, time.time() - start_time)
            return response
            
        except Exception as e:
            # Log the error
            log_error(e, {
                "provider": self.provider,
                "model": model,
                "profile": profile,
                "chat_id": chat_id,
                "user_id": user_id
            })
            # Re-raise the exception to be handled by the API layer
            raise

    def embed(self, input, model=None, **kwargs):
        start_time = time.time()
        try:
            # Log internal operation
            log_request(self.provider, "router.embed", {
                "model": model,
                "input_length": len(input) if input else 0
            })
            
            # Call the client
            response = self.client.embed(input, model=model, **kwargs)
            
            # Log successful operation
            log_response(self.provider, "router.embed", 200, time.time() - start_time)
            return response
            
        except Exception as e:
            # Log the error
            log_error(e, {
                "provider": self.provider,
                "model": model,
                "input_length": len(input) if input else 0
            })
            # Re-raise the exception to be handled by the API layer
            raise

    def image(self, prompt, **kwargs):
        start_time = time.time()
        try:
            # Log internal operation
            log_request(self.provider, "router.image", {
                "prompt_length": len(prompt) if prompt else 0
            })
            
            # Call the client
            response = self.client.image(prompt, **kwargs)
            
            # Log successful operation
            log_response(self.provider, "router.image", 200, time.time() - start_time)
            return response
            
        except Exception as e:
            # Log the error
            log_error(e, {
                "provider": self.provider,
                "prompt_length": len(prompt) if prompt else 0
            })
            # Re-raise the exception to be handled by the API layer
            raise
