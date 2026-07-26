import pytest

from database.connection import get_connection
from domain.emprestimo_service import EmprestimoService
from orb_core.exceptions import ORBError


def test_return_restores_stock_once(database_path):
    service = EmprestimoService(database_path)
    loan = service.emprestarLivro("usuario-001", "livro-001")
    result = service.devolverLivro(loan["id"])
    assert result["status"] == "devolvido"
    with pytest.raises(ORBError) as error:
        service.devolverLivro(loan["id"])
    assert error.value.code == "LOAN_ALREADY_RETURNED"
    connection = get_connection(database_path)
    assert connection.execute("SELECT copias_disponiveis FROM livro WHERE id = 'livro-001'").fetchone()[0] == 2
    connection.close()


def test_cannot_return_other_user_loan(database_path):
    service = EmprestimoService(database_path)
    loan = service.emprestarLivro("usuario-001", "livro-001")
    with pytest.raises(ORBError) as error:
        service.devolverLivro(loan["id"], usuario_id="usuario-002")
    assert error.value.code == "LOAN_NOT_OWNED"

