from app.database import DATABASE_LOCK, get_connection, initialize_database


def create_message(uuid_client: str, uuid_session: str, role: str, mensagem: str) -> None:
    initialize_database()

    with DATABASE_LOCK:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO messages (uuid_client, uuid_session, role, mensagem)
                VALUES (?, ?, ?, ?)
                """,
                (uuid_client, uuid_session, role, mensagem),
            )


def get_messages_by_session(uuid_session: str) -> list[dict]:
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT role, mensagem
            FROM messages
            WHERE uuid_session = ?
            ORDER BY id
            """,
            (uuid_session,),
        ).fetchall()

    return [
        {
            "role": row["role"],
            "content": row["mensagem"],
        }
        for row in rows
    ]
