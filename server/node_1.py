"""Processo do nó ORB 1."""

import asyncio
import os

from .node_common import run_node


if __name__ == "__main__":
    asyncio.run(run_node("node-1", os.getenv("NODE_1_HOST", "0.0.0.0"), int(os.getenv("NODE_1_PORT", "9001")), os.getenv("NODE_1_DB", "biblioteca_node1.db"), os.getenv("REGISTRY_HOST", "127.0.0.1"), int(os.getenv("REGISTRY_PORT", "8765")), os.getenv("NODE_1_ADVERTISE_HOST")))
