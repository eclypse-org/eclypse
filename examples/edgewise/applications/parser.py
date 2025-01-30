from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Optional,
)

import prolog_to_networkx as ptn
from networkx.classes.reportviews import (
    EdgeView,
    NodeView,
)

from eclypse.graph import Application

from .handlers import get_handlers

if TYPE_CHECKING:
    from eclypse.graph.assets import Asset


cfg = ptn.FactsConfig(
    graph_facts=["application", "service", "function", "thing"],
    node_facts=["serviceInstance", "functionInstance", "thingInstance"],
    edge_facts="dataFlow",
    graph_id="AppId",
    node_id="InstanceId",
)

cfg.add_graph_fact("application", "Functions", "Services")
cfg.add_fact("service", "ServiceId", "SW", ("Arch", "HW"))
cfg.add_fact("function", "FunctionId", "SWPlatform", ("Arch", "HW"))
cfg.add_fact("thing", "ThingId", "TType")

cfg.add_node_fact("serviceInstance", "ServiceId")
cfg.add_node_fact("functionInstance", "FunctionId", ("ReqXMont", "ReqDuration"))
cfg.add_node_fact("thingInstance", "ThingId")

cfg.add_edge_fact("dataFlow", "DataId", "Sec", "Size", "Rate", "latency")


def get_application(
    application_id: str,
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    edge_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    edge_assets: Optional[Dict[str, Asset]] = None,
    seed: Optional[int] = None,
) -> Application:
    """Parse the knowledge base and return the application graph,
    by its application_id.
    """

    parser = ptn.PrologGraphParser(cfg, handlers=get_handlers())
    app = Application(
        application_id=application_id,
        node_update_policy=node_update_policy,
        edge_update_policy=edge_update_policy,
        node_assets=node_assets,
        edge_assets=edge_assets,
        include_default_assets=False,
        seed=seed,
    )
    app.graph["components"] = defaultdict(dict)
    app.graph["things"] = defaultdict(dict)
    app.graph["file"] = Path(__file__).parent / "prolog" / f"{application_id}.pl"

    parser.parse(file_path=app.graph["file"], graph=app)

    for c in app.graph["components"]:
        app.graph["components"][c] = dict(app.graph["components"][c])

    app.graph["things"] = dict(app.graph["things"])
    return app
