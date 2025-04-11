import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

settings = Settings()
