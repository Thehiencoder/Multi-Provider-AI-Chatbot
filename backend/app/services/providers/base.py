from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional
from app.schemas import Message


class BaseLLMProvider(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def is_available(self) -> bool:
        """Check if provider has a valid API key configured."""
        return bool(self.api_key and self.api_key.strip())

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Stream tokens from LLM asynchronously.
        Yields text chunks as they arrive.
        """
        pass
