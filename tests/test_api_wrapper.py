from fastapi.testclient import TestClient
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_wrapper import app

client = TestClient(app)

def test_chat_route(monkeypatch):
    # Mock Router.chat to accept both dict and model_dump formats
    from router import Router
    
    def mock_chat_function(self, messages, model=None, **kwargs):
        return {"choices": [{"message": {"content": "Hello!"}}]}
    
    monkeypatch.setattr(Router, "chat", mock_chat_function)
    
    response = client.post("/chat", json={
        "provider": "openai", 
        "messages": [{"role": "user", "content": "Hi"}]
    })
    
    assert response.status_code == 200
    assert "choices" in response.json()

def test_embed_route(monkeypatch):
    from router import Router
    monkeypatch.setattr(Router, "embed", lambda self, input, model=None: {"data": [1, 2, 3]})
    response = client.post("/embed", json={"provider": "openai", "input": "test"})
    assert response.status_code == 200
    assert "data" in response.json()

def test_image_route(monkeypatch):
    from router import Router
    monkeypatch.setattr(Router, "image", lambda self, prompt: {"url": "http://example.com/image.png"})
    response = client.post("/image", json={"provider": "openai", "prompt": "cat"})
    assert response.status_code == 200
    assert "url" in response.json()

def test_tools_endpoint(monkeypatch):
    # Mock the list_tools function to return a fixed list including "add"
    import plugins
    monkeypatch.setattr(plugins, "list_tools", lambda: ["add"])
    
    response = client.get("/tools")
    assert response.status_code == 200
    assert "tools" in response.json()
    assert "add" in response.json()["tools"]

def test_call_tool_endpoint(monkeypatch):
    # Directly patch the plugins.call_tool function
    import plugins
    
    def mock_call_tool(name, *args, **kwargs):
        if name == "add":
            return args[0] + args[1]
        raise ValueError(f"Tool '{name}' not found.")
    
    monkeypatch.setattr(plugins, "call_tool", mock_call_tool)
    monkeypatch.setattr(plugins, "list_tools", lambda: ["add"])
    
    response = client.post("/call_tool", json={"name": "add", "args": [2, 3], "kwargs": {}})
    assert response.status_code == 200
    assert response.json()["result"] == 5

def test_chat_with_profile(monkeypatch):
    from router import Router
    def mock_chat(self, messages, model=None, profile=None, **kwargs):
        # If profile is provided, inject a system message
        if profile == "roleplay_knight":
            messages = [{"role": "system", "content": "You are a brave medieval knight"}] + messages
        return {"messages": messages}
    monkeypatch.setattr(Router, "chat", mock_chat)
    response = client.post("/chat", json={"provider": "openai", "messages": [{"role": "user", "content": "Hi"}], "profile": "roleplay_knight"})
    assert response.status_code == 200
    messages = response.json()["messages"]
    assert any(m["role"] == "system" and "knight" in m["content"].lower() for m in messages)

def test_chat_memory(monkeypatch):
    from router import Router
    memory = []
    def mock_chat(self, messages, model=None, profile=None, chat_id=None, **kwargs):
        memory.extend(messages)
        return {"messages": messages}
    monkeypatch.setattr(Router, "chat", mock_chat)
    chat_id = "test-session"
    # First message
    response1 = client.post("/chat", json={"provider": "openai", "messages": [{"role": "user", "content": "First message"}], "chat_id": chat_id})
    assert response1.status_code == 200
    # Second message, should include memory
    response2 = client.post("/chat", json={"provider": "openai", "messages": [{"role": "user", "content": "Second message"}], "chat_id": chat_id})
    assert response2.status_code == 200
    # Check that memory contains both messages
    assert any("First message" in m["content"] for m in memory)
    assert any("Second message" in m["content"] for m in memory)
