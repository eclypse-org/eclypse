from __future__ import annotations

import pytest

from eclypse.placement import Placement
from eclypse.placement.view import PlacementView


def test_placement_maps_services_nodes_links_and_flags(
    sample_infrastructure,
    sample_application,
    mapped_placement,
):
    placement = Placement(sample_infrastructure, sample_application)

    assert placement.reset_requested is False
    assert placement.deployed is False

    with pytest.raises(ValueError, match="No placement strategy"):
        placement._generate_mapping({}, PlacementView(sample_infrastructure))

    placement.mark_for_reset()
    placement.mark_deployed()

    assert placement.reset_requested is True
    assert placement.deployed is True
    assert mapped_placement.service_placement("gateway") == "edge-a"
    assert mapped_placement.services_on_node("edge-a") == ["gateway"]
    assert mapped_placement.interactions_on_link("edge-a", "edge-b") == [
        ("gateway", "worker")
    ]
    assert mapped_placement.node_service_mapping()["edge-b"] == ["worker"]
    assert mapped_placement.node_requirements_mapping()["edge-a"]["cpu"] == 1
    assert mapped_placement.link_requirements_mapping()[("edge-a", "edge-b")] == {
        "latency": 6,
        "bandwidth": 4,
    }
    assert mapped_placement.is_partial == []
    assert "gateway -> edge-a" in str(mapped_placement)
    assert repr(mapped_placement) == str(mapped_placement)
    assert mapped_placement._path_crosses_link(None, "edge-a", "edge-b") is False

    placement.clear_reset()
    placement.mark_undeployed()

    assert placement.reset_requested is False
    assert placement.deployed is False


@pytest.mark.parametrize("node", ["edge-a", "edge-b"])
def test_colocated_interactions_do_not_consume_links(mapped_placement, node):
    mapped_placement.mapping = {"gateway": node, "worker": node}
    assert mapped_placement.interactions_on_link("edge-a", "edge-b") == []
    assert (
        mapped_placement._path_crosses_link([("other", "link", {})], "edge-a", "edge-b")
        is False
    )


def test_interactions_skip_unused_direct_link_and_reuse_route_cache(mapped_placement):
    infrastructure = mapped_placement.infrastructure
    infrastructure.add_node("relay", availability=1)
    infrastructure.add_edge("edge-a", "relay", latency=1, bandwidth=10)
    infrastructure.add_edge("relay", "edge-b", latency=1, bandwidth=10)
    mapped_placement.application.add_edge("worker", "gateway", latency=6, bandwidth=4)

    assert mapped_placement.interactions_on_link("edge-a", "edge-b") == []
