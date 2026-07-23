"""Fixtures compartilhadas dos testes."""

from __future__ import annotations

import asyncio

import pytest

from database.connection import get_connection
from database.seed import seed_database


@pytest.fixture
def database_path(tmp_path):
    """Fornece um banco temporário com dados de demonstração."""
    path = str(tmp_path / "test.db")
    seed_database(path)
    return path


@pytest.fixture
def connection(database_path):
    """Fornece conexão SQLite isolada por teste."""
    conn = get_connection(database_path)
    yield conn
    conn.close()


@pytest.fixture
def event_loop():
    """Cria e encerra um event loop isolado."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
