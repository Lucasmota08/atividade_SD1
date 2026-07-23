"""Dispatch seguro de métodos em objetos locais do servidor."""

from __future__ import annotations

import inspect
from typing import Any

from .exceptions import MethodNotFoundError


async def dispatch(instance: object, method: str, args: list[Any], kwargs: dict[str, Any]) -> Any:
    """Executa somente um método público exposto no objeto."""
    if not method or method.startswith("_"):
        raise MethodNotFoundError(f"Método '{method}' não está exposto")
    target = getattr(instance, method, None)
    if target is None or not callable(target):
        raise MethodNotFoundError(f"Método '{method}' não encontrado")
    result = target(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


class Skeleton:
    """Adaptador orientado a objeto para dispatch de Skeleton."""

    async def dispatch(self, instance: object, method: str, args: list[Any], kwargs: dict[str, Any]) -> Any:
        """Encaminha a chamada para o objeto de domínio."""
        return await dispatch(instance, method, args, kwargs)
