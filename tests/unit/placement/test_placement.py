from __future__ import annotations

from eclypse.placement import Placement


def test_placement_maps_services_nodes_links_and_flags(
    sample_infrastructure,
    sample_application,
    mapped_placement,
):
    placement = Placement(sample_infrastructure, sample_application)

    assert placement.reset_requested is False
    assert placement.deployed is False

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

    placement.clear_reset()
    placement.mark_undeployed()

    assert placement.reset_requested is False
    assert placement.deployed is False
