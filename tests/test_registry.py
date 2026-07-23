import pytest

from orb_core.exceptions import ObjectNotFoundError
from orb_core.registry import Registry


def test_registry_round_robin_and_missing_object():
    registry = Registry()
    registry.registrar("LivroService", "node-1", 9001, "node-1")
    registry.registrar("LivroService", "node-2", 9002, "node-2")
    assert registry.resolver("LivroService").node_id == "node-1"
    assert registry.resolver("LivroService").node_id == "node-2"
    assert registry.resolver("LivroService").node_id == "node-1"
    with pytest.raises(ObjectNotFoundError):
        registry.resolver("missing")
