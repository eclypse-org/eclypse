"""Structured result for remote node operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Optional,
)

if TYPE_CHECKING:
    from eclypse.remote.service import Service
    from eclypse.remote.utils import (
        RemoteOps,
        ResponseCode,
    )


@dataclass
class RemoteOpResult:
    """Result payload returned by remote node operations."""

    code: ResponseCode
    operation: RemoteOps
    node_id: str
    service_id: str
    error: Optional[str] = None
    service: Optional[Service] = None
