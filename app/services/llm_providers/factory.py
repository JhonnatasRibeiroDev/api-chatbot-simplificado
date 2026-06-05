from app.core.config import LLMConfig
from app.services.llm_providers.base import LLMProvider
from app.services.llm_providers.gemini_provider import GeminiProvider
from app.services.llm_providers.ollama_provider import OllamaProvider
from app.services.llm_providers.openai_compatible_provider import (
    OpenAICompatibleProvider,
)


DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


def create_llm_provider(config: LLMConfig) -> LLMProvider:
    provider = config.provider.lower().strip()

    if provider == "gemini":
        _require_api_key(config.api_key, provider)
        return GeminiProvider(api_key=config.api_key, model=config.model)

    if provider == "openai":
        _require_api_key(config.api_key, provider)
        return OpenAICompatibleProvider(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url or DEFAULT_OPENAI_BASE_URL,
        )

    if provider == "openai_compatible":
        _require_base_url(config.base_url, provider)
        return OpenAICompatibleProvider(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url,
        )

    if provider == "ollama":
        return OllamaProvider(
            model=config.model,
            base_url=config.base_url or DEFAULT_OLLAMA_BASE_URL,
        )

    raise ValueError(f"Provider LLM nao suportado: {config.provider}")


def _require_api_key(api_key: str, provider: str) -> None:
    if not api_key:
        raise ValueError(f"LLM_API_KEY e obrigatoria para provider {provider}")


def _require_base_url(base_url: str, provider: str) -> None:
    if not base_url:
        raise ValueError(f"LLM_BASE_URL e obrigatoria para provider {provider}")
