# 📋 Project Plan: Unified LLM API Wrapper (with MCP Support)

This document outlines the step-by-step implementation plan for a self-hostable, multi-provider LLM API wrapper. The project will unify access to OpenAI, OpenRouter, and Ollama, while also adding support for custom features and the Model Context Protocol (MCP).

---

## 📌 Project Goals

- Create a unified Python-based interface for multiple LLM providers
- Wrap key APIs: chat, embeddings, image generation, tools
- Support local hosting with proper config and environment handling
- Add extended features beyond official APIs (memory, prompt profiles, etc.)
- Enable tool/plugin system via MCP and OpenAI-compatible formats
- Make it GitHub-ready with clean project structure, docs, and security

---

## 🗂️ Project Structure

``` text
llm-wrapper/
├── core/                    # All LLM provider clients
│   ├── base_client.py       # Abstract class/interface
│   ├── openai_client.py
│   ├── openrouter_client.py
│   ├── ollama_client.py
│   └── mcp_client.py
│
├── plugins/                 # Optional tools/functions callable by LLMs
│   └── custom_tool.py
│
├── memory/                  # Optional memory integration (e.g., ChromaDB)
│   └── vector_store.py
│
├── router.py                # Provider dispatcher
├── api_wrapper.py           # Public interface (class or web API)
├── settings.py              # Configuration loader (.env or constants)
├── utils.py                 # Helpers: logging, streaming, retries
│
├── .env.example             # Example environment config
├── .gitignore
├── requirements.txt
├── setup.py                 # Optional install script
├── README.md
└── LICENSE
```

---

## 🛠️ Setup & Configuration

### 1. Environment Setup

- Use `python-dotenv` to load secrets from `.env`
- Create `.env.example` and `.gitignore` to protect keys
- Keys required:
  - `OPENAI_API_KEY`
  - `OPENROUTER_API_KEY`
  - `OLLAMA_HOST` (default to `http://localhost:11434/`)

### 2. `settings.py`

- Load and expose config values for the app
- Provide fallbacks and sanity checks

---

## 🔧 Core Feature Implementation

### ✅ Phase 1: Provider Clients (`core/`)

- [x] `base_client.py` – abstract methods for chat, embed, image
- [x] `openai_client.py` – full support for Chat, Embeddings, DALL·E, Tools
- [x] `openrouter_client.py` – mirror OpenAI format using requests
- [x] `ollama_client.py` – POST to `http://localhost:11434/api/chat`
- [ ] `mcp_client.py` – integration with Model Context Protocol

### ✅ Phase 2: Routing & Wrapper

- [x] `router.py` – simple router to call the correct provider
- [x] `api_wrapper.py` – single entry class for the user to interact with
- [ ] Add optional fallback or cascading call logic

### ✅ Phase 3: CLI or Web API

- [ ] FastAPI server exposing routes for `/chat`, `/embed`, `/image`
- [ ] WebSocket or SSE support for streaming
- [ ] Middleware for API key verification or basic auth

---

## 🌟 Custom Feature Extensions

### 🚀 Prompt Profiles

- [ ] `profiles.json` or `profiles/` folder
- [ ] Load predefined system messages per profile name
- [ ] Add to `.chat()` with `profile="roleplay_knight"`

### 🧠 Memory System

- [ ] Add `memory/vector_store.py` using Chroma or SQLite
- [ ] Store summaries, previous context, or embedding-indexed history
- [ ] Allow retrieval and injection into prompt as context
- [ ] Context aware and only adds to memory as context from current chat fills up
- [ ] Tag to define weather memory is for current chat only or chat agnostic
- [ ] Deletion of chat deletes any memory from that chat as long as it's tagged chat only

### 🧰 Plugin Tools (Function Calling)

- [ ] `plugins/` folder with Python functions
- [ ] Scan, register, and expose as tool list
- [ ] Tool return format compatible with OpenAI tool-calling
- [ ] Add built-in tools (math, calendar, wiki lookup, etc.)

### 📊 Model Benchmark Mode

- [ ] Run same prompt across all providers
- [ ] Compare latency, token usage, and output
- [ ] Export side-by-side report as JSON or markdown

### 🔌 MCP Integration

- [ ] Add `mcp_client.py` using MCP Python SDK
- [ ] Support querying MCP tools/documents
- [ ] Optionally expose the wrapper as an MCP server/node

---

## ✅ Developer Experience

### Security & GitHub Readiness

- [x] `.gitignore` excludes `.env`
- [x] `.env.example` for safe config sharing
- [ ] Add `CONTRIBUTING.md` and `LICENSE`
- [ ] Optional: Pre-commit hooks or linters (e.g., black, isort, flake8)

### Packaging

- [ ] `requirements.txt` for dependencies
- [ ] `setup.py` for pip install support
- [ ] Dockerfile and `docker-compose.yml` for container deployment

---

## 🚀 Deployment Options

### Local API

```bash
uvicorn api_wrapper:app --host 0.0.0.0 --port 8080
```

### Reverse Proxy (Optional)

- Use Nginx or Caddy to add HTTPS, CORS headers, and rate-limiting

### Docker (Optional)

```bash
docker build -t llm-wrapper .
docker run -p 8080:8080 --env-file .env llm-wrapper
```

---

## 🧪 Testing & Examples

- [ ] Unit tests for each client implementation
- [ ] Integration tests for full pipeline (router → provider → response)
- [ ] Example scripts or notebooks for:
  - Chat
  - Embedding generation
  - Tool calling
- [ ] Logging utility for saving query sessions

---

## 📅 Milestone Timeline (Suggested)

| Phase                | Est. Time | Priority |
|---------------------|-----------|----------|
| Environment & Config| 1 day     | ⭐⭐⭐⭐⭐    |
| Provider Clients    | 2–3 days  | ⭐⭐⭐⭐⭐    |
| Routing + Wrapper   | 1 day     | ⭐⭐⭐⭐     |
| MCP Integration     | 2 days    | ⭐⭐⭐      |
| Prompt Profiles     | 1 day     | ⭐⭐⭐      |
| Memory System       | 2 days    | ⭐⭐⭐⭐     |
| Plugin Tools        | 2 days    | ⭐⭐⭐      |
| Web API / UI        | 2 days    | ⭐⭐       |
| Docker + Deploy     | 1–2 days  | ⭐⭐       |

---

## 📌 Final Thoughts

This project is designed to be extensible, modder-friendly, and secure. Every module should be independently testable and replaceable. With clear abstraction and routing, adding support for new APIs in the future will be trivial. MCP integration and extended memory/tooling support will take this beyond a basic API bridge — into something closer to a lightweight LLM operating system.
