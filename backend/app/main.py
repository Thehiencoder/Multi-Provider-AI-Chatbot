import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.schemas import (
    ChatRequest,
    ChatHistoryResponse,
    Message,
)
from app.services.redis_service import redis_service
from app.services.llm_factory import llm_factory

# Configure logger
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chatbot.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Multi-Provider AI Chatbot backend...")
    # Initialize redis connection
    await redis_service.get_client()
    yield
    logger.info("Shutting down backend, closing connections...")
    await redis_service.close()


app = FastAPI(
    title="Multi-Provider AI Chatbot Gateway",
    description="Unified streaming chat API with OpenAI, Claude, Gemini & Redis Memory",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Multi-Provider AI Chatbot"}


@app.get("/api/models")
async def get_models():
    """Retrieve all supported providers and their models with availability status."""
    return llm_factory.get_available_providers()


@app.get("/api/chat/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Retrieve full conversation history for a given session."""
    messages = await redis_service.get_history(session_id)
    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages,
        count=len(messages)
    )


@app.delete("/api/chat/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear conversation history for a given session."""
    success = await redis_service.clear_history(session_id)
    return {"session_id": session_id, "cleared": success}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, raw_req: Request):
    """
    Stream chat response from requested LLM provider using Server-Sent Events (SSE).
    Saves user message and assistant answer automatically to Redis with Sliding Window.
    """
    # 1. Validate Provider
    try:
        provider = llm_factory.get_provider(request.provider)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    # 2. Save new incoming user message(s) to Redis
    for msg in request.messages:
        await redis_service.save_message(request.session_id, msg)

    # 3. Fetch conversation context with Sliding Window for token management
    context_messages = await redis_service.get_history(
        session_id=request.session_id,
        limit=settings.SLIDING_WINDOW_SIZE
    )

    # If history is empty (e.g. redis failure), fallback to incoming messages
    if not context_messages:
        context_messages = request.messages

    # 4. SSE Generator with Auto-Saving Assistant Response
    async def sse_stream_generator() -> AsyncGenerator[dict, None]:
        full_assistant_response = []
        try:
            stream = provider.generate_stream(
                messages=context_messages,
                model=request.model,
                system_prompt=request.system_prompt,
                temperature=request.temperature or 0.7,
            )

            async for token in stream:
                # Check if client disconnected
                if await raw_req.is_disconnected():
                    logger.warning(f"Client disconnected for session {request.session_id}")
                    break

                full_assistant_response.append(token)
                yield {
                    "data": json.dumps({"token": token, "done": False, "error": None})
                }

        except Exception as e:
            logger.error(f"Error during stream generation: {e}")
            yield {
                "data": json.dumps({"token": None, "done": True, "error": str(e)})
            }
        finally:
            # 5. Persist the complete response to Redis
            complete_text = "".join(full_assistant_response).strip()
            if complete_text:
                await redis_service.save_message(
                    request.session_id,
                    Message(role="assistant", content=complete_text)
                )

            # Send final SSE completion signal
            yield {
                "data": json.dumps({"token": "", "done": True, "error": None})
            }

    return EventSourceResponse(sse_stream_generator())
