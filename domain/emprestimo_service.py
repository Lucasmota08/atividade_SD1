"""Serviço remoto de empréstimos e devoluções."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from database.connection import get_connection
from orb_core.exceptions import ORBError, ObjectNotFoundError


class EmprestimoService:
    """Implementa transições atômicas de empréstimo."""

    def __init__(self, db_path: str, loan_days: int = 14) -> None:
        self.db_path = db_path
        self.loan_days = loan_days

    def emprestarLivro(self, usuario_id: str, livro_id: str) -> dict[str, Any]:
        """Cria empréstimo ativo e decrementa estoque atomicamente."""
        now = datetime.now(timezone.utc)
        due = now + timedelta(days=self.loan_days)
        connection = get_connection(self.db_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            user = connection.execute("SELECT status FROM usuario WHERE id = ?", (usuario_id,)).fetchone()
            if user is None:
                raise ObjectNotFoundError(f"Usuário '{usuario_id}' não encontrado")
            if user["status"] != "ativo":
                raise ORBError("Usuário bloqueado", code="USER_BLOCKED")
            updated = connection.execute(
                "UPDATE livro SET copias_disponiveis = copias_disponiveis - 1 WHERE id = ? AND copias_disponiveis > 0",
                (livro_id,),
            )
            if updated.rowcount == 0:
                exists = connection.execute("SELECT 1 FROM livro WHERE id = ?", (livro_id,)).fetchone()
                if exists is None:
                    raise ObjectNotFoundError(f"Livro '{livro_id}' não encontrado")
                raise ORBError("Não há cópias disponíveis", code="SEM_COPIAS_DISPONIVEIS")
            loan = {
                "id": str(uuid.uuid4()),
                "livro_id": livro_id,
                "usuario_id": usuario_id,
                "data_emprestimo": now.isoformat(),
                "data_devolucao_prevista": due.isoformat(),
                "status": "ativo",
            }
            connection.execute(
                "INSERT INTO emprestimo(id, livro_id, usuario_id, data_emprestimo, data_devolucao_prevista, status) VALUES (?, ?, ?, ?, ?, ?)",
                tuple(loan.values()),
            )
            connection.commit()
            return loan
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def devolverLivro(self, emprestimo_id: str, usuario_id: str | None = None) -> dict[str, Any]:
        """Marca empréstimo como devolvido e restaura estoque uma vez, validando titular se informado."""
        connection = get_connection(self.db_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            loan = connection.execute("SELECT * FROM emprestimo WHERE id = ?", (emprestimo_id,)).fetchone()
            if loan is None:
                raise ObjectNotFoundError(f"Empréstimo '{emprestimo_id}' não encontrado")
            if usuario_id and loan["usuario_id"] != usuario_id:
                raise ORBError("Este empréstimo não pertence a este usuário", code="LOAN_NOT_OWNED")
            if loan["status"] != "ativo":
                raise ORBError("Empréstimo já devolvido", code="LOAN_ALREADY_RETURNED")
            connection.execute("UPDATE emprestimo SET status = 'devolvido' WHERE id = ? AND status = 'ativo'", (emprestimo_id,))
            connection.execute("UPDATE livro SET copias_disponiveis = copias_disponiveis + 1 WHERE id = ?", (loan["livro_id"],))
            connection.commit()
            return {"emprestimo_id": emprestimo_id, "status": "devolvido"}
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def listarEmprestimosAtivos(self, usuario_id: str) -> list[dict[str, Any]]:
        """Lista empréstimos ativos de um usuário específico."""
        connection = get_connection(self.db_path)
        try:
            rows = connection.execute(
                "SELECT id, livro_id, usuario_id, data_emprestimo, data_devolucao_prevista, status FROM emprestimo WHERE usuario_id = ? AND status = 'ativo' ORDER BY data_emprestimo",
                (usuario_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()
