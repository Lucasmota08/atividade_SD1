"""API administrativa FastAPI, sem invocações de domínio."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query

from orb_core.registry import RegistryClient

app = FastAPI(title="Biblioteca ORB Admin API", version="1.0.0")


def _registry() -> RegistryClient:
    return RegistryClient(os.getenv("REGISTRY_HOST", "127.0.0.1"), int(os.getenv("REGISTRY_PORT", "8765")))


@app.get("/health")
async def health() -> dict[str, Any]:
    """Retorna o estado da API e dos nós registrados."""
    try:
        nodes = await _registry().list_nodes()
        return {"status": "ok", "nodes": nodes}
    except Exception as exc:  # noqa: BLE001 - endpoint administrativo não vaza traceback
        return {"status": "degraded", "nodes": [], "error": str(exc)}


@app.get("/logs")
async def logs(limit: int = Query(100, ge=1, le=1000)) -> dict[str, Any]:
    """Retorna as últimas entradas do arquivo de log."""
    path = Path(os.getenv("LOG_FILE", "orb.log"))
    if not path.exists():
        return {"entries": [], "limit": limit}
    entries = path.read_text(encoding="utf-8").splitlines()
    return {"entries": entries[-limit:], "limit": limit}
