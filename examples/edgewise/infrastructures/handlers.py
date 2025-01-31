from __future__ import annotations
from eclypse.graph import NodeGroup

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
    ntype = nattr.pop("Type")
    infrastructure.nodes[node_id]["Type"] = ntype


def location_handler(infrastructure: Infrastructure, **nattr: Dict[str, Any]) -> None:
    node_id = nattr.pop("NodeId")
    infrastructure.nodes[node_id]["Location"] = nattr["Location"]


def provider_handler(infrastructure: Infrastructure, **nattr: Dict[str, Any]) -> None:
    node_id = nattr.pop("NodeId")
    infrastructure.nodes[node_id]["Provider"] = nattr["Provider"]


def node_handler(infrastructure: Infrastructure, **nattr: Dict[str, Any]) -> None:
    node_id = nattr.pop("NodeId")
    infrastructure.add_cloud_node(node_id, **nattr)


def link_handler(infrastructure: Infrastructure, **lattr: Dict[str, Any]) -> None:
    source, target = lattr.pop("SourceId"), lattr.pop("TargetId")
    infrastructure.add_edge(source, target, **lattr)


def get_handlers() -> Dict[str, Callable]:
    return {
        "bwTh": bwth_handler,
        "hwTh": hwth_handler,
        "nodeType": node_type_handler,
        "location": location_handler,
        "provider": provider_handler,
        "node": node_handler,
        "link": link_handler,
    }
