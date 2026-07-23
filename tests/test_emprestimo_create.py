import pytest

from database.connection import get_connection
from domain.emprestimo_service import EmprestimoService
from orb_core.exceptions import ORBError


def test_loan_decrements_stock_and_returns_active_loan(database_path):
    loan = EmprestimoService(database_path).emprestarLivro("usuario-001", "livro-001")
    assert loan["status"] == "ativo"
    connection = get_connection(database_path)
    assert connection.execute("SELECT copias_disponiveis FROM livro WHERE id = 'livro-001'").fetchone()[0] == 1
    connection.close()


def test_no_copies_is_a_business_error(database_path):
    connection = get_connection(database_path)
    connection.execute("UPDATE livro SET copias_disponiveis = 0 WHERE id = 'livro-001'")
    connection.close()
    with pytest.raises(ORBError) as error:
        EmprestimoService(database_path).emprestarLivro("usuario-001", "livro-001")
    assert error.value.code == "SEM_COPIAS_DISPONIVEIS"
