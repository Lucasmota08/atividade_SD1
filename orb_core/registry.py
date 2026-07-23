"""Registry local e cliente TCP do Naming Service."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from .exceptions import ObjectNotFoundError, ORBConnectionRefusedError, ORBTimeoutError
from .serializer import deserialize_stream, write_message


@dataclass(frozen=True)
class Endpoint:
    """Localização de uma instância de objeto remoto."""

    object_id: str
    host: str
    port: int
    node_id: str = ""


class Registry:
    """Registry em memória com resolução round-robin."""

    def __init__(self) -> None:
        self._entries: dict[str, list[Endpoint]] = defaultdict(list)
        self._cursors: dict[str, int] = defaultdict(int)

    def registrar(self, object_id: str, host: str, port: int, node_id: str = "") -> Endpoint:
        """Registra uma instância sem duplicar o mesmo endpoint."""
        endpoint = Endpoint(object_id, host, int(port), node_id)
        if endpoint not in self._entries[object_id]:
            self._entries[object_id].append(endpoint)
        return endpoint

    def resolver(self, object_id: str) -> Endpoint:
        """Retorna a próxima instância pelo algoritmo round-robin."""
        entries = self._entries.get(object_id, [])
        if not entries:
            raise ObjectNotFoundError(f"Objeto '{object_id}' não está registrado")
        index = self._cursors[object_id] % len(entries)
        self._cursors[object_id] = index + 1
        return entries[index]

    def listar(self) -> list[dict[str, Any]]:
        """Retorna os endpoints conhecidos para observabilidade."""
        return [asdict(endpoint) for values in self._entries.values() for endpoint in values]


class RegistryClient:
    """Cliente asyncio para o Registry Service separado."""

    def __init__(self, host: str, port: int, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    async def _request(self, message: dict[str, Any]) -> dict[str, Any]:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), self.timeout)
        except asyncio.TimeoutError as exc:
            raise ORBTimeoutError("Registry excedeu o timeout") from exc
        except OSError as exc:
            raise ORBConnectionRefusedError("Registry indisponível") from exc
        try:
            await asyncio.wait_for(write_message(writer, message), self.timeout)
            return await asyncio.wait_for(deserialize_stream(reader), self.timeout)
        except asyncio.TimeoutError as exc:
            raise ORBTimeoutError("Registry excedeu o timeout") from exc
        except (ConnectionError, OSError) as exc:
            raise ORBConnectionRefusedError("Conexão com Registry encerrada") from exc
        finally:
            writer.close()
            await writer.wait_closed()

    async def register(self, endpoint: Endpoint) -> Endpoint:
        """Registra endpoint no serviço remoto."""
        response = await self._request({"operation": "register", **asdict(endpoint)})
        if response.get("status") != "OK":
            raise ObjectNotFoundError(response.get("message", "Falha no registro"))
        return endpoint

    async def resolve(self, object_id: str) -> Endpoint:
        """Resolve um objeto no serviço remoto."""
        response = await self._request({"operation": "resolve", "object_id": object_id})
        if response.get("status") != "OK":
            raise ObjectNotFoundError(response.get("message", "Objeto não encontrado"))
        return Endpoint(**response["endpoint"])

    async def list_nodes(self) -> list[dict[str, Any]]:
        """Lista endpoints registrados para a API administrativa."""
        response = await self._request({"operation": "list"})
        if response.get("status") != "OK":
            raise ObjectNotFoundError(response.get("message", "Registry indisponível"))
        return response.get("nodes", [])
