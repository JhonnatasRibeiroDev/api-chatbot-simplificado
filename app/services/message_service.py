from app.repositories.messages_repository import create_message, get_messages_by_session


DEFAULT_UUID_CLIENT = "default-client"


def save_message(uuid_session: str, role: str, content: str, uuid_client: str = DEFAULT_UUID_CLIENT) -> None:
    create_message(
        uuid_client=uuid_client,
        uuid_session=uuid_session,
        role=role,
        mensagem=content,
    )


def get_session_messages(uuid_session: str) -> list[dict]:
    return get_messages_by_session(uuid_session)
