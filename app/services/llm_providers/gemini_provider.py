from threading import Semaphore
import logging
from time import perf_counter
from time import sleep
from typing import Any


logger = logging.getLogger(__name__)

GEMINI_MAX_CONCURRENT_REQUESTS = 5
GEMINI_MAX_ATTEMPTS = 3
GEMINI_BACKOFF_SECONDS = (0.5, 1.0)
GEMINI_TIMEOUT_MS = 60000

_gemini_semaphore = Semaphore(GEMINI_MAX_CONCURRENT_REQUESTS)


class GeminiProvider:
    def __init__(self, api_key: str, model: str) -> None:
        started_at = perf_counter()
        self.api_key = api_key
        self.model = model
        self.client = self._create_client(api_key)
        logger.info(
            "Gemini client criado. model=%s elapsed_s=%.3f",
            self.model,
            perf_counter() - started_at,
        )

    def generate(self, prompt: str) -> str:
        for attempt in range(1, GEMINI_MAX_ATTEMPTS + 1):
            try:
                started_at = perf_counter()
                with _gemini_semaphore:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                    )
                elapsed = perf_counter() - started_at

                answer = getattr(response, "text", "")
                if not answer or not answer.strip():
                    raise ValueError("Gemini retornou resposta vazia")

                logger.info(
                    "Gemini generate_content concluido. model=%s attempt=%s "
                    "elapsed_s=%.3f prompt_chars=%s answer_chars=%s",
                    self.model,
                    attempt,
                    elapsed,
                    len(prompt),
                    len(answer),
                )

                return answer.strip()
            except Exception as error:
                elapsed = perf_counter() - started_at
                logger.exception(
                    "Gemini generate_content falhou. model=%s attempt=%s/%s "
                    "elapsed_s=%.3f erro=%s",
                    self.model,
                    attempt,
                    GEMINI_MAX_ATTEMPTS,
                    elapsed,
                    error,
                )

                if attempt == GEMINI_MAX_ATTEMPTS:
                    raise

                sleep(GEMINI_BACKOFF_SECONDS[attempt - 1])

        raise RuntimeError("Gemini nao retornou resposta")

    def _create_client(self, api_key: str) -> Any:
        from google import genai

        return genai.Client(
            api_key=api_key,
            http_options={"timeout": GEMINI_TIMEOUT_MS},
        )
