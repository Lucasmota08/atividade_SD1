import pytest

from database.seed import seed_database
from domain.usuario_service import UsuarioService
from orb_core.exceptions import AuthenticationError


def test_user_authentication_and_invalid_credentials(database_path):
    service = UsuarioService(database_path)
    token = service.autenticar("admin@gmail.com", "admin")
    assert isinstance(token, str)
    with pytest.raises(AuthenticationError):
        service.autenticar("admin@gmail.com", "wrong")


def test_user_registration_hides_password(database_path):
    service = UsuarioService(database_path)
    user = service.cadastrarUsuario("Clara", "clara@example.com", "secret")
    assert user["email"] == "clara@example.com"
    assert "senha_hash" not in user
