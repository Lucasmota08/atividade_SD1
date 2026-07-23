"""Processo do nó ORB 2."""

import asyncio
import os

from .node_common import run_node


if __name__ == "__main__":
    asyncio.run(run_node("node-2", os.getenv("NODE_2_HOST", "0.0.0.0"), int(os.getenv("NODE_2_PORT", "9002")), os.getenv("NODE_2_DB", "biblioteca_node2.db"), os.getenv("REGISTRY_HOST", "127.0.0.1"), int(os.getenv("REGISTRY_PORT", "8765")), os.getenv("NODE_2_ADVERTISE_HOST")))
