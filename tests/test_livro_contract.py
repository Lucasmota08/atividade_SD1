import asyncio

from database.seed import seed_database
from domain.livro_service import LivroService
from orb_core.auth import gerar_token
from orb_core.broker import Broker
from orb_core.stub import Stub


def test_availability_contract_shape(tmp_path):
    async def scenario():
        path = str(tmp_path / "book.db")
        seed_database(path)
        server = await Broker({"LivroService": LivroService(path)}).start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            result = await Stub("LivroService", "127.0.0.1", port).invoke_async("consultarDisponibilidade", "livro-001", auth_token=gerar_token("usuario-001"))
            assert isinstance(result["disponivel"], bool)
            assert isinstance(result["copias"], int)
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
