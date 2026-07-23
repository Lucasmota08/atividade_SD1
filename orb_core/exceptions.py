"""Exceções e códigos de erro do middleware ORB."""


class ORBError(Exception):
    """Erro base transportável do ORB."""

    code = "INTERNAL_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class ORBTimeoutError(ORBError):
    """Indica que uma chamada excedeu o timeout configurado."""

    code = "TIMEOUT"


class ORBConnectionRefusedError(ORBError):
    """Indica que nenhum nó aceitou a conexão."""

    code = "CONNECTION_REFUSED"


class ORBSerializationError(ORBError):
    """Indica framing ou payload JSON inválido."""

    code = "SERIALIZATION_ERROR"


class ObjectNotFoundError(ORBError):
    """Indica objeto remoto ou registro de domínio inexistente."""

    code = "OBJECT_NOT_FOUND"


class MethodNotFoundError(ORBError):
    """Indica método remoto não exposto pelo objeto."""

    code = "METHOD_NOT_FOUND"


class AuthenticationError(ORBError):
    """Indica credencial ou token JWT inválido."""

    code = "AUTH_INVALID"
