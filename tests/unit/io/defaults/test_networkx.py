from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

from eclypse.graph import (
    Application,
    Infrastructure,
)
from eclypse.graph.assets import Additive
from eclypse.io import (
    InfrastructureContext,
    dump_application,
    dump_infrastructure,
    load_application,
    load_infrastructure,
)
from eclypse.io.defaults.networkx import NetworkXImporter
from eclypse.io.graphs import graph_from_networkx


class DummyNetworkXImporter(NetworkXImporter):
    def read_data(self, source, *, context=None):
        del source, context
        return nx.DiGraph()


def test_gml_graphml_and_node_link_round_trips(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
    sample_application: Application,
):
    gml_path = tmp_path / "infra.gml"
    graphml_path = tmp_path / "infra.graphml"
    node_link_path = tmp_path / "app.node-link.json"

    dump_infrastructure(sample_infrastructure, gml_path)
    dump_infrastructure(sample_infrastructure, graphml_path, "graphml")
    dump_application(sample_application, node_link_path, "node-link-json")

    assert load_infrastructure(gml_path).has_edge("n1", "n2")
    assert load_infrastructure(graphml_path).nodes["n1"]["tier"] == "edge"
    assert load_application(node_link_path, "node-link-json").has_edge(
        "frontend",
        "worker",
    )


def test_graph_only_import_can_take_asset_schema_from_context():
    data = nx.DiGraph()
    data.add_node("sensor", temperature=25)

    context = InfrastructureContext(
        node_assets={"temperature": Additive(0, 100)},
        edge_assets={},
        include_default_assets=False,
    )
    loaded = graph_from_networkx(
        data,
        kind="infrastructure",
        context=context,
    )

    assert list(loaded.node_assets) == ["temperature"]
    assert loaded.nodes["sensor"]["temperature"] == 25


def test_graph_from_networkx_rejects_unknown_kind():
    with pytest.raises(ValueError):
        graph_from_networkx(nx.DiGraph(), kind="unknown")
    with pytest.raises(ValueError, match="explicit graph kind"):
        DummyNetworkXImporter().from_data(nx.DiGraph())
