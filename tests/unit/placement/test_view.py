from __future__ import annotations

from eclypse.placement.view import PlacementView


def test_placement_view_tracks_residual_resources_and_resets(mapped_placement):
    view = PlacementView(mapped_placement.infrastructure)

    view._update_view(mapped_placement)

    assert view.nodes_used_by["edge-a"] == {"shop"}
    assert view.residual.nodes["edge-a"]["cpu"] == 3
    assert view.get_edge_view("edge-a", "edge-b")["latency"] == 6

    view._reset()

    assert view.nodes_used_by == {}
    assert view.get_node_view("edge-a")["cpu"] == 0


def test_placement_view_marks_reset_when_interaction_path_is_missing(mapped_placement):
    mapped_placement.infrastructure.remove_edge("edge-a", "edge-b")
    view = PlacementView(mapped_placement.infrastructure)

    view._update_view(mapped_placement)

    assert mapped_placement.reset_requested is True
