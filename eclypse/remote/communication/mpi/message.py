"""Received MPI message with transport metadata separate from its data."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Message:
    """An MPI message's sender and application data."""

    source: str
    data: dict[str, Any]
