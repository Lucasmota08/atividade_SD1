import asyncio

from orb_core.broker import Broker
from orb_core.registry import Registry
from orb_core.stub import Stub


class Healthy:
    def status(self):
        return "healthy"


def test_failover_uses_remaining_endpoint():
    async def scenario():
        registry = Registry()
        dead = await Broker({"Probe": Healthy()}, protected_methods=set()).start("127.0.0.1", 0)
        dead_port = dead.sockets[0].getsockname()[1]
        healthy = await Broker({"Probe": Healthy()}, protected_methods=set()).start("127.0.0.1", 0)
        healthy_port = healthy.sockets[0].getsockname()[1]
        registry.registrar("Probe", "127.0.0.1", dead_port, "dead")
        registry.registrar("Probe", "127.0.0.1", healthy_port, "healthy")
        class LocalRegistry:
            async def resolve(self, object_id):
                return registry.resolver(object_id)
        dead.close()
        await dead.wait_closed()
        try:
            assert await Stub("Probe", registry=LocalRegistry(), timeout=0.05).invoke_async("status") == "healthy"
        finally:
            healthy.close()
            await healthy.wait_closed()

    asyncio.run(scenario())
