"""Processo TCP separado do Naming Service."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from orb_core.logging_config import configure_logging
from orb_core.registry import Endpoint, Registry
from orb_core.serializer import deserialize_stream, write_message

logger = logging.getLogger(__name__)


class RegistryServer:
    """Expõe registro, resolução e listagem via TCP."""

    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()
        configure_logging()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Processa uma operação do Registry."""
        try:
            request = await deserialize_stream(reader)
            operation = request.get("operation")
            if operation == "register":
                endpoint = self.registry.registrar(request["object_id"], request["host"], int(request["port"]), request.get("node_id", ""))
                response = {"status": "OK", "endpoint": endpoint.__dict__}
            elif operation == "resolve":
                endpoint = self.registry.resolver(request["object_id"])
                response = {"status": "OK", "endpoint": endpoint.__dict__}
            elif operation == "list":
                response = {"status": "OK", "nodes": self.registry.listar()}
            else:
                response = {"status": "ERROR", "message": "Operação desconhecida"}
        except Exception as exc:  # noqa: BLE001 - fronteira TCP deve responder erro
            response = {"status": "ERROR", "message": str(exc)}
        try:
            await write_message(writer, response)
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self, host: str, port: int) -> asyncio.AbstractServer:
        """Inicia o Registry Service."""
        return await asyncio.start_server(self.handle_connection, host, port)


async def main() -> None:
    """Executa o Registry Service até interrupção."""
    server = await RegistryServer().start("0.0.0.0", 8765)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
