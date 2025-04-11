import requests
import json
import sys

base_url = "http://localhost:8080"
print(f"Testing API at {base_url}")

# Test server connectivity first
print("\n=== Testing server connectivity ===")
try:
    response = requests.get(f"{base_url}/docs")  # FastAPI auto-generates /docs endpoint
    print(f"Server is running and responding (status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to server at http://localhost:8080")
    print("Make sure the server is running with: uvicorn api_wrapper:app --host 0.0.0.0 --port 8080")
    sys.exit(1)

# Test /tools endpoint
print("\n=== Testing /tools endpoint ===")
try:
    response = requests.get(f"{base_url}/tools")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test /call_tool endpoint
print("\n=== Testing /call_tool endpoint ===")
try:
    data = {
        "name": "add",
        "args": [2, 3],
        "kwargs": {}
    }
    response = requests.post(f"{base_url}/call_tool", json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test /chat endpoint with Ollama
print("\n=== Testing /chat endpoint with Ollama ===")
try:
    data = {
        "provider": "ollama",
        "messages": [
            {"role": "user", "content": "Hello, please give a very brief response."}
        ],
        "profile": "concise"
    }
    response = requests.post(f"{base_url}/chat", json=data)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")

print("\nAll tests completed!")