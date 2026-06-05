import logging
from time import perf_counter

from app.core.config import get_llm_config
from app.services.llm_providers import create_llm_provider


logger = logging.getLogger(__name__)

FRIENDLY_LLM_ERROR_MESSAGE = (
    "Nao consegui gerar uma resposta agora. Tente novamente em instantes."
)


def generate_answer(message: str, history: list[dict[str, str]]) -> str:
    started_at = perf_counter()
    config = get_llm_config()

    try:
        provider_started_at = perf_counter()
        provider = create_llm_provider(config)
        provider_elapsed = perf_counter() - provider_started_at

        prompt_started_at = perf_counter()
        prompt = _build_prompt(message=message, history=history)
        prompt_elapsed = perf_counter() - prompt_started_at

        generate_started_at = perf_counter()
        answer = provider.generate(prompt)
        generate_elapsed = perf_counter() - generate_started_at
        total_elapsed = perf_counter() - started_at

        logger.info(
            "LLM gerou resposta. provider=%s model=%s provider_s=%.3f "
            "prompt_s=%.3f generate_s=%.3f total_s=%.3f prompt_chars=%s "
            "answer_chars=%s",
            config.provider,
            config.model,
            provider_elapsed,
            prompt_elapsed,
            generate_elapsed,
            total_elapsed,
            len(prompt),
            len(answer),
        )

        return answer
    except Exception as error:
        total_elapsed = perf_counter() - started_at
        logger.exception(
            "Falha ao gerar resposta com LLM. provider=%s model=%s "
            "total_s=%.3f erro=%s",
            config.provider,
            config.model,
            total_elapsed,
            error,
        )
        return FRIENDLY_LLM_ERROR_MESSAGE


def generate_chatbot_response(message: str) -> str:
    return generate_answer(message=message, history=[])


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
