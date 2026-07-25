"""Serviço remoto de catálogo de livros."""

from __future__ import annotations

from typing import Any

from database.connection import get_connection
from orb_core.exceptions import ObjectNotFoundError


class LivroService:
    """Consulta catálogo e disponibilidade em SQLite."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def listarLivros(self) -> list[dict[str, Any]]:
        """Retorna o catálogo ordenado pelo identificador."""
        connection = get_connection(self.db_path)
        try:
            rows = connection.execute("SELECT id, titulo, autor, isbn, copias_disponiveis FROM livro ORDER BY id").fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()

    def consultarLivro(self, livro_id: str) -> dict[str, Any]:
        """Retorna os dados completos de um livro."""
        connection = get_connection(self.db_path)
        try:
            row = connection.execute("SELECT id, titulo, autor, isbn, copias_disponiveis FROM livro WHERE id = ?", (livro_id,)).fetchone()
            if row is None:
                raise ObjectNotFoundError(f"Livro '{livro_id}' não encontrado")
            return dict(row)
        finally:
            connection.close()

    def consultarDisponibilidade(self, livro_id: str) -> dict[str, Any]:
        """Retorna disponibilidade e quantidade de cópias."""
        connection = get_connection(self.db_path)
        try:
            row = connection.execute("SELECT copias_disponiveis FROM livro WHERE id = ?", (livro_id,)).fetchone()
            if row is None:
                raise ObjectNotFoundError(f"Livro '{livro_id}' não encontrado")
            copies = int(row["copias_disponiveis"])
            return {"disponivel": copies > 0, "copias": copies}
        finally:
            connection.close()

    def adicionarLivro(self, livro_id: str, titulo: str, autor: str, isbn: str, copias: int) -> dict[str, Any]:
        """Adiciona um novo livro ao catálogo."""
        connection = get_connection(self.db_path)
        try:
            connection.execute(
                "INSERT INTO livro(id, titulo, autor, isbn, copias_disponiveis) VALUES (?, ?, ?, ?, ?)",
                (livro_id, titulo, autor, isbn, copias)
            )
            connection.commit()
            return {"status": "success", "id": livro_id}
        except Exception as exc:
            connection.rollback()
            raise exc
        finally:
            connection.close()

    def excluirLivro(self, livro_id: str) -> dict[str, Any]:
        """Exclui um livro do catálogo pelo ID."""
        connection = get_connection(self.db_path)
        try:
            row = connection.execute("SELECT id FROM livro WHERE id = ?", (livro_id,)).fetchone()
            if row is None:
                raise ObjectNotFoundError(f"Livro '{livro_id}' não encontrado")
            connection.execute("DELETE FROM livro WHERE id = ?", (livro_id,))
            connection.commit()
            return {"status": "success", "message": f"Livro {livro_id} excluído com sucesso."}
        except Exception as exc:
            connection.rollback()
            raise exc
        finally:
            connection.close()

