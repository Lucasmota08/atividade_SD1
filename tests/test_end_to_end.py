import asyncio

from database.seed import seed_database
from domain.emprestimo_service import EmprestimoService
from domain.livro_service import LivroService
from domain.usuario_service import UsuarioService
from orb_core.broker import Broker
from orb_core.stub import Stub


def test_end_to_end_remote_library_flow(tmp_path):
    async def scenario():
        path = str(tmp_path / "e2e.db")
        seed_database(path)
        broker = Broker({
            "LivroService": LivroService(path),
            "UsuarioService": UsuarioService(path),
            "EmprestimoService": EmprestimoService(path),
        })
        server = await broker.start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            user = Stub("UsuarioService", "127.0.0.1", port)
            token = await user.invoke_async("autenticar", "ana@example.com", "senha123")
            books = Stub("LivroService", "127.0.0.1", port)
            catalog = await books.invoke_async("listarLivros", auth_token=token)
            loan_stub = Stub("EmprestimoService", "127.0.0.1", port)
            loan = await loan_stub.invoke_async("emprestarLivro", "usuario-001", catalog[0]["id"], auth_token=token)
            active = await loan_stub.invoke_async("listarEmprestimosAtivos", "usuario-001", auth_token=token)
            assert active[0]["id"] == loan["id"]
            await loan_stub.invoke_async("devolverLivro", loan["id"], auth_token=token)
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
