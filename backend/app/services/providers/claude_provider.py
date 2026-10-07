import logging
from typing import AsyncGenerator, List, Optional
from anthropic import AsyncAnthropic
from app.schemas import Message
from app.services.providers.base import BaseLLMProvider
from app.utils.normalization import to_claude_format

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.client: Optional[AsyncAnthropic] = None
        if self.is_available():
            self.client = AsyncAnthropic(api_key=self.api_key.strip())

    async def generate_stream(
        self,
        messages: List[Message],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        if not self.is_available() or not self.client:
            raise ValueError("Anthropic API Key is not configured or invalid.")

        system_msg, formatted_messages = to_claude_format(messages, system_prompt)

        # Anthropic requires at least 1 message
        if not formatted_messages:
            formatted_messages = [{"role": "user", "content": "Hello"}]

        try:
            kwargs = {
                "model": model,
                "messages": formatted_messages,
                "max_tokens": 4096,
                "temperature": temperature,
            }
            if system_msg:
                kwargs["system"] = system_msg

            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Claude streaming error: {e}")
            raise e
