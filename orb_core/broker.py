"""ORB Core: recebe, autentica e despacha invocações remotas."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from .auth import validar_token
from .exceptions import AuthenticationError, ORBError, ORBSerializationError, ObjectNotFoundError
from .logging_config import configure_logging
from .serializer import deserialize_stream, write_message
from .skeleton import Skeleton

logger = logging.getLogger(__name__)


class Broker:
    """Servidor asyncio que expõe objetos de domínio por object_id."""

    def __init__(self, objects: dict[str, object] | None = None, protected_methods: set[str] | None = None) -> None:
        self.objects = objects or {}
        self.protected_methods = protected_methods or {
            "cadastrarUsuario",
            "consultarUsuario",
            "emprestarLivro",
            "devolverLivro",
            "listarEmprestimosAtivos",
            "consultarDisponibilidade",
            "listarLivros",
            "adicionarLivro",
            "excluirLivro",
        }
        self.skeleton = Skeleton()
        configure_logging()

    def register_local_object(self, object_id: str, instance: object) -> None:
        """Registra um objeto local para dispatch."""
        self.objects[object_id] = instance

    @staticmethod
    def _response(request_id: str, status: str, result: Any = None, error: dict[str, str] | None = None) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        return {"request_id": request_id, "timestamp": timestamp, "status": status, "result": result, "error": error}

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Processa uma conexão isoladamente e devolve uma resposta."""
        request_id = "-"
        try:
            request = await deserialize_stream(reader)
            request_id = str(request.get("request_id", "-"))
            object_id = request.get("object_id")
            method = request.get("method")
            if not isinstance(object_id, str) or not isinstance(method, str):
                raise ORBSerializationError("object_id e method são obrigatórios")
            if method in self.protected_methods:
                validar_token(request.get("auth_token"))
            instance = self.objects.get(object_id)
            if instance is None:
                raise ObjectNotFoundError(f"Objeto '{object_id}' não encontrado")
            logger.info("Dispatch %s.%s", object_id, method, extra={"component": "ORBCore", "request_id": request_id})
            result = await self.skeleton.dispatch(instance, method, request.get("args", []), request.get("kwargs", {}))
            response = self._response(request_id, "OK", result=result)
        except ORBError as exc:
            response = self._response(request_id, "ERROR", error={"code": exc.code, "message": exc.message})
        except Exception as exc:  # noqa: BLE001 - fronteira do servidor converte falhas inesperadas
            logger.exception("Erro interno no dispatch", extra={"component": "ORBCore", "request_id": request_id})
            response = self._response(request_id, "ERROR", error={"code": "INTERNAL_ERROR", "message": str(exc)})
        try:
            await write_message(writer, response)
        except (ConnectionError, OSError):
            logger.warning("Cliente desconectou antes da resposta", extra={"component": "ORBCore", "request_id": request_id})
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self, host: str, port: int) -> asyncio.AbstractServer:
        """Inicia o servidor TCP do Broker."""
        return await asyncio.start_server(self.handle_connection, host, port)
