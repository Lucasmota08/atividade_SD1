from orb_core.exceptions import (
    AuthenticationError,
    MethodNotFoundError,
    ObjectNotFoundError,
    ORBConnectionRefusedError,
    ORBError,
    ORBSerializationError,
    ORBTimeoutError,
)


def test_custom_exceptions_have_standard_codes():
    errors = (
        (ORBTimeoutError, "TIMEOUT"),
        (ORBConnectionRefusedError, "CONNECTION_REFUSED"),
        (ORBSerializationError, "SERIALIZATION_ERROR"),
        (ObjectNotFoundError, "OBJECT_NOT_FOUND"),
        (MethodNotFoundError, "METHOD_NOT_FOUND"),
        (AuthenticationError, "AUTH_INVALID"),
    )
    for error_type, code in errors:
        error = error_type("falha")
        assert isinstance(error, ORBError)
        assert error.code == code
        assert str(error) == "falha"
