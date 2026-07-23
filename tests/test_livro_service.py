import pytest

from domain.livro_service import LivroService
from orb_core.exceptions import ObjectNotFoundError


def test_book_availability_and_missing_book(database_path):
    service = LivroService(database_path)
    assert service.consultarDisponibilidade("livro-001") == {"disponivel": True, "copias": 2}
    with pytest.raises(ObjectNotFoundError):
        service.consultarDisponibilidade("missing")


def test_book_listing_can_be_empty(tmp_path):
    from database.connection import get_connection
    path = str(tmp_path / "empty.db")
    get_connection(path).close()
    assert LivroService(path).listarLivros() == []
