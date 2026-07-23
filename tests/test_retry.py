import asyncio

import pytest

from orb_core.exceptions import ORBConnectionRefusedError
from orb_core.stub import Stub


def test_retry_can_be_observed_without_socket_leak(monkeypatch):
    attempts = 0
    original_sleep = asyncio.sleep

    async def fake_open(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        raise ConnectionRefusedError()

    monkeypatch.setattr(asyncio, "open_connection", fake_open)
    async def no_wait(_):
        await original_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", no_wait)

    async def scenario():
        with pytest.raises(ORBConnectionRefusedError):
            await Stub("Missing", "host", 1).invoke_async("call")

    asyncio.run(scenario())
    assert attempts == 3
