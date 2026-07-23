import asyncio

import pytest

from orb_core.broker import Broker
from orb_core.exceptions import ORBError
from orb_core.stub import Stub


class Echo:
    async def echo(self, value):
        return value


def test_stub_broker_skeleton_round_trip():
    async def scenario():
        broker = Broker({"Echo": Echo()}, protected_methods=set())
        server = await broker.start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            stub = Stub("Echo", "127.0.0.1", port, timeout=1)
            assert await stub.invoke_async("echo", "hello") == "hello"
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())


def test_broker_returns_method_not_found():
    async def scenario():
        broker = Broker({"Echo": Echo()}, protected_methods=set())
        server = await broker.start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            with pytest.raises(ORBError) as error:
                await Stub("Echo", "127.0.0.1", port, timeout=1).invoke_async("missing")
            assert error.value.code == "METHOD_NOT_FOUND"
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
