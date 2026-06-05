import asyncio
import statistics
import time
import unicodedata
from dataclasses import dataclass

import httpx
import pytest


BASE_URL = "http://127.0.0.1:8000"
FRIENDLY_LLM_ERROR_MESSAGE = (
    "Não consegui gerar uma resposta agora. Tente novamente em instantes."
)


@dataclass
class ChatBenchmarkResult:
    user_label: str
    session_id: str
    status_code: int
    latency_ms: float
    question: str
    response: str
    history_isolated: bool


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.casefold()


def _print_header(title: str) -> None:
    print("\n" + "=" * 88)
    print(f"[BENCHMARK] {title}")
    print("=" * 88)


def _print_kv(label: str, value: object) -> None:
    print(f"{label:<34} {value}")


async def _create_session(client: httpx.AsyncClient) -> str:
    response = await client.post(f"{BASE_URL}/api/sessions")
    response.raise_for_status()
    return response.json()["session_id"]


async def _send_chat_message(
    client: httpx.AsyncClient,
    session_id: str,
    message: str,
) -> tuple[int, float, dict]:
    start = time.perf_counter()
    response = await client.post(
        f"{BASE_URL}/api/chat",
        json={
            "session_id": session_id,
            "message": message,
        },
    )
    latency_ms = (time.perf_counter() - start) * 1000
    return response.status_code, latency_ms, response.json()


async def _get_history(client: httpx.AsyncClient, session_id: str) -> list[dict]:
    response = await client.get(f"{BASE_URL}/api/sessions/{session_id}/history")
    response.raise_for_status()
    return response.json()["history"]


async def _run_happy_path_scenario(client: httpx.AsyncClient) -> None:
    _print_header("CENARIO 1 - Fluxo Feliz de Sessao e Chat")

    session_id = await _create_session(client)
    _print_kv("Session ID criado", session_id)

    first_message = (
        "Olá, meu nome é Vinícius e estou no 6º período de Engenharia de Software."
    )
    first_status, first_latency, first_body = await _send_chat_message(
        client=client,
        session_id=session_id,
        message=first_message,
    )

    second_message = "Qual é o meu nome e o que eu curso?"
    second_status, second_latency, second_body = await _send_chat_message(
        client=client,
        session_id=session_id,
        message=second_message,
    )

    second_response = second_body.get("response", "")
    normalized_response = _normalize_text(second_response)
    history = await _get_history(client, session_id)

    kept_name = "vinicius" in normalized_response
    kept_course = (
        "engenharia de software" in normalized_response
        or "software" in normalized_response
    )
    no_fallback = second_response != FRIENDLY_LLM_ERROR_MESSAGE

    _print_kv("POST /api/chat #1 status", first_status)
    _print_kv("POST /api/chat #1 latencia", f"{first_latency:.2f} ms")
    _print_kv("POST /api/chat #2 status", second_status)
    _print_kv("POST /api/chat #2 latencia", f"{second_latency:.2f} ms")
    _print_kv("Historico total da sessao", f"{len(history)} mensagens")
    _print_kv("Validacao nome no contexto", "OK" if kept_name else "FALHOU")
    _print_kv("Validacao curso no contexto", "OK" if kept_course else "FALHOU")
    _print_kv("Fallback do LLM", "NAO" if no_fallback else "SIM")
    print("\n[RESPOSTA DO CHATBOT]")
    print(second_response)

    assert first_status == 200
    assert second_status == 200
    assert len(history) == 4
    assert kept_name
    assert kept_course
    assert no_fallback


async def _send_concurrent_user_message(
    client: httpx.AsyncClient,
    user_label: str,
    session_id: str,
    question: str,
    all_questions: list[str],
) -> ChatBenchmarkResult:
    status_code, latency_ms, body = await _send_chat_message(
        client=client,
        session_id=session_id,
        message=question,
    )
    history = await _get_history(client, session_id)
    history_text = "\n".join(item.get("content", "") for item in history)

    has_own_question = question in history_text
    has_other_question = any(
        other_question != question and other_question in history_text
        for other_question in all_questions
    )

    return ChatBenchmarkResult(
        user_label=user_label,
        session_id=session_id,
        status_code=status_code,
        latency_ms=latency_ms,
        question=question,
        response=body.get("response", ""),
        history_isolated=has_own_question and not has_other_question,
    )


