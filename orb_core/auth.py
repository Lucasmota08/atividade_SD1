"""Emissão e validação de tokens JWT."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from .exceptions import AuthenticationError

_ALGORITHM = "HS256"


def _secret() -> str:
    return os.getenv("JWT_SECRET", "local-compose-secret")


def gerar_token(usuario_id: str) -> str:
    """Gera um JWT com identificação do usuário e expiração configurável."""
    try:
        minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    except ValueError:
        minutes = 60
    now = datetime.now(timezone.utc)
    payload = {"sub": usuario_id, "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, _secret(), algorithm=_ALGORITHM)


def validar_token(token: str | None) -> dict[str, Any]:
    """Valida um JWT e retorna seus claims."""
    if not token:
        raise AuthenticationError("Token JWT ausente")
    try:
        claims = jwt.decode(token, _secret(), algorithms=[_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Token JWT inválido ou expirado") from exc
    if not claims.get("sub"):
        raise AuthenticationError("Token JWT sem usuário")
    return claims
