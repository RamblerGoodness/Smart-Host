import os
import pytest
import requests
from unittest.mock import MagicMock, patch
from core.openai_client import OpenAIClient
from core.openrouter_client import OpenRouterClient
from core.ollama_client import OllamaClient

def test_openai_chat():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello there!"}}]
        }
        mock_post.return_value = mock_response
        
        client = OpenAIClient(api_key="mock-key")
        response = client.chat([
            {"role": "user", "content": "Hello!"}
        ])
        assert 'choices' in response

def test_openrouter_chat():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello from OpenRouter!"}}]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="mock-key")
        response = client.chat([
            {"role": "user", "content": "Hello!"}
        ])
        assert 'choices' in response

def test_ollama_chat():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Hello from Ollama!"}
        }
        mock_post.return_value = mock_response
        
        client = OllamaClient(host="http://localhost:11434")
        response = client.chat([
            {"role": "user", "content": "Hello!"}
        ])
        assert 'message' in response
