import asyncio

import pytest

from orb_core.exceptions import ORBConnectionRefusedError
from orb_core.stub import Stub


def test_all_nodes_down_returns_treated_error():
    with pytest.raises(ORBConnectionRefusedError):
        asyncio.run(Stub("LivroService", "127.0.0.1", 0, timeout=1.0).invoke_async("listarLivros"))
