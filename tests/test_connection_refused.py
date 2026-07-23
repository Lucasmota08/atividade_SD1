import asyncio

import pytest

from orb_core.exceptions import ORBConnectionRefusedError
from orb_core.stub import Stub


def test_connection_refused_is_translated():
    async def scenario():
        with pytest.raises(ORBConnectionRefusedError):
            await Stub("Missing", "127.0.0.1", 0, timeout=1.0).invoke_async("call")

    asyncio.run(scenario())
