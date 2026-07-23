"""Configuração de logging estruturado do ORB."""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone


class OrbFormatter(logging.Formatter):
    """Formata logs no padrão exigido pelo projeto."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        component = getattr(record, "component", "ORBCore")
        request_id = getattr(record, "request_id", "-")
        return f"[{timestamp}] [{record.levelname}] [{component}] [{request_id}] {record.getMessage()}"


def configure_logging(level: int = logging.INFO) -> None:
    """Configura saída de console e arquivo opcional uma única vez."""
    root = logging.getLogger()
    if root.handlers:
        return
    formatter = OrbFormatter()
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    root.setLevel(level)
    root.addHandler(stream)
    log_file = os.getenv("LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
