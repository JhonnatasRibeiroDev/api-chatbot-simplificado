import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    api_key: str


def get_llm_config() -> LLMConfig:
    return LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "gemini"),
        model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("LLM_API_KEY", ""),
    )


llm_config = get_llm_config()
