import asyncio

from orb_core.broker import Broker
from orb_core.registry import Registry
from orb_core.stub import Stub


class Node:
    def __init__(self, node_id):
        self.node_id = node_id

    def identify(self):
        return self.node_id


def test_registry_distributes_calls_between_nodes():
    async def scenario():
        registry = Registry()
        servers = []
        for node_id in ("node-1", "node-2"):
            broker = Broker({"Probe": Node(node_id)}, protected_methods=set())
            server = await broker.start("127.0.0.1", 0)
            port = server.sockets[0].getsockname()[1]
            registry.registrar("Probe", "127.0.0.1", port, node_id)
            servers.append(server)
        class LocalRegistry:
            async def resolve(self, object_id):
                return registry.resolver(object_id)
        try:
            stub = Stub("Probe", registry=LocalRegistry())
            assert await stub.invoke_async("identify") == "node-1"
            assert await stub.invoke_async("identify") == "node-2"
        finally:
            for server in servers:
                server.close()
                await server.wait_closed()

    asyncio.run(scenario())
