"""Serialização JSON e framing length-prefixed do ORB."""

from __future__ import annotations

import asyncio
import json
import struct
from typing import Any

from .exceptions import ORBSerializationError

_HEADER_SIZE = 4
_MAX_MESSAGE_SIZE = 4 * 1024 * 1024


def serialize(message: dict[str, Any]) -> bytes:
    """Serializa uma mensagem JSON com cabeçalho de quatro bytes."""
    try:
        payload = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ORBSerializationError("Payload não pode ser serializado") from exc
    if len(payload) > _MAX_MESSAGE_SIZE:
        raise ORBSerializationError("Payload excede o tamanho máximo")
    return struct.pack("!I", len(payload)) + payload


def deserialize(data: bytes) -> dict[str, Any]:
    """Desserializa uma mensagem completa com framing."""
    if len(data) < _HEADER_SIZE:
        raise ORBSerializationError("Cabeçalho incompleto")
    size = struct.unpack("!I", data[:_HEADER_SIZE])[0]
    payload = data[_HEADER_SIZE:]
    if size != len(payload) or size > _MAX_MESSAGE_SIZE:
        raise ORBSerializationError("Tamanho do payload inválido")
    try:
        result = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ORBSerializationError("Payload JSON inválido") from exc
    if not isinstance(result, dict):
        raise ORBSerializationError("Envelope deve ser um objeto JSON")
    return result


async def read_message(reader: asyncio.StreamReader) -> dict[str, Any]:
    """Lê uma mensagem enquadrada de um stream asyncio."""
    try:
        header = await reader.readexactly(_HEADER_SIZE)
        size = struct.unpack("!I", header)[0]
        if size > _MAX_MESSAGE_SIZE:
            raise ORBSerializationError("Tamanho do payload inválido")
        payload = await reader.readexactly(size)
    except asyncio.IncompleteReadError as exc:
        raise ORBSerializationError("Stream terminou antes do payload completo") from exc
    return deserialize(header + payload)


async def deserialize_stream(reader: asyncio.StreamReader) -> dict[str, Any]:
    """Alias assíncrono compatível com o contrato do projeto."""
    return await read_message(reader)


async def write_message(writer: asyncio.StreamWriter, message: dict[str, Any]) -> None:
    """Serializa e envia uma mensagem pelo stream."""
    writer.write(serialize(message))
    await writer.drain()
