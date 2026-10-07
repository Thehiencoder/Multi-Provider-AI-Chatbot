from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier for chat history")
    provider: Literal["openai", "claude", "gemini"] = Field(..., description="LLM Provider name")
    model: str = Field(..., description="Specific model ID to use")
    messages: List[Message] = Field(default_factory=list, description="New messages to send")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)


class ChatResponseStream(BaseModel):
    token: Optional[str] = None
    error: Optional[str] = None
    done: bool = False
    metadata: Optional[Dict[str, Any]] = None


class ModelInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class ProviderModelsResponse(BaseModel):
    provider: str
    name: str
    is_available: bool
    models: List[ModelInfo]


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Message]
    count: int
