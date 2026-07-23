"""Stub cliente para invocação remota síncrona ou assíncrona."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from .exceptions import ORBConnectionRefusedError, ORBError, ORBSerializationError, ORBTimeoutError
from .logging_config import configure_logging
from .registry import Endpoint, RegistryClient
from .serializer import deserialize_stream, write_message

logger = logging.getLogger(__name__)


class Stub:
    """Proxy de objeto remoto com retry e failover."""

    def __init__(self, object_id: str, host: str | None = None, port: int | None = None, timeout: float = 5.0, registry: RegistryClient | None = None) -> None:
        self.object_id = object_id
        self.host = host
        self.port = port
        self.timeout = timeout
        self.registry = registry
        configure_logging()

    async def invoke_async(self, method: str, *args: Any, auth_token: str | None = None, **kwargs: Any) -> Any:
        """Invoca o método remoto com até três tentativas."""
        request_id = str(uuid.uuid4())
        last_error: ORBError | None = None
        for attempt in range(3):
            try:
                endpoint = await self._endpoint()
                return await self._invoke_endpoint(endpoint, request_id, method, args, kwargs, auth_token)
            except (ORBConnectionRefusedError, ORBTimeoutError, ORBSerializationError) as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep((0.5, 1.0, 2.0)[attempt])
        assert last_error is not None
        raise last_error

    def invoke(self, method: str, *args: Any, auth_token: str | None = None, **kwargs: Any) -> Any:
        """Invoca o método remoto a partir de código síncrono."""
        return asyncio.run(self.invoke_async(method, *args, auth_token=auth_token, **kwargs))

    async def _endpoint(self) -> Endpoint:
        if self.registry is not None:
            return await self.registry.resolve(self.object_id)
        if self.host is None or self.port is None:
            raise ORBConnectionRefusedError("Nenhum endpoint foi configurado")
        return Endpoint(self.object_id, self.host, self.port)

    async def _invoke_endpoint(self, endpoint: Endpoint, request_id: str, method: str, args: tuple[Any, ...], kwargs: dict[str, Any], auth_token: str | None) -> Any:
        request = {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "object_id": self.object_id,
            "method": method,
            "args": list(args),
            "kwargs": kwargs,
            "auth_token": auth_token,
        }
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(endpoint.host, endpoint.port), self.timeout)
        except asyncio.TimeoutError as exc:
            raise ORBTimeoutError("Servidor não respondeu no timeout configurado") from exc
        except OSError as exc:
            raise ORBConnectionRefusedError("Nó de servidor inacessível") from exc
        try:
            await asyncio.wait_for(write_message(writer, request), self.timeout)
            response = await asyncio.wait_for(deserialize_stream(reader), self.timeout)
        except asyncio.TimeoutError as exc:
            raise ORBTimeoutError("Servidor não respondeu no timeout configurado") from exc
        except ORBSerializationError:
            raise
        except (ConnectionError, OSError) as exc:
            raise ORBConnectionRefusedError("Conexão encerrada pelo servidor") from exc
        finally:
            writer.close()
            await writer.wait_closed()
        if response.get("request_id") != request_id:
            raise ORBSerializationError("request_id da resposta não corresponde à requisição")
        if response.get("status") == "OK":
            return response.get("result")
        error = response.get("error") or {}
        code = error.get("code", "INTERNAL_ERROR")
        message = error.get("message", "Falha remota")
        error_type = {"TIMEOUT": ORBTimeoutError, "CONNECTION_REFUSED": ORBConnectionRefusedError, "SERIALIZATION_ERROR": ORBSerializationError}.get(code, ORBError)
        raise error_type(message, code=code)
