from __future__ import annotations

from types import SimpleNamespace

import pytest

from eclypse.placement import Placement
from eclypse.placement._manager import PlacementManager
from eclypse.placement.strategies import StaticStrategy


def test_manager_generate_mapping_uses_global_strategy_and_enact_resets(
    sample_infrastructure,
    sample_application,
):
    sample_infrastructure.strategy = StaticStrategy(
        {"gateway": "edge-a", "worker": "edge-b"}
    )
    manager = PlacementManager(sample_infrastructure)
    manager.register(sample_application)
    placement = manager.get(sample_application.id)

    manager.generate_mapping(placement)

    assert placement.mapping == {"gateway": "edge-a", "worker": "edge-b"}
    assert manager.placements == {sample_application.id: placement}

    placement.mark_for_reset()
    placement.mark_deployed()
    manager.enact()

    assert placement.mapping == {}
    assert placement.reset_requested is False
    assert manager.placement_view.infrastructure is sample_infrastructure


def test_manager_rejects_missing_strategy_and_resets_partial_mapping(
    sample_infrastructure,
    sample_application,
):
    manager = PlacementManager(sample_infrastructure)

    with pytest.raises(ValueError, match="No placement strategy provided"):
        manager.generate_mapping(Placement(sample_infrastructure, sample_application))

    partial_strategy = SimpleNamespace(
        place=lambda *_args, **_kwargs: {"gateway": "edge-a", "worker": None}
    )
    placement = Placement(
        sample_infrastructure,
        sample_application,
        strategy=partial_strategy,
    )

    manager.generate_mapping(placement)

    assert placement.mapping == {}
    assert placement.is_partial == ["gateway", "worker"]


def test_manager_audit_marks_violating_apps_and_get_raises(
    monkeypatch,
    sample_infrastructure,
    sample_application,
):
    manager = PlacementManager(sample_infrastructure)
    manager.register(
        sample_application,
        StaticStrategy({"gateway": "edge-a", "worker": "edge-b"}),
    )
    placement = manager.get(sample_application.id)
    manager.placement_view.nodes_used_by["edge-a"].add(sample_application.id)
    monkeypatch.setattr(
        manager,
        "mapping_phase",
        lambda: iter([(placement, ["edge-a"])]),
    )

    manager.audit()

    assert placement.reset_requested is True

    with pytest.raises(KeyError, match="Application missing not found"):
        manager.get("missing")


def test_manager_handles_empty_mappings_and_respected_audits(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    dummy_logger,
):
    manager = PlacementManager(sample_infrastructure)
    standalone = Placement(sample_infrastructure, sample_application)
    sample_infrastructure.strategy = SimpleNamespace(
        place=lambda *_args, **_kwargs: {"gateway": None, "worker": None}
    )
    monkeypatch.setattr("eclypse.placement._manager.logger", dummy_logger)

    manager.generate_mapping(standalone)

    manager.register(
        sample_application,
        StaticStrategy({"gateway": "edge-a", "worker": "edge-b"}),
    )
    placement = manager.get(sample_application.id)
    monkeypatch.setattr(manager, "mapping_phase", lambda: iter([(placement, [])]))

    manager.audit()

    assert standalone.mapping == {}
    assert placement.reset_requested is False
