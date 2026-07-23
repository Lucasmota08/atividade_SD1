"""Inicialização compartilhada dos nós ORB."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from database.seed import seed_database
from domain.emprestimo_service import EmprestimoService
from domain.livro_service import LivroService
from domain.usuario_service import UsuarioService
from orb_core.broker import Broker
from orb_core.registry import Endpoint, RegistryClient


async def run_node(
    node_id: str,
    bind_host: str,
    port: int,
    db_path: str,
    registry_host: str,
    registry_port: int,
    advertise_host: str | None = None,
) -> None:
    """Sobe um nó, seus serviços e registra os objetos remotos."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    seed_database(db_path)
    broker = Broker()
    broker.register_local_object("LivroService", LivroService(db_path))
    broker.register_local_object("UsuarioService", UsuarioService(db_path))
    broker.register_local_object("EmprestimoService", EmprestimoService(db_path))
    server = await broker.start(bind_host, port)
    registry = RegistryClient(registry_host, registry_port)
    for object_id in broker.objects:
        endpoint = Endpoint(object_id, advertise_host or bind_host, port, node_id)
        for attempt in range(5):
            try:
                await registry.register(endpoint)
                break
            except Exception:
                if attempt == 4:
                    raise
                await asyncio.sleep(1)
    async with server:
        await server.serve_forever()
