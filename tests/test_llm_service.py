import pytest

from app.core.config import LLMConfig
from app.services import llm_service
from app.services.llm_providers.gemini_provider import GeminiProvider


class FakeProvider:
    def __init__(self, answer: str):
        self.answer = answer
        self.last_prompt = ""

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.answer


class FailingProvider:
    def generate(self, prompt: str) -> str:
        raise RuntimeError("api unavailable")


class FakeResponse:
    def __init__(self, text: str):
        self.text = text


class FakeModels:
    def __init__(self, text: str):
        self.text = text
        self.last_model = None
        self.last_contents = None

    def generate_content(self, model: str, contents: str):
        self.last_model = model
        self.last_contents = contents
        return FakeResponse(self.text)


class FlakyModels:
    def __init__(self):
        self.calls = 0

    def generate_content(self, model: str, contents: str):
        self.calls += 1

        if self.calls == 1:
            raise RuntimeError("temporary api error")

        return FakeResponse("Resposta apos retry")


class AlwaysFailingModels:
    def __init__(self):
        self.calls = 0

    def generate_content(self, model: str, contents: str):
        self.calls += 1
        raise RuntimeError("api unavailable")


class FakeClient:
    def __init__(self, text: str):
        self.models = FakeModels(text)


class FlakyClient:
    def __init__(self):
        self.models = FlakyModels()


class AlwaysFailingClient:
    def __init__(self):
        self.models = AlwaysFailingModels()


def test_generate_answer_returns_provider_text(monkeypatch):
    fake_provider = FakeProvider("Resposta real do provider")

    monkeypatch.setattr(
        llm_service,
        "get_llm_config",
        lambda: LLMConfig(
            provider="gemini",
            model="gemini-3.5-flash",
            api_key="fake-key",
            base_url="",
        ),
    )
    monkeypatch.setattr(
        llm_service,
        "create_llm_provider",
        lambda config: fake_provider,
    )

    answer = llm_service.generate_answer(
        message="Qual foi minha primeira pergunta?",
        history=[
            {"role": "user", "content": "Ola"},
            {"role": "assistant", "content": "Ola, como posso ajudar?"},
        ],
    )

    assert answer == "Resposta real do provider"
    assert "user: Ola" in fake_provider.last_prompt
    assert "assistant: Ola, como posso ajudar?" in fake_provider.last_prompt
    assert "Qual foi minha primeira pergunta?" in fake_provider.last_prompt


def test_generate_answer_returns_friendly_message_when_provider_fails(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "get_llm_config",
        lambda: LLMConfig(
            provider="gemini",
            model="gemini-3.5-flash",
            api_key="fake-key",
            base_url="",
        ),
    )
    monkeypatch.setattr(
        llm_service,
        "create_llm_provider",
        lambda config: FailingProvider(),
    )

    answer = llm_service.generate_answer(message="Ola", history=[])

    assert answer == llm_service.FRIENDLY_LLM_ERROR_MESSAGE


def test_generate_answer_returns_friendly_message_for_invalid_config(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "get_llm_config",
        lambda: LLMConfig(
            provider="unsupported",
            model="test-model",
            api_key="",
            base_url="",
        ),
    )

    answer = llm_service.generate_answer(message="Ola", history=[])

    assert answer == llm_service.FRIENDLY_LLM_ERROR_MESSAGE


def test_gemini_provider_returns_model_text(monkeypatch):
    fake_client = FakeClient("Resposta real do Gemini")

    monkeypatch.setattr(
        GeminiProvider,
        "_create_client",
        lambda self, api_key: fake_client,
    )

    provider = GeminiProvider(api_key="fake-key", model="gemini-3.5-flash")
    answer = provider.generate("Prompt de teste")

    assert answer == "Resposta real do Gemini"
    assert fake_client.models.last_model == "gemini-3.5-flash"
    assert fake_client.models.last_contents == "Prompt de teste"


def test_gemini_provider_retries_and_returns_text_when_second_attempt_works(
    monkeypatch,
):
    fake_client = FlakyClient()

    monkeypatch.setattr(
        GeminiProvider,
        "_create_client",
        lambda self, api_key: fake_client,
    )
    monkeypatch.setattr(
        "app.services.llm_providers.gemini_provider.sleep",
        lambda seconds: None,
    )

    provider = GeminiProvider(api_key="fake-key", model="gemini-3.5-flash")
    answer = provider.generate("Ola")

    assert answer == "Resposta apos retry"
    assert fake_client.models.calls == 2


def test_gemini_provider_retries_three_times_before_raising(monkeypatch):
    fake_client = AlwaysFailingClient()

    monkeypatch.setattr(
        GeminiProvider,
        "_create_client",
        lambda self, api_key: fake_client,
    )
    monkeypatch.setattr(
        "app.services.llm_providers.gemini_provider.sleep",
        lambda seconds: None,
    )

    provider = GeminiProvider(api_key="fake-key", model="gemini-3.5-flash")

    with pytest.raises(RuntimeError):
        provider.generate("Ola")

    assert fake_client.models.calls == 3
