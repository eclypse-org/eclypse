from __future__ import annotations

import sys
import types

import networkx as nx
import pytest

from eclypse.builders.infrastructure import (
    get_backbone,
    get_caida,
    get_gabriel,
    get_orion_cev,
    get_sndlib,
    get_topohub,
    get_topology_zoo,
)


def _install_fake_topohub(monkeypatch: pytest.MonkeyPatch):
    requests: list[tuple[str, bool]] = []

    def get(path: str, use_names: bool = False):
        requests.append((path, use_names))

        graph = nx.Graph(name=path, demands={"A->B": 7}, stats={"avg_degree": 1.0})
        if path.startswith(("sndlib/", "topozoo/")):
            graph.add_node(0, name="Alpha", pos=[10.0, 20.0])
            graph.add_node(1, name="Beta", pos=[30.0, 40.0])
        else:
            graph.add_node(0, pos=[10.0, 20.0])
            graph.add_node(1, pos=[30.0, 40.0])

        graph.add_edge(
            0,
            1,
            dist=400.0,
            capacity=123.0,
            ecmp_fwd={"uni": 0.1},
            ecmp_bwd={"uni": 0.2},
        )
        return nx.node_link_data(graph, edges="edges")

    module = types.SimpleNamespace(get=get)
    monkeypatch.setitem(sys.modules, "topohub", module)
    return requests


def test_get_orion_cev():
    infrastructure = get_orion_cev(include_default_assets=True)

    assert "DU11" in infrastructure.nodes
    assert infrastructure.has_edge("DU11", "NS11")
    assert infrastructure.nodes["NS11"]["processing_time"] == 1


def test_get_sndlib(monkeypatch: pytest.MonkeyPatch):
    requests = _install_fake_topohub(monkeypatch)

    infrastructure = get_sndlib("polska", include_default_assets=True)

    assert requests == [("sndlib/polska", True)]
    assert "Alpha" in infrastructure.nodes
    assert "name" not in infrastructure.nodes["Alpha"]
    assert infrastructure.graph["dataset_path"] == "sndlib/polska"
    assert infrastructure.graph["demands"] == {"A->B": 7}
    assert infrastructure.has_edge("Alpha", "Beta")
    assert infrastructure["Alpha"]["Beta"]["latency"] == 2.0
    assert infrastructure["Alpha"]["Beta"]["bandwidth"] == 123.0


def test_get_topology_zoo(monkeypatch: pytest.MonkeyPatch):
    requests = _install_fake_topohub(monkeypatch)

    infrastructure = get_topology_zoo("Abilene", include_default_assets=True)

    assert requests == [("topozoo/Abilene", True)]
    assert "Alpha" in infrastructure.nodes
    assert infrastructure.graph["dataset_path"] == "topozoo/Abilene"
    assert infrastructure.nodes["Alpha"]["topohub_id"] == 0


def test_get_backbone(monkeypatch: pytest.MonkeyPatch):
    requests = _install_fake_topohub(monkeypatch)

    infrastructure = get_backbone("africa", include_default_assets=True)

    assert requests == [("backbone/africa", False)]
    assert "n0" in infrastructure.nodes
    assert infrastructure.graph["dataset_path"] == "backbone/africa"
    assert "cpu" in infrastructure.nodes["n0"]
    assert infrastructure.nodes["n0"]["topohub_id"] == 0


def test_get_caida(monkeypatch: pytest.MonkeyPatch):
    requests = _install_fake_topohub(monkeypatch)

    infrastructure = get_caida("2024-01", include_default_assets=True)

    assert requests == [("caida/2024-01", False)]
    assert "n0" in infrastructure.nodes
    assert infrastructure.graph["dataset_path"] == "caida/2024-01"


def test_get_gabriel(monkeypatch: pytest.MonkeyPatch):
    requests = _install_fake_topohub(monkeypatch)

    infrastructure = get_gabriel(25, sample=2, include_default_assets=True)

    assert requests == [("gabriel/25/2", False)]
    assert "n0" in infrastructure.nodes
    assert infrastructure.graph["dataset_path"] == "gabriel/25/2"


def test_get_topohub(monkeypatch: pytest.MonkeyPatch):
    requests: list[tuple[str, bool]] = []

    def get(path: str, use_names: bool = False):
        requests.append((path, use_names))

        graph = nx.Graph(name=path)
        graph.add_node("alpha", pos=[1.0, 2.0])
        graph.add_node("beta", pos=[3.0, 4.0])
        graph.add_node("gamma", pos=[5.0, 6.0])
        graph.add_edge(
            "alpha",
            "beta",
            latency=7.5,
            bandwidth=99.0,
            capacity=123.0,
        )
        graph.add_edge("beta", "gamma")
        return nx.node_link_data(graph, edges="edges")

    monkeypatch.setitem(sys.modules, "topohub", types.SimpleNamespace(get=get))

    infrastructure = get_topohub(
        "sndlib/polska", use_names=True, include_default_assets=True
    )
    raw_infrastructure = get_topohub(
        "sndlib/polska", use_names=True, include_default_assets=False
    )

    assert requests == [("sndlib/polska", True), ("sndlib/polska", True)]
    assert "alpha" in infrastructure.nodes
    assert infrastructure.graph["dataset_path"] == "sndlib/polska"
    assert infrastructure["alpha"]["beta"]["latency"] == 7.5
    assert infrastructure["alpha"]["beta"]["bandwidth"] == 99.0
    assert infrastructure["alpha"]["beta"]["capacity"] == 123.0
    assert "bandwidth" not in raw_infrastructure["beta"]["gamma"]
    assert "latency" not in raw_infrastructure["beta"]["gamma"]


def test_get_topohub_preserves_name_metadata_when_not_used_as_id(
    monkeypatch: pytest.MonkeyPatch,
):
    def get(path: str, use_names: bool = False):
        del use_names
        graph = nx.Graph(name=path)
        graph.add_node(0, name="Alpha", pos=[1.0, 2.0])
        graph.add_node(1, name="Beta", pos=[3.0, 4.0])
        graph.add_edge(0, 1, dist=400.0)
        return nx.node_link_data(graph, edges="edges")

    monkeypatch.setitem(sys.modules, "topohub", types.SimpleNamespace(get=get))

    infrastructure = get_topohub(
        "sndlib/polska", use_names=False, include_default_assets=True
    )

    assert "n0" in infrastructure.nodes
    assert infrastructure.nodes["n0"]["name"] == "Alpha"
    assert infrastructure.nodes["n0"]["topohub_id"] == 0


def test_get_sndlib_requires_topohub(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delitem(sys.modules, "topohub", raising=False)
    monkeypatch.setattr(
        "eclypse.builders.infrastructure.references.topohub._helpers._require_module",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ImportError(
                "topohub is not installed. Please install it with 'pip install topohub'."
            )
        ),
    )

    with pytest.raises(ImportError, match="pip install topohub"):
        get_sndlib("polska")
