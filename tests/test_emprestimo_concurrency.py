from domain.emprestimo_service import EmprestimoService


def test_multiple_loans_never_make_stock_negative(database_path):
    service = EmprestimoService(database_path)
    first = service.emprestarLivro("usuario-001", "livro-001")
    second = service.emprestarLivro("usuario-002", "livro-001")
    assert first["status"] == second["status"] == "ativo"
    from database.connection import get_connection
    connection = get_connection(database_path)
    assert connection.execute("SELECT copias_disponiveis FROM livro WHERE id = 'livro-001'").fetchone()[0] == 0
    connection.close()
