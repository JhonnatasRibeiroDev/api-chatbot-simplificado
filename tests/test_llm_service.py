from app.services import llm_service


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


class FakeClient:
    def __init__(self, text: str):
        self.models = FakeModels(text)


def test_generate_answer_returns_model_text(monkeypatch):
    fake_client = FakeClient("Resposta real do Gemini")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("LLM_API_KEY", "fake-key")
    monkeypatch.setattr(
        llm_service,
        "_create_gemini_client",
        lambda api_key: fake_client,
    )

    answer = llm_service.generate_answer(
        message="Qual foi minha primeira pergunta?",
        history=[
            {"role": "user", "content": "Ola"},
            {"role": "assistant", "content": "Ola, como posso ajudar?"},
        ],
    )

    assert answer == "Resposta real do Gemini"
    assert fake_client.models.last_model == "gemini-2.5-flash"
    assert "user: Ola" in fake_client.models.last_contents
    assert "assistant: Ola, como posso ajudar?" in fake_client.models.last_contents
    assert "Qual foi minha primeira pergunta?" in fake_client.models.last_contents


def test_generate_answer_returns_friendly_message_without_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_MODEL", "gemini-2.5-flash")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    answer = llm_service.generate_answer(message="Ola", history=[])

    assert answer == llm_service.FRIENDLY_LLM_ERROR_MESSAGE


def test_generate_answer_returns_friendly_message_when_api_fails(monkeypatch):
    def raise_api_error(api_key: str):
        raise RuntimeError("api unavailable")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("LLM_API_KEY", "fake-key")
    monkeypatch.setattr(llm_service, "_create_gemini_client", raise_api_error)

    answer = llm_service.generate_answer(message="Ola", history=[])

    assert answer == llm_service.FRIENDLY_LLM_ERROR_MESSAGE


def test_generate_answer_returns_friendly_message_for_unsupported_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-test")
    monkeypatch.setenv("LLM_API_KEY", "fake-key")

    answer = llm_service.generate_answer(message="Ola", history=[])

    assert answer == llm_service.FRIENDLY_LLM_ERROR_MESSAGE
