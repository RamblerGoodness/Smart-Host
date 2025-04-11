from fastapi import FastAPI, HTTPException, Body, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
from router import Router
from settings import settings
from plugins import list_tools, call_tool
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Any

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    provider: str
    messages: List[Message]
    model: Optional[str] = None
    profile: Optional[str] = None
    chat_id: Optional[str] = None

class EmbedRequest(BaseModel):
    provider: str
    input: str
    model: Optional[str] = None

class ImageRequest(BaseModel):
    provider: str
    prompt: str

class CallToolRequest(BaseModel):
    name: str
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        router = Router(request.provider)
        return router.chat(
            [m.model_dump() for m in request.messages],
            model=request.model,
            profile=request.profile,
            chat_id=request.chat_id
        )
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/embed")
def embed(request: EmbedRequest):
    try:
        router = Router(request.provider)
        return router.embed(request.input, model=request.model)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/image")
def image(request: ImageRequest):
    try:
        router = Router(request.provider)
        return router.image(request.prompt)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tools")
def get_tools():
    return {"tools": list_tools()}

@app.post("/call_tool")
def api_call_tool(request: CallToolRequest):
    try:
        result = call_tool(request.name, *request.args, **request.kwargs)
        return {"result": result}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws_chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            provider = data.get("provider")
            messages = data.get("messages")
            model = data.get("model")
            profile = data.get("profile")
            chat_id = data.get("chat_id")
            router = Router(provider)
            # Simulate streaming by splitting response into chunks
            response = router.chat(messages, model=model, profile=profile, chat_id=chat_id)
            if isinstance(response, dict) and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                # Stream content in chunks
                for i in range(0, len(content), 20):
                    await websocket.send_text(content[i:i+20])
                    await asyncio.sleep(0.05)
                await websocket.send_text("[END]")
            else:
                await websocket.send_text(str(response))
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
