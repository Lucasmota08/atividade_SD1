import asyncio

import pytest

from orb_core.exceptions import ORBSerializationError
from orb_core.stub import Stub


def test_mismatched_request_id_is_rejected():
    async def handler(reader, writer):
        from orb_core.serializer import deserialize_stream, write_message
        await deserialize_stream(reader)
        await write_message(writer, {"request_id": "wrong", "status": "OK", "result": 1, "error": None})
        writer.close()

    async def scenario():
        server = await asyncio.start_server(handler, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            with pytest.raises(ORBSerializationError):
                await Stub("Echo", "127.0.0.1", port, timeout=0.1).invoke_async("echo")
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())
