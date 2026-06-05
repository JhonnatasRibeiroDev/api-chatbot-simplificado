from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

from fastapi.testclient import TestClient

from app.main import app
from app.services.session_service import sessions


def test_chat_route_handles_concurrent_requests(monkeypatch):
    sessions.clear()

    def fake_generate_answer(message, history):
        sleep(0.05)
        assert history[-1] == {"role": "user", "content": message}
        return f"Resposta para {message}"

    monkeypatch.setattr("app.routes.chat.generate_answer", fake_generate_answer)

    client = TestClient(app)
    requests_count = 10
    session_ids = [
        client.post("/api/sessions").json()["session_id"]
        for _ in range(requests_count)
    ]

    def send_message(index):
        response = client.post(
            "/api/chat",
            json={
                "session_id": session_ids[index],
                "message": f"Mensagem {index}",
            },
        )
        return index, response

    with ThreadPoolExecutor(max_workers=requests_count) as executor:
        futures = [
            executor.submit(send_message, index)
            for index in range(requests_count)
        ]
        results = [future.result() for future in as_completed(futures)]

    assert len(results) == requests_count

    for index, response in results:
        session_id = session_ids[index]
        message = f"Mensagem {index}"
        assistant_response = f"Resposta para {message}"

        assert response.status_code == 200
        assert response.json() == {
            "session_id": session_id,
            "response": assistant_response,
        }
        assert sessions[session_id]["messages"] == [
            {"role": "user", "content": message},
            {"role": "assistant", "content": assistant_response},
        ]
