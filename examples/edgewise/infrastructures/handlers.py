from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
)

if TYPE_CHECKING:
    from eclypse.graph.infrastructure import Infrastructure


def bwth_handler(infrastructure: Infrastructure, **iattr: Dict[str, Any]) -> None:
    infrastructure.graph["bwTh"] = iattr["Threshold"]


def hwth_handler(infrastructure: Infrastructure, **iattr: Dict[str, Any]) -> None:
    infrastructure.graph["hwTh"] = iattr["Threshold"]


def node_type_handler(infrastructure: Infrastructure, **nattr: Dict[str, Any]) -> None:
    node_id = nattr.pop("NodeId")
    infrastructure.nodes[node_id]["Type"] = nattr["Type"]


def location_handler(infrastructure: Infrastructure, **nattr: Dict[str, Any]) -> None:
    node_id = nattr.pop("NodeId")
    infrastructure.nodes[node_id]["Location"] = nattr["Location"]


def provider_handler(infrastructure: Infrastructure, **nattr: Dict[str, Any]) -> None:
    node_id = nattr.pop("NodeId")
    infrastructure.nodes[node_id]["Provider"] = nattr["Provider"]


def get_handlers() -> Dict[str, Callable]:
    return {
        "bwTh": bwth_handler,
        "hwTh": hwth_handler,
        "nodeType": node_type_handler,
        "location": location_handler,
        "provider": provider_handler,
    }
