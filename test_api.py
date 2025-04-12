import requests
import json
import time
from fastapi.testclient import TestClient
from api_wrapper import app

client = TestClient(app)

def print_separator():
    print("\n" + "="*50 + "\n")

# Test the health endpoint to check if providers are available
print_separator()
print("🔍 TESTING API HEALTH")
print_separator()

response = client.get("/health")
print(f"Status code: {response.status_code}")
health_data = response.json()
print(json.dumps(health_data, indent=2))

# Test OpenRouter provider
print_separator()
print("🔍 TESTING OPENROUTER PROVIDER")
print_separator()

print("Testing Chat Completion:")
try:
    response = client.post("/chat", json={
        "provider": "openrouter", 
        "messages": [{"role": "user", "content": "What's the capital of France? Keep it brief."}],
        "model": "openai/gpt-3.5-turbo"  # OpenRouter model
    })
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        chat_response = response.json()
        print("Response content:")
        if "choices" in chat_response and chat_response["choices"]:
            content = chat_response["choices"][0]["message"]["content"]
            print(f"Answer: {content}")
        else:
            print(json.dumps(chat_response, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error testing OpenRouter chat: {str(e)}")

# Test embeddings
print("\nTesting Embeddings:")
try:
    response = client.post("/embed", json={
        "provider": "openrouter",
        "input": "This is a test sentence for embeddings.",
        "model": "openai/text-embedding-ada-002"  # OpenRouter embedding model
    })
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        embed_response = response.json()
        print(f"Embedding dimensions: {len(embed_response['data'][0]['embedding'])}")
        print(f"First 5 values: {embed_response['data'][0]['embedding'][:5]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error testing OpenRouter embeddings: {str(e)}")

# Test Ollama provider
print_separator()
print("🔍 TESTING OLLAMA PROVIDER")
print_separator()

print("Testing Chat Completion:")
try:
    response = client.post("/chat", json={
        "provider": "ollama", 
        "messages": [{"role": "user", "content": "What's 2+2? Keep it brief."}],
        "model": "llama2"  # Ollama model
    })
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        chat_response = response.json()
        print("Response content:")
        if "choices" in chat_response and chat_response["choices"]:
            content = chat_response["choices"][0]["message"]["content"]
            print(f"Answer: {content}")
        else:
            print(json.dumps(chat_response, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error testing Ollama chat: {str(e)}")

# Test with memory
print_separator()
print("🔍 TESTING MEMORY SYSTEM")
print_separator()

chat_id = f"test-{int(time.time())}"
print(f"Using chat_id: {chat_id}")

# First message
print("\nSending first message:")
try:
    response = client.post("/chat", json={
        "provider": "openrouter", 
        "messages": [{"role": "user", "content": "My name is Alice."}],
        "model": "openai/gpt-3.5-turbo",
        "chat_id": chat_id
    })
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        chat_response = response.json()
        if "choices" in chat_response and chat_response["choices"]:
            content = chat_response["choices"][0]["message"]["content"]
            print(f"Answer: {content}")
    else:
        print(f"Error: {response.text}")
        
    # Second message that references first
    print("\nSending follow-up message:")
    response = client.post("/chat", json={
        "provider": "openrouter", 
        "messages": [{"role": "user", "content": "What's my name?"}],
        "model": "openai/gpt-3.5-turbo",
        "chat_id": chat_id
    })
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        chat_response = response.json()
        if "choices" in chat_response and chat_response["choices"]:
            content = chat_response["choices"][0]["message"]["content"]
            print(f"Answer: {content}")
            if "Alice" in content:
                print("✅ Memory test passed! The API remembered the name.")
            else:
                print("❌ Memory test failed. The API did not remember the name.")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error testing memory: {str(e)}")

# Test profiles
print_separator()
print("🔍 TESTING PROFILES")
print_separator()

try:
    response = client.post("/chat", json={
        "provider": "openrouter", 
        "messages": [{"role": "user", "content": "Tell me about yourself."}],
        "model": "openai/gpt-3.5-turbo",
        "profile": "concise"
    })
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        chat_response = response.json()
        if "choices" in chat_response and chat_response["choices"]:
            content = chat_response["choices"][0]["message"]["content"]
            print(f"Answer with 'concise' profile: {content}")
            print(f"Character count: {len(content)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error testing profiles: {str(e)}")

print_separator()
print("✅ TESTING COMPLETE")
print_separator()