"""Utilitários de conexão e inicialização SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_connection(db_path: str) -> sqlite3.Connection:
    """Abre uma conexão SQLite com schema e foreign keys habilitados."""
    connection = sqlite3.connect(db_path, timeout=10.0, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))
    return connection
