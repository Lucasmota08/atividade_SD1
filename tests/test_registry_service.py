import asyncio

from orb_core.registry import Endpoint, RegistryClient
from registry_service.main import RegistryServer


def test_registry_tcp_register_and_resolve():
    async def scenario():
        server = await RegistryServer().start("127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        client = RegistryClient("127.0.0.1", port)
        try:
            await client.register(Endpoint("Probe", "127.0.0.1", 9001, "node-1"))
            resolved = await client.resolve("Probe")
            assert resolved.node_id == "node-1"
            assert (await client.list_nodes())[0]["object_id"] == "Probe"
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
