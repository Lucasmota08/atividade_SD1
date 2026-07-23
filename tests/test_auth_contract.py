from domain.usuario_service import UsuarioService
from orb_core.auth import validar_token


def test_auth_service_returns_valid_jwt(database_path):
    token = UsuarioService(database_path).autenticar("ana@example.com", "senha123")
    assert validar_token(token)["sub"] == "usuario-001"
