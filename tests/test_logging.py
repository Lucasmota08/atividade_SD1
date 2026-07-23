import logging

from orb_core.logging_config import OrbFormatter


def test_log_formatter_contains_required_fields():
    record = logging.LogRecord("test", logging.INFO, "", 1, "mensagem", (), None)
    record.component = "Stub"
    record.request_id = "req-1"
    formatted = OrbFormatter().format(record)
    assert "[INFO]" in formatted
    assert "[Stub]" in formatted
    assert "[req-1]" in formatted
    assert formatted.endswith("mensagem")
