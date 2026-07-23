from domain.emprestimo_service import EmprestimoService


def test_active_loans_are_filtered_by_user(database_path):
    service = EmprestimoService(database_path)
    loan = service.emprestarLivro("usuario-001", "livro-001")
    assert service.listarEmprestimosAtivos("usuario-001")[0]["id"] == loan["id"]
    assert service.listarEmprestimosAtivos("usuario-002") == []
