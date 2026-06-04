from typing import Any

from app.core.config import get_llm_config


FRIENDLY_LLM_ERROR_MESSAGE = (
    "Não consegui gerar uma resposta agora. Tente novamente em instantes."
)


def generate_answer(message: str, history: list[dict[str, str]]) -> str:
    config = get_llm_config()

    if not config.api_key:
        return FRIENDLY_LLM_ERROR_MESSAGE

    if config.provider.lower() != "gemini":
        return FRIENDLY_LLM_ERROR_MESSAGE

    try:
        client = _create_gemini_client(config.api_key)
        prompt = _build_prompt(message=message, history=history)
        response = client.models.generate_content(
            model=config.model,
            contents=prompt,
        )

        answer = getattr(response, "text", "")
        if not answer or not answer.strip():
            return FRIENDLY_LLM_ERROR_MESSAGE

        return answer.strip()
    except Exception:
        return FRIENDLY_LLM_ERROR_MESSAGE


def generate_chatbot_response(message: str) -> str:
    return generate_answer(message=message, history=[])


def _create_gemini_client(api_key: str) -> Any:
    from google import genai

    return genai.Client(api_key=api_key)


def _build_prompt(message: str, history: list[dict[str, str]]) -> str:
    history_text = _format_history(history)

    return (
        "Voce e um assistente virtual util, claro e objetivo.\n"
        "Use o historico da conversa para manter contexto quando for relevante.\n\n"
        f"Historico da conversa:\n{history_text}\n\n"
        f"Mensagem atual do usuario:\n{message}"
    )


def _format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "Sem historico anterior."

    formatted_messages = []

    for item in history:
        role = item.get("role", "unknown")
        content = item.get("content", "")

        if content:
            formatted_messages.append(f"{role}: {content}")

    if not formatted_messages:
        return "Sem historico anterior."

    return "\n".join(formatted_messages)

