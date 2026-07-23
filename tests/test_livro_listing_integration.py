import asyncio

from database.seed import seed_database
from domain.livro_service import LivroService
from orb_core.broker import Broker
from orb_core.stub import Stub


def test_remote_book_listing(tmp_path):
    async def scenario():
        path = str(tmp_path / "books.db")
        seed_database(path)
        server = await Broker({"LivroService": LivroService(path)}).start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            result = await Stub("LivroService", "127.0.0.1", port).invoke_async("listarLivros", auth_token="invalid")
            return result
        finally:
            server.close()
            await server.wait_closed()

    import pytest
    with pytest.raises(Exception):
        asyncio.run(scenario())
