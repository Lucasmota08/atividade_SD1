"""Carga dados determinísticos para a demonstração local."""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from pathlib import Path

from .connection import get_connection


def hash_password(password: str) -> str:
    """Cria hash determinístico de senha usando a stdlib."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def seed_database(db_path: str) -> None:
    """Insere cinco livros e dois usuários sem duplicação."""
    connection = get_connection(db_path)
    try:
        connection.execute("BEGIN")
        for index in range(1, 6):
            connection.execute(
                "INSERT OR IGNORE INTO livro(id, titulo, autor, isbn, copias_disponiveis) VALUES (?, ?, ?, ?, ?)",
                (f"livro-{index:03d}", f"Livro de Demonstração {index}", "Autor ORB", f"isbn-{index:03d}", 2),
            )
        users = (("usuario-001", "Ana", "ana@example.com"), ("usuario-002", "Bruno", "bruno@example.com"))
        for user_id, name, email in users:
            connection.execute(
                "INSERT OR IGNORE INTO usuario(id, nome, email, senha_hash, status) VALUES (?, ?, ?, ?, 'ativo')",
                (user_id, name, email, hash_password("senha123")),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    seed_database(str(Path("biblioteca.db")))
