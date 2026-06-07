import os
import sqlite3
from threading import Lock
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_URL = "sqlite:///./data/app.sqlite3"
DATABASE_LOCK = Lock()
_DATABASE_INITIALIZED = False

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid_client TEXT NOT NULL,
    uuid_session TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid_client TEXT NOT NULL,
    uuid_session TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    mensagem TEXT NOT NULL
);
"""


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_database_path(database_url: str | None = None) -> Path:
    url = database_url or get_database_url()

    if not url.startswith("sqlite:///"):
        raise ValueError("DATABASE_URL deve usar SQLite. Exemplo: sqlite:///./data/app.sqlite3")

    raw_path = url.removeprefix("sqlite:///")
    database_path = Path(raw_path)

    if not database_path.is_absolute():
        database_path = PROJECT_ROOT / database_path

    return database_path


def get_connection() -> sqlite3.Connection:
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path, check_same_thread=False, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 30000")
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database() -> None:
    global _DATABASE_INITIALIZED

    if _DATABASE_INITIALIZED:
        return

    with DATABASE_LOCK:
        if _DATABASE_INITIALIZED:
            return

        with get_connection() as connection:
            connection.executescript(SCHEMA_SQL)

        _DATABASE_INITIALIZED = True


if __name__ == "__main__":
    initialize_database()
