import asyncio

import pytest

from orb_core.exceptions import ORBSerializationError
from orb_core.serializer import deserialize, deserialize_stream, serialize


def test_round_trip_serialization():
    message = {"request_id": "abc", "args": [1, "x"], "kwargs": {}}
    encoded = serialize(message)
    assert deserialize(encoded) == message


def test_invalid_json_raises_serialization_error():
    invalid = b"\x00\x00\x00\x08not-json"
    with pytest.raises(ORBSerializationError):
        deserialize(invalid)


def test_invalid_length_raises_serialization_error():
    with pytest.raises(ORBSerializationError):
        deserialize(b"\x00\x00\x00\x05{}")


def test_partial_stream_is_reassembled():
    async def scenario():
        reader = asyncio.StreamReader()
        payload = serialize({"ok": True})
        reader.feed_data(payload[:2])
        reader.feed_data(payload[2:])
        reader.feed_eof()
        return await deserialize_stream(reader)

    assert asyncio.run(scenario()) == {"ok": True}
