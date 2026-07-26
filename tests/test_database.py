import sqlite3

import pytest

from database.connection import get_connection
from database.seed import seed_database


def test_seed_creates_expected_data(tmp_path):
    path = str(tmp_path / "seed.db")
    seed_database(path)
    connection = get_connection(path)
    assert connection.execute("SELECT COUNT(*) FROM livro").fetchone()[0] == 4
    assert connection.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] == 2
    connection.close()


def test_seed_is_idempotent(tmp_path):
    path = str(tmp_path / "seed.db")
    seed_database(path)
    seed_database(path)
    connection = get_connection(path)
    assert connection.execute("SELECT COUNT(*) FROM livro").fetchone()[0] == 4
    connection.close()


def test_database_constraints_are_enforced(connection):
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("INSERT INTO livro VALUES ('bad', 'x', 'y', 'bad-isbn', -1)")
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("INSERT INTO usuario VALUES ('u', 'x', 'x@example.com', 'hash', 'unknown')")
