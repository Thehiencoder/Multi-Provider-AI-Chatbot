from typing import Dict, List
from app.config import settings
from app.schemas import ModelInfo, ProviderModelsResponse
from app.services.providers.base import BaseLLMProvider
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.claude_provider import ClaudeProvider
from app.services.providers.gemini_provider import GeminiProvider


class LLMFactory:
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._init_providers()

    def _init_providers(self):
        self._providers["openai"] = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        self._providers["claude"] = ClaudeProvider(api_key=settings.ANTHROPIC_API_KEY)
        self._providers["gemini"] = GeminiProvider(api_key=settings.GEMINI_API_KEY)

    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        provider = self._providers.get(provider_name.lower())
        if not provider:
            raise ValueError(f"Provider '{provider_name}' is not supported. Choose from: openai, claude, gemini.")
        if not provider.is_available():
            raise ValueError(f"Provider '{provider_name}' is not configured. Please add the API key in .env.")
        return provider

    def get_available_providers(self) -> List[ProviderModelsResponse]:
        models_catalog = [
            ProviderModelsResponse(
                provider="gemini",
                name="Google Gemini",
                is_available=self._providers["gemini"].is_available(),
                models=[
                    ModelInfo(id="gemini-3.8-flash", name="Gemini 3.8 Flash", description="Model thế hệ mới nhất, siêu nhanh & được Google khuyến nghị"),
                    ModelInfo(id="gemini-3.7-flash", name="Gemini 3.7 Flash", description="Model thông minh cân bằng, suy luận tốt"),
                    ModelInfo(id="gemini-3.6-flash", name="Gemini 3.6 Flash", description="Model tốc độ cao và độ ổn định cao"),
                ]
            ),
            ProviderModelsResponse(
                provider="openai",
                name="OpenAI",
                is_available=self._providers["openai"].is_available(),
                models=[
                    ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", description="Mô hình chính nhẹ, nhanh & tiết kiệm chi phí"),
                    ModelInfo(id="gpt-4o", name="GPT-4o (Omni)", description="Mô hình thông minh flagship của OpenAI"),
                    ModelInfo(id="o3-mini", name="o3-mini", description="Mô hình Reasoning (suy luận logic) tốc độ cao"),
                    ModelInfo(id="o1", name="o1", description="Mô hình suy luận sâu giải toán và lập trình đỉnh cao"),
                ]
            ),
            ProviderModelsResponse(
                provider="claude",
                name="Anthropic Claude",
                is_available=self._providers["claude"].is_available(),
                models=[
                    ModelInfo(id="claude-3-5-sonnet-20241022", name="Claude 3.5 Sonnet", description="Top 1 về coding và tư duy kiến trúc"),
                    ModelInfo(id="claude-3-5-haiku-20241022", name="Claude 3.5 Haiku", description="Phản hồi nhanh tức thì cho đoạn chat ngắn"),
                    ModelInfo(id="claude-3-opus-20240229", name="Claude 3 Opus", description="Xử lý văn bản dài và phân tích chuyên sâu"),
                ]
            ),
        ]
        return models_catalog


llm_factory = LLMFactory()
