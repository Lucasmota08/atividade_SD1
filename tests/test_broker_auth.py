import asyncio

import pytest

from orb_core.broker import Broker
from orb_core.exceptions import ORBError
from orb_core.stub import Stub


class Protected:
    def read(self):
        return "secret"


def test_protected_method_requires_token():
    async def scenario():
        server = await Broker({"Protected": Protected()}, protected_methods={"read"}).start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            with pytest.raises(ORBError) as error:
                await Stub("Protected", "127.0.0.1", port).invoke_async("read")
            assert error.value.code == "AUTH_INVALID"
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
