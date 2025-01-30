from __future__ import annotations
from .handlers import get_handlers
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Literal,
    Optional,
)

import prolog_to_networkx as ptn

from eclypse.graph import Infrastructure

if TYPE_CHECKING:
    from eclypse.graph.assets import Asset

cfg = ptn.FactsConfig(
    node_facts=["node", "nodeType", "location", "provider"],
    edge_facts="link",
)

cfg.add_fact("bwTh", "Threshold")
cfg.add_fact("hwTh", "Threshold")

cfg.add_node_fact("node", "SW", ("Arch", "HW"), "Sec", "IoT")
cfg.add_node_fact("nodeType", "Type")
cfg.add_node_fact("location", "Location")
cfg.add_node_fact("provider", "Provider")

cfg.add_edge_fact("link", "latency", "bandwidth")


def get_infrastructure(
    n: int,
    seed: int,
    topology: Literal["BA", "ER"],
    node_update_policy: Optional[Callable] = None,
    edge_update_policy: Optional[Callable] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    edge_assets: Optional[Dict[str, Asset]] = None,
) -> Infrastructure:

    parser = ptn.PrologGraphParser(cfg, handlers=get_handlers())

    infra = Infrastructure(
        f"Infr{n}-{seed}",
        node_update_policy=node_update_policy,
        edge_update_policy=edge_update_policy,
        node_assets=node_assets,
        edge_assets=edge_assets,
        include_default_assets=False,
        seed=seed,
    )

    infra.graph["file"] = Path(__file__).parent / topology / f"infr{n}-{seed}.pl"

    parser.parse(file=infra.graph["file"], graph=infra)

    return infra
