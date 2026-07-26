"""Serviço remoto de usuários da Biblioteca Digital."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from typing import Any

from orb_core.auth import gerar_token
from orb_core.exceptions import AuthenticationError, ORBError, ObjectNotFoundError

from database.connection import get_connection


class UsuarioService:
    """Implementa cadastro e autenticação persistentes."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def cadastrarUsuario(self, nome: str, email: str, senha: str) -> dict[str, Any]:
        """Cadastra um usuário ativo e não retorna sua senha."""
        connection = get_connection(self.db_path)
        try:
            connection.execute("BEGIN")
            cursor = connection.execute("SELECT id FROM usuario WHERE id LIKE 'usuario-%'")
            existing_nums = []
            for row in cursor.fetchall():
                parts = str(row["id"]).split("-")
                if len(parts) == 2 and parts[1].isdigit():
                    existing_nums.append(int(parts[1]))
            next_num = max(existing_nums, default=0) + 1
            user_id = f"usuario-{next_num:03d}"

            connection.execute(
                "INSERT INTO usuario(id, nome, email, senha_hash, status) VALUES (?, ?, ?, ?, 'ativo')",
                (user_id, nome, email, self._hash(senha)),
            )
            connection.commit()
            return {"id": user_id, "nome": nome, "email": email, "status": "ativo"}
        except Exception as exc:
            connection.rollback()
            if "UNIQUE" in str(exc).upper():
                raise ORBError("Email já cadastrado", code="USER_ALREADY_EXISTS") from exc
            raise
        finally:
            connection.close()

    def consultarUsuario(self, usuario_id: str) -> dict[str, Any]:
        """Consulta um usuário sem expor o hash da senha."""
        connection = get_connection(self.db_path)
        try:
            row = connection.execute("SELECT id, nome, email, status FROM usuario WHERE id = ?", (usuario_id,)).fetchone()
            if row is None:
                raise ObjectNotFoundError(f"Usuário '{usuario_id}' não encontrado")
            return dict(row)
        finally:
            connection.close()

    def autenticar(self, email: str, senha: str) -> dict[str, str]:
        """Valida credenciais e emite token JWT e ID do usuário."""
        connection = get_connection(self.db_path)
        try:
            row = connection.execute("SELECT id, senha_hash, status FROM usuario WHERE email = ?", (email,)).fetchone()
            if row is None or row["status"] != "ativo" or not hmac.compare_digest(row["senha_hash"], self._hash(senha)):
                raise AuthenticationError("Email ou senha inválidos")
            return {"token": gerar_token(row["id"]), "usuario_id": row["id"]}
        finally:
            connection.close()

    def listarUsuarios(self) -> list[dict[str, Any]]:
        """Lista todos os usuários cadastrados sem expor o hash da senha."""
        connection = get_connection(self.db_path)
        try:
            cursor = connection.execute("SELECT id, nome, email, status FROM usuario")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            connection.close()

