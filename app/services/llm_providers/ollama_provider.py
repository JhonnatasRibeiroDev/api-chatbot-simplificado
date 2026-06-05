from typing import Any

import httpx


OLLAMA_TIMEOUT_SECONDS = 60


class OllamaProvider:
    def __init__(self, model: str, base_url: str) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        data = response.json()
        answer = self._extract_answer(data)
        if not answer:
            raise ValueError("Ollama retornou resposta vazia")

        return answer

    def _extract_answer(self, data: dict[str, Any]) -> str:
        answer = data.get("response", "")

        if isinstance(answer, str):
            return answer.strip()

        return ""
