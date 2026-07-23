import pytest

from database.connection import get_connection
from domain.emprestimo_service import EmprestimoService
from orb_core.exceptions import ObjectNotFoundError


def test_missing_loan_does_not_change_books(database_path):
    service = EmprestimoService(database_path)
    with pytest.raises(ObjectNotFoundError):
        service.devolverLivro("missing-loan")
    connection = get_connection(database_path)
    assert connection.execute("SELECT copias_disponiveis FROM livro WHERE id = 'livro-001'").fetchone()[0] == 2
    connection.close()
