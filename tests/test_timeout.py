import asyncio

import pytest

from orb_core.exceptions import ORBTimeoutError
from orb_core.stub import Stub


class Slow:
    async def wait(self):
        await asyncio.sleep(10)


def test_slow_server_times_out():
    async def scenario():
        from orb_core.broker import Broker

        server = await Broker({"Slow": Slow()}, protected_methods=set()).start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            with pytest.raises(ORBTimeoutError):
                await Stub("Slow", "127.0.0.1", port, timeout=0.05).invoke_async("wait")
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
