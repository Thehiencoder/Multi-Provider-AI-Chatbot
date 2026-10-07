import logging
from typing import AsyncGenerator, List, Optional
from openai import AsyncOpenAI
from app.schemas import Message
from app.services.providers.base import BaseLLMProvider
from app.utils.normalization import to_openai_format

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.client: Optional[AsyncOpenAI] = None
        if self.is_available():
            self.client = AsyncOpenAI(api_key=self.api_key.strip())

    async def generate_stream(
        self,
        messages: List[Message],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        if not self.is_available() or not self.client:
            raise ValueError("OpenAI API Key is not configured or invalid.")

        formatted_messages = to_openai_format(messages, system_prompt)

        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise e
