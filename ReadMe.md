# Smart-Host: Unified LLM API Wrapper

Smart-Host is a self-hostable, multi-provider LLM API wrapper that unifies access to OpenAI, OpenRouter, and Ollama through a single REST API. It provides a consistent interface for chat completions, embeddings, and image generation across different providers.

## Features

- **Unified API**: Access OpenAI, OpenRouter, and Ollama through identical endpoints
- **Multiple Capabilities**: Chat completions, embeddings, and image generation
- **Memory System**: Store and retrieve conversation history with chat_id
- **Prompt Profiles**: Use predefined system messages for different use cases
- **Robust Error Handling**: Detailed logging and standardized error responses
- **WebSocket Support**: Stream responses in real-time
- **Tool Integration**: Call custom tools directly from the API
- **Docker Ready**: Deploy easily with Docker and docker-compose

## Quickstart

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd Smart-Host
   ```

2. Copy and edit environment variables:

   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the API server:

   ```bash
   uvicorn api_wrapper:app --reload --port 8080
   ```

5. Or use Docker:

   ```bash
   docker-compose up --build
   ```

6. Access the API documentation at http://localhost:8080/docs

## API Endpoints

### Chat Completion

```
POST /chat
```

Request body:
```json
{
  "provider": "openai",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "model": "gpt-3.5-turbo",
  "profile": "default",
  "chat_id": "user-123"
}
```

### Embeddings

```
POST /embed
```

Request body:
```json
{
  "provider": "openai",
  "input": "Text to embed",
  "model": "text-embedding-ada-002"
}
```

### Image Generation

```
POST /image
```

Request body:
```json
{
  "provider": "openai",
  "prompt": "A beautiful sunset over the ocean"
}
```

### Available Tools

```
GET /tools
```

### Call a Tool

```
POST /call_tool
```

Request body:
```json
{
  "name": "tool_name",
  "args": ["arg1", "arg2"],
  "kwargs": {"param1": "value1"}
}
```

## WebSocket Streaming

Connect to `/ws_chat` with a WebSocket client and send a JSON payload similar to the `/chat` endpoint.

Example Python client:

```python
import asyncio
import websockets
import json

async def main():
    uri = "ws://localhost:8080/ws_chat"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "provider": "openai",
            "messages": [{"role": "user", "content": "Tell me a story"}]
        }))
        
        response = ""
        while True:
            chunk = await websocket.recv()
            if chunk == "[END]":
                break
            response += chunk
            print(chunk, end="", flush=True)
        
        print("\nFull response:", response)

asyncio.run(main())
```

## Prompt Profiles

You can create custom prompt profiles in `profiles/profiles.json`. Each profile contains a system message that gets prepended to your chat messages.

Example profiles.json:
```json
{
  "default": {
    "system": "You are a helpful assistant."
  },
  "programmer": {
    "system": "You are an expert programmer."
  },
  "concise": {
    "system": "You are a helpful assistant. Keep your answers concise and to the point."
  }
}
```

To use a profile, include the profile name in your chat request:
```json
{
  "provider": "openai",
  "messages": [{"role": "user", "content": "Help me with Python"}],
  "profile": "programmer"
}
```

## Memory System

Smart-Host includes a sophisticated memory system that supports both conversation-specific and user-specific memory:

### Memory Types

1. **Conversation-specific Memory**:
   - Tied to a specific conversation/chat thread
   - Useful for maintaining context within a single conversation
   - Identified by `chat_id` in API calls

2. **User-specific Memory**:
   - Persists across multiple conversations with the same user
   - Perfect for remembering user preferences, facts, or history
   - Identified by `user_id` in API calls

### Using Memory in Chat Requests

To use the memory system, include the appropriate parameters in your chat request:

```json
{
  "provider": "openai",
  "messages": [{"role": "user", "content": "What's my favorite color?"}],
  "model": "gpt-3.5-turbo",
  "chat_id": "conversation-123",          // For conversation-specific memory
  "user_id": "user-456",                  // For user-specific memory
  "include_user_memory": true,            // Whether to include user memory in context
  "save_to_user_memory": true             // Whether to save this exchange to user memory
}
```

#### Parameters Explained:

- `chat_id`: Identifies a specific conversation. Messages are stored and retrieved using this ID.
- `user_id`: Identifies a specific user across conversations. User preferences and facts can be stored here.
- `include_user_memory`: When true, the API will include user-specific memory in the context.
- `save_to_user_memory`: When true, the current exchange will be saved to user-specific memory for future conversations.

### Memory Management API

Smart-Host provides endpoints to manage memory:

#### Delete Conversation Memory

```
DELETE /memory/conversation/{conversation_id}
```

#### Delete User Memory

```
DELETE /memory/user/{user_id}
```

#### Get Memory Statistics

```
GET /memory/status
```

Returns statistics about current memory usage, including counts and IDs of both user and conversation memories.

### Memory Strategy Recommendations

For best results with the memory system:

1. **For casual chatbots**:
   - Use only `chat_id` for conversation-specific context
   - No need to set `user_id` or `save_to_user_memory`

2. **For personal assistants**:
   - Use both `chat_id` and `user_id`
   - Set `save_to_user_memory: true` for important user facts
   - Example: "My name is Alice" or "I prefer dark mode"

3. **For user preferences**:
   - Use `user_id` with `save_to_user_memory: true`
   - Keep `include_user_memory: true` to maintain consistent user experience

4. **For privacy-sensitive applications**:
   - Regularly call the memory deletion endpoints
   - Consider implementing automatic memory expiration

### Memory Example

First conversation:

```json
// Request 1
{
  "provider": "openai",
  "messages": [{"role": "user", "content": "My name is Alice and I love blue."}],
  "chat_id": "conversation-1",
  "user_id": "user-123",
  "save_to_user_memory": true
}

// Request 2 (same conversation)
{
  "provider": "openai",
  "messages": [{"role": "user", "content": "What's my name?"}],
  "chat_id": "conversation-1",
  "user_id": "user-123"
}
// Response: "Your name is Alice."
```

Second conversation (different chat_id, same user_id):

```json
// Request 3
{
  "provider": "openai",
  "messages": [{"role": "user", "content": "What's my favorite color?"}],
  "chat_id": "conversation-2",
  "user_id": "user-123",
  "include_user_memory": true
}
// Response: "Your favorite color is blue."
```

This demonstrates how user-specific memory persists across different conversations, while conversation-specific memory is isolated to each chat.

## Environment Variables

Configure your API using the following environment variables in `.env`:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OLLAMA_HOST`: URL for your Ollama instance (default: http://localhost:11434/)
- `API_HOST`: Host to bind the API server to (default: 0.0.0.0)
- `API_PORT`: Port to run the API server on (default: 8080)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Set logging level (default: INFO)

## Adding Custom Tools

Create new Python files in the `plugins/` directory to define custom tools.

Example custom tool:

```python
def weather(location: str):
    """Get the weather for a location"""
    # Implement weather lookup
    return {
        "location": location,
        "temperature": "72°F",
        "conditions": "Sunny"
    }
```

Tools will be automatically discovered and made available through the `/tools` endpoint.

## Logging

Logs are written to both the console and `smart_host.log` in the project directory. The log level can be adjusted in the `.env` file.

## Contributors

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
