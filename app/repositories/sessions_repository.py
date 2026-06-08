from app.database import DATABASE_LOCK, get_connection, initialize_database


def create_session_record(uuid_client: str, uuid_session: str) -> None:
    initialize_database()

    with DATABASE_LOCK:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO sessions (uuid_client, uuid_session)
                VALUES (?, ?)
                """,
                (uuid_client, uuid_session),
            )


def session_record_exists(uuid_session: str) -> bool:
    initialize_database()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM sessions
            WHERE uuid_session = ?
            LIMIT 1
            """,
            (uuid_session,),
        ).fetchone()

    return row is not None


def get_client_by_session(uuid_session: str) -> str | None:
    initialize_database()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT uuid_client
            FROM sessions
            WHERE uuid_session = ?
            LIMIT 1
            """,
            (uuid_session,),
        ).fetchone()

    if row is None:
        return None

    return row["uuid_client"]


def get_sessions_by_client(uuid_client: str) -> list[dict]:
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT uuid_session, created_at
            FROM sessions
            WHERE uuid_client = ?
            ORDER BY created_at DESC, id DESC
            """,
            (uuid_client,),
        ).fetchall()

    return [
        {
            "session_id": row["uuid_session"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
