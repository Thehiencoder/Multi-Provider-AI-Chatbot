import logging
from typing import AsyncGenerator, List, Optional
from app.schemas import Message
from app.services.providers.base import BaseLLMProvider
from app.utils.normalization import to_gemini_format

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.client = None
        if self.is_available():
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key.strip())
            except ImportError:
                # Fallback to legacy google.generativeai if installed
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key.strip())
                self.client = "legacy"

    async def generate_stream(
        self,
        messages: List[Message],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        if not self.is_available() or not self.client:
            raise ValueError("Gemini API Key is not configured or invalid.")

        system_msg, formatted_contents = to_gemini_format(messages, system_prompt)

        # Standardize model names if necessary (e.g. gemini-2.5-flash, gemini-1.5-flash)
        model_name = model if not model.startswith("models/") else model.replace("models/", "")

        try:
            if self.client == "legacy":
                import google.generativeai as legacy_genai
                gen_model = legacy_genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_msg
                )
                response = await gen_model.generate_content_async(
                    contents=formatted_contents,
                    generation_config={"temperature": temperature},
                    stream=True
                )
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text
            else:
                from google.genai import types
                config = types.GenerateContentConfig(
                    temperature=temperature,
                )
                if system_msg:
                    config.system_instruction = system_msg

                response = await self.client.aio.models.generate_content_stream(
                    model=model_name,
                    contents=formatted_contents,
                    config=config
                )
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise e
