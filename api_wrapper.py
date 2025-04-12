from fastapi import FastAPI, HTTPException, Body, WebSocket, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import asyncio
import time
from router import Router, MEMORY_STORE
from settings import settings
from plugins import list_tools, call_tool
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Any
from utils import log_error, log_request, log_response, format_error_response

app = FastAPI(
    title="Smart-Host LLM API",
    description="A unified API for multiple LLM providers including OpenAI, OpenRouter, and Ollama",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender (system, user, or assistant)")
    content: str = Field(..., description="The content of the message")

class ChatRequest(BaseModel):
    provider: str = Field(..., description="LLM provider to use (openai, openrouter, or ollama)")
    messages: List[Message] = Field(..., description="List of conversation messages with roles and content")
    model: Optional[str] = Field(None, description="Specific model to use (e.g., gpt-3.5-turbo, mistral-7b)")
    profile: Optional[str] = Field(None, description="Profile name from profiles.json to use for system message")
    chat_id: Optional[str] = Field(None, description="Unique identifier for the conversation memory")
    user_id: Optional[str] = Field(None, description="User identifier for user-specific memory across conversations")
    include_user_memory: Optional[bool] = Field(True, description="Whether to include user memory in the context")
    save_to_user_memory: Optional[bool] = Field(False, description="Whether to save this exchange to user memory")

class EmbedRequest(BaseModel):
    provider: str = Field(..., description="LLM provider to use (openai, openrouter, or ollama)")
    input: str = Field(..., description="Text to convert into embeddings")
    model: Optional[str] = Field(None, description="Specific embedding model to use")

class ImageRequest(BaseModel):
    provider: str = Field(..., description="LLM provider to use (openai, openrouter)")
    prompt: str = Field(..., description="Text description of the image to generate")

class CallToolRequest(BaseModel):
    name: str = Field(..., description="Name of the tool to call")
    args: List[Any] = Field(default_factory=list, description="Positional arguments for the tool")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments for the tool")

@app.post("/chat", tags=["LLM Endpoints"], 
         summary="Generate a chat completion",
         description="Send a conversation to an LLM provider and get a completion response")
def chat(request: ChatRequest):
    start_time = time.time()
    try:
        # Log the incoming request
        log_request(request.provider, "chat", {
            "model": request.model,
            "profile": request.profile,
            "chat_id": request.chat_id,
            "user_id": request.user_id,
            "include_user_memory": request.include_user_memory,
            "save_to_user_memory": request.save_to_user_memory,
            "messages_count": len(request.messages)
        })
        
        router = Router(request.provider)
        response = router.chat(
            [m.model_dump() for m in request.messages],
            model=request.model,
            profile=request.profile,
            chat_id=request.chat_id,
            user_id=request.user_id,
            include_user_memory=request.include_user_memory,
            save_to_user_memory=request.save_to_user_memory
        )
        
        # Log the successful response
        log_response(request.provider, "chat", 200, time.time() - start_time)
        return response
        
    except ValidationError as ve:
        log_error(ve, {"request": request.model_dump()})
        return JSONResponse(
            status_code=422,
            content=format_error_response(ve)
        )
    except Exception as e:
        log_error(e, {"request": request.model_dump()})
        return JSONResponse(
            status_code=500,
            content=format_error_response(e)
        )

@app.post("/embed", tags=["LLM Endpoints"],
         summary="Generate embeddings",
         description="Convert text into vector embeddings using the specified provider")
def embed(request: EmbedRequest):
    start_time = time.time()
    try:
        # Log the incoming request
        log_request(request.provider, "embed", {
            "model": request.model,
            "input_length": len(request.input)
        })
        
        router = Router(request.provider)
        response = router.embed(request.input, model=request.model)
        
        # Log the successful response
        log_response(request.provider, "embed", 200, time.time() - start_time)
        return response
        
    except ValidationError as ve:
        log_error(ve, {"request": request.model_dump()})
        return JSONResponse(
            status_code=422,
            content=format_error_response(ve)
        )
    except Exception as e:
        log_error(e, {"request": request.model_dump()})
        return JSONResponse(
            status_code=500,
            content=format_error_response(e)
        )

@app.post("/image", tags=["LLM Endpoints"],
         summary="Generate an image",
         description="Create an image based on a text prompt using the specified provider")
def image(request: ImageRequest):
    start_time = time.time()
    try:
        # Log the incoming request
        log_request(request.provider, "image", {
            "prompt_length": len(request.prompt)
        })
        
        router = Router(request.provider)
        response = router.image(request.prompt)
        
        # Log the successful response
        log_response(request.provider, "image", 200, time.time() - start_time)
        return response
        
    except ValidationError as ve:
        log_error(ve, {"request": request.model_dump()})
        return JSONResponse(
            status_code=422,
            content=format_error_response(ve)
        )
    except Exception as e:
        log_error(e, {"request": request.model_dump()})
        return JSONResponse(
            status_code=500,
            content=format_error_response(e)
        )

@app.get("/tools", tags=["Tools"],
       summary="List available tools",
       description="Returns a list of all available tools that can be called via the API")
def get_tools():
    start_time = time.time()
    try:
        tools = list_tools()
        log_response("system", "tools", 200, time.time() - start_time)
        return {"tools": tools}
    except Exception as e:
        log_error(e)
        return JSONResponse(
            status_code=500,
            content=format_error_response(e)
        )

@app.post("/call_tool", tags=["Tools"],
          summary="Execute a tool",
          description="Call a custom tool with specified arguments and return the result")
def api_call_tool(request: CallToolRequest):
    start_time = time.time()
    try:
        # Log the tool call
        log_request("system", "call_tool", {
            "name": request.name,
            "args_count": len(request.args),
            "kwargs_count": len(request.kwargs)
        })
        
        result = call_tool(request.name, *request.args, **request.kwargs)
        
        log_response("system", "call_tool", 200, time.time() - start_time)
        return {"result": result}
        
    except ValidationError as ve:
        log_error(ve, {"request": request.model_dump()})
        return JSONResponse(
            status_code=422,
            content=format_error_response(ve)
        )
    except Exception as e:
        log_error(e, {"request": request.model_dump()})
        return JSONResponse(
            status_code=500,
            content=format_error_response(e)
        )

@app.websocket("/ws_chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    start_time = time.time()
    try:
        while True:
            data = await websocket.receive_json()
            provider = data.get("provider")
            messages = data.get("messages")
            model = data.get("model")
            profile = data.get("profile")
            chat_id = data.get("chat_id")
            user_id = data.get("user_id")
            include_user_memory = data.get("include_user_memory", True)
            save_to_user_memory = data.get("save_to_user_memory", False)
            
            # Log the websocket request
            log_request(provider, "ws_chat", {
                "model": model,
                "profile": profile,
                "chat_id": chat_id,
                "user_id": user_id,
                "include_user_memory": include_user_memory,
                "save_to_user_memory": save_to_user_memory,
                "messages_count": len(messages) if messages else 0
            })
            
            router = Router(provider)
            # Simulate streaming by splitting response into chunks
            response = router.chat(
                messages, 
                model=model, 
                profile=profile, 
                chat_id=chat_id,
                user_id=user_id,
                include_user_memory=include_user_memory,
                save_to_user_memory=save_to_user_memory
            )
            
            if isinstance(response, dict) and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                # Stream content in chunks
                for i in range(0, len(content), 20):
                    await websocket.send_text(content[i:i+20])
                    await asyncio.sleep(0.05)
                await websocket.send_text("[END]")
            else:
                await websocket.send_text(str(response))
                
            # Log successful websocket response
            log_response(provider, "ws_chat", 200, time.time() - start_time)
            
    except Exception as e:
        log_error(e, {
            "provider": provider if 'provider' in locals() else "unknown",
            "endpoint": "ws_chat"
        })
        await websocket.close(code=1011, reason=str(e))

@app.get("/health", tags=["System"],
        summary="Check API health",
        description="Returns the health status of the API and its connected providers")
def health_check():
    """
    Check the health of the API and its connected providers.
    Returns status information and basic diagnostics.
    """
    health_status = {
        "status": "healthy",
        "version": app.version,
        "timestamp": time.time(),
        "providers": {}
    }
    
    # Check provider connections
    providers = ["openai", "openrouter", "ollama"]
    for provider in providers:
        try:
            # Just instantiate the router to check if provider configs are available
            Router(provider)
            health_status["providers"][provider] = "available"
        except Exception as e:
            health_status["providers"][provider] = f"unavailable: {str(e)}"
            # If any critical provider is down, mark system as degraded
            if provider in ["openai", "openrouter"]:
                health_status["status"] = "degraded"
    
    return health_status

@app.delete("/memory/conversation/{conversation_id}", tags=["Memory Management"],
           summary="Delete conversation memory",
           description="Delete all memory associated with a specific conversation")
def delete_conversation_memory(conversation_id: str):
    """
    Delete all memory entries for a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation whose memory should be deleted
    """
    try:
        MEMORY_STORE.delete_conversation(conversation_id)
        return {"status": "success", "message": f"Memory for conversation {conversation_id} has been deleted"}
    except Exception as e:
        log_error(e, {"conversation_id": conversation_id})
        return JSONResponse(
            status_code=500,
            content=format_error_response(e)
        )

@app.delete("/memory/user/{user_id}", tags=["Memory Management"],
           summary="Delete user memory",
           description="Delete all user-specific memory for a particular user")
def delete_user_memory(user_id: str):
    """
    Delete all user-specific memory entries for a specific user.
    
    Args:
        user_id: The ID of the user whose memory should be deleted
    """
    try:
        MEMORY_STORE.delete_user_memory(user_id)
        return {"status": "success", "message": f"Memory for user {user_id} has been deleted"}
    except Exception as e:
        log_error(e, {"user_id": user_id})
        return JSONResponse(
            status_code=500,
            content=format_error_response(e)
        )

@app.get("/memory/status", tags=["Memory Management"],
        summary="Get memory statistics",
        description="Returns statistics about the current memory usage")
def memory_status():
    """
    Get statistics about memory usage.
    
    Returns:
        Information about current memory usage including counts of user and conversation memories.
    """
    try:
        # Create a memory usage report
        user_count = len(MEMORY_STORE.memory['user'])
        conversation_count = len(MEMORY_STORE.memory['conversation'])
        
        # Count total entries
        user_entries = sum(len(entries) for entries in MEMORY_STORE.memory['user'].values())
        conversation_entries = sum(len(entries) for entries in MEMORY_STORE.memory['conversation'].values())
        
        return {
            "status": "success",
            "users": {
                "count": user_count,
                "total_entries": user_entries,
                "ids": list(MEMORY_STORE.memory['user'].keys())
            },
            "conversations": {
                "count": conversation_count,
                "total_entries": conversation_entries,
                "ids": list(MEMORY_STORE.memory['conversation'].keys())
            }
        }
    except Exception as e:
        log_error(e)
        return JSONResponse(
            status_code=500,
            content=format_error_response(e)
        )
