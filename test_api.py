import requests
from fastapi.testclient import TestClient
from api_wrapper import app

client = TestClient(app)

# Test the /tools endpoint
response = client.get("/tools")
print("\n=== Testing /tools endpoint ===")
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")

# Test the /call_tool endpoint
response = client.post("/call_tool", json={"name": "add", "args": [2, 3], "kwargs": {}})
print("\n=== Testing /call_tool endpoint ===")
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")

# Test the Ollama provider since it doesn't require API keys
print("\n=== Testing /chat endpoint with Ollama ===")
response = client.post("/chat", json={
    "provider": "ollama", 
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "profile": "concise"
})
print(f"Status code: {response.status_code}")
try:
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text}")