async def _run_concurrency_scenario(client: httpx.AsyncClient) -> None:
    _print_header("CENARIO 2 - Carga Concorrente e Race Conditions")

    questions = [
        "Usuario 1: qual e a capital da Franca? Responda em uma frase curta.",
        "Usuario 2: quanto e 17 vezes 4? Responda em uma frase curta.",
        "Usuario 3: defina API em uma frase curta.",
        "Usuario 4: cite uma vantagem do FastAPI em uma frase curta.",
        "Usuario 5: o que e um chatbot? Responda em uma frase curta.",
    ]

    session_ids = await asyncio.gather(
        *(_create_session(client) for _ in range(len(questions)))
    )

    benchmark_start = time.perf_counter()
    results = await asyncio.gather(
        *(
            _send_concurrent_user_message(
                client=client,
                user_label=f"Usuario {index + 1}",
                session_id=session_ids[index],
                question=questions[index],
                all_questions=questions,
            )
            for index in range(len(questions))
        )
    )
    total_ms = (time.perf_counter() - benchmark_start) * 1000

    latencies = [result.latency_ms for result in results]
    success_count = sum(1 for result in results if result.status_code == 200)
    isolated_count = sum(1 for result in results if result.history_isolated)
    fallback_count = sum(
        1 for result in results if result.response == FRIENDLY_LLM_ERROR_MESSAGE
    )

    print(
        "\n"
        "USUARIO    STATUS   LATENCIA(ms)   HISTORICO_ISOLADO   SESSION_ID\n"
        + "-" * 88
    )
    for result in results:
        print(
            f"{result.user_label:<10} "
            f"{result.status_code:<8} "
            f"{result.latency_ms:>11.2f}   "
            f"{'OK' if result.history_isolated else 'FALHOU':<18} "
            f"{result.session_id}"
        )

    print("\n[RESUMO DE PERFORMANCE]")
    _print_kv("Requisicoes concorrentes", len(results))
    _print_kv("Status HTTP 200", f"{success_count}/{len(results)}")
    _print_kv("Historicos isolados", f"{isolated_count}/{len(results)}")
    _print_kv("Fallbacks do LLM", fallback_count)
    _print_kv("Tempo total simultaneo", f"{total_ms:.2f} ms")
    _print_kv("Latencia media", f"{statistics.mean(latencies):.2f} ms")
    _print_kv("Latencia mediana", f"{statistics.median(latencies):.2f} ms")
    _print_kv("Menor latencia", f"{min(latencies):.2f} ms")
    _print_kv("Maior latencia", f"{max(latencies):.2f} ms")

    print("\n[AMOSTRA DAS RESPOSTAS]")
    for result in results:
        response_preview = result.response.replace("\n", " ")[:160]
        print(f"- {result.user_label}: {response_preview}")

    assert success_count == len(results)
    assert isolated_count == len(results)


@pytest.mark.integration
def test_backend_live_benchmark() -> None:
    """
    Teste de integracao/benchmark contra o servidor FastAPI real.

    Pre-requisito:
    - a API precisa estar rodando em http://127.0.0.1:8000;
    - o arquivo .env precisa ter LLM_PROVIDER, LLM_MODEL e LLM_API_KEY validos;
    - este teste consome chamadas reais da API Gemini.
    """

    async def runner() -> None:
        async with httpx.AsyncClient(timeout=90) as client:
            try:
                health = await client.get(f"{BASE_URL}/health")
                health.raise_for_status()
            except httpx.HTTPError as exc:
                pytest.fail(
                    "Servidor local indisponivel em http://127.0.0.1:8000. "
                    "Inicie com: uvicorn app.main:app --reload. "
                    f"Erro original: {exc}"
                )

            _print_header("HEALTH CHECK")
            _print_kv("Endpoint", f"{BASE_URL}/health")
            _print_kv("Status", health.status_code)
            _print_kv("Resposta", health.text)

            await _run_happy_path_scenario(client)
            await _run_concurrency_scenario(client)

    asyncio.run(runner())
