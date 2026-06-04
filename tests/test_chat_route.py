from fastapi.testclient import TestClient

from app.main import app
from app.services.session_service import sessions


client = TestClient(app)


def test_chat_route_uses_llm_response_and_saves_history(monkeypatch):
    sessions.clear()

    def fake_generate_answer(message, history):
        assert message == "Ola, chatbot"
        assert history[-1] == {"role": "user", "content": "Ola, chatbot"}
        return "Resposta gerada pelo LLM"

    monkeypatch.setattr("app.routes.chat.generate_answer", fake_generate_answer)

    session_response = client.post("/api/sessions")
    session_id = session_response.json()["session_id"]

    chat_response = client.post(
        "/api/chat",
        json={"session_id": session_id, "message": "Ola, chatbot"},
    )

    assert chat_response.status_code == 200
    assert chat_response.json() == {
        "session_id": session_id,
        "response": "Resposta gerada pelo LLM",
    }
    assert sessions[session_id]["messages"] == [
        {"role": "user", "content": "Ola, chatbot"},
        {"role": "assistant", "content": "Resposta gerada pelo LLM"},
    ]
