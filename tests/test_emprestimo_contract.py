import asyncio

import pytest

from database.seed import seed_database
from domain.emprestimo_service import EmprestimoService
from orb_core.broker import Broker
from orb_core.exceptions import ORBError
from orb_core.stub import Stub


def test_loan_remote_requires_jwt(tmp_path):
    async def scenario():
        path = str(tmp_path / "loan.db")
        seed_database(path)
        server = await Broker({"EmprestimoService": EmprestimoService(path)}).start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            with pytest.raises(ORBError) as error:
                await Stub("EmprestimoService", "127.0.0.1", port).invoke_async("emprestarLivro", "usuario-001", "livro-001")
            assert error.value.code == "AUTH_INVALID"
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
