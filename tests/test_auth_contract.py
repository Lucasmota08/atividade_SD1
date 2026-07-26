from domain.usuario_service import UsuarioService
from orb_core.auth import validar_token


def test_auth_service_returns_valid_jwt(database_path):
    res = UsuarioService(database_path).autenticar("admin@gmail.com", "admin")
    token = res["token"] if isinstance(res, dict) else res
    assert validar_token(token)["sub"] == "usuario-001"
