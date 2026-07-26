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
        books = (
            ("livro-001", "Volta ao Mundo em 80 Dias", "Julio Verne", "isbn-001", 2),
            ("livro-002", "Dom Casmurro", "Machado de Assis", "isbn-002", 2),
            ("livro-003", "O Hobbit", "J.R.R. Tolkien", "isbn-003", 2),
            ("livro-004", "Ideias Têm Consequências", "Richard Weaver", "isbn-004", 2),
        )
        for book_id, titulo, autor, isbn, copias in books:
            connection.execute(
                "INSERT INTO livro(id, titulo, autor, isbn, copias_disponiveis) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET titulo=excluded.titulo, autor=excluded.autor, isbn=excluded.isbn, copias_disponiveis=excluded.copias_disponiveis",
                (book_id, titulo, autor, isbn, copias),
            )
        users = (("usuario-001", "Admin", "admin@gmail.com"), ("usuario-002", "Bruno", "bruno@example.com"))
        for user_id, name, email in users:
            senha = "admin" if email == "admin@gmail.com" else "senha123"
            connection.execute(
                "INSERT INTO usuario(id, nome, email, senha_hash, status) VALUES (?, ?, ?, ?, 'ativo') "
                "ON CONFLICT(id) DO UPDATE SET nome=excluded.nome, email=excluded.email, senha_hash=excluded.senha_hash",
                (user_id, name, email, hash_password(senha)),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    seed_database(str(Path("biblioteca.db")))
