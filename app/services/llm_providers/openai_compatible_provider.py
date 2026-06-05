from typing import Any

import httpx


OPENAI_COMPATIBLE_TIMEOUT_SECONDS = 60


class OpenAICompatibleProvider:
    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            },
            timeout=OPENAI_COMPATIBLE_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        data = response.json()
        answer = self._extract_answer(data)
        if not answer:
            raise ValueError("Provider compativel com OpenAI retornou resposta vazia")

        return answer

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def _extract_answer(self, data: dict[str, Any]) -> str:
        choices = data.get("choices", [])
        if not choices:
            return ""

        message = choices[0].get("message", {})
        content = message.get("content", "")

        if isinstance(content, str):
            return content.strip()

        return ""
