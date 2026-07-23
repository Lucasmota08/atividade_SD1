from datetime import datetime, timedelta, timezone

import jwt
import pytest

from orb_core.auth import gerar_token, validar_token
from orb_core.exceptions import AuthenticationError


def test_valid_token_has_user_claim(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    token = gerar_token("user-1")
    assert validar_token(token)["sub"] == "user-1"


def test_missing_token_is_rejected():
    with pytest.raises(AuthenticationError) as error:
        validar_token(None)
    assert error.value.code == "AUTH_INVALID"


def test_invalid_signature_is_rejected(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    token = jwt.encode({"sub": "user-1", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}, "other", algorithm="HS256")
    with pytest.raises(AuthenticationError):
        validar_token(token)


def test_expired_token_is_rejected(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    token = jwt.encode({"sub": "user-1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, "test-secret", algorithm="HS256")
    with pytest.raises(AuthenticationError):
        validar_token(token)
