from __future__ import annotations

import pytest

from eclypse.placement.strategies import (
    BestFitStrategy,
    FirstFitStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    StaticStrategy,
    PlacementStrategy,
)
from eclypse.placement.view import PlacementView
from eclypse.utils.constants import RND_SEED


class DummyStrategy(PlacementStrategy):
    def place(self, infrastructure, application, placements, placement_view):
        del infrastructure, application, placements, placement_view
        return {}


def test_first_and_best_fit_strategies_choose_feasible_nodes(
    sample_infrastructure,
    sample_application,
):
    view = PlacementView(sample_infrastructure)
    first_fit = FirstFitStrategy(sort_fn=lambda item: item[0])
    best_fit = BestFitStrategy()

    first_mapping = first_fit.place(
        sample_infrastructure,
        sample_application,
        {},
        view,
    )
    best_mapping = best_fit.place(
        sample_infrastructure,
        sample_application,
        {},
        view,
    )

    assert first_mapping["gateway"] == "edge-a"
    assert set(best_mapping) == {"gateway", "worker"}

    unsorted_first_mapping = FirstFitStrategy().place(
        sample_infrastructure,
        sample_application,
        {},
        view,
    )
    assert set(unsorted_first_mapping) == {"gateway", "worker"}

    for node in sample_infrastructure.nodes:
        sample_infrastructure.nodes[node]["availability"] = 0
    assert FirstFitStrategy(sort_fn=lambda item: item[0]).place(
        sample_infrastructure,
        sample_application,
        {},
        view,
    ) == {}


def test_random_round_robin_and_static_strategies(
    monkeypatch,
    sample_infrastructure,
    sample_application,
):
    monkeypatch.setenv(RND_SEED, "5")
    view = PlacementView(sample_infrastructure)

    random_mapping = RandomStrategy(spread=True).place(
        sample_infrastructure,
        sample_application,
        {},
        view,
    )
    random_unspread_mapping = RandomStrategy(seed=3).place(
        sample_infrastructure,
        sample_application,
        {},
        view,
    )
    rr_mapping = RoundRobinStrategy(sort_fn=lambda item: item[0]).place(
        sample_infrastructure,
        sample_application,
        {},
        view,
    )
    static_mapping = StaticStrategy({"gateway": "edge-a", "worker": "edge-b"}).place(
        sample_infrastructure,
        sample_application,
        {},
        view,
    )

    assert set(random_mapping.values()) <= {"edge-a", "edge-b"}
    assert set(random_unspread_mapping.values()) <= {"edge-a", "edge-b"}
    assert rr_mapping == {"gateway": "edge-a", "worker": "edge-b"}
    assert static_mapping == {"gateway": "edge-a", "worker": "edge-b"}

    empty_view = PlacementView(sample_infrastructure)
    empty_view.residual.clear()
    assert (
        RandomStrategy(seed=3).place(
            sample_infrastructure,
            sample_application,
            {},
            empty_view,
        )
        == {}
    )


def test_static_strategy_validation_and_base_strategy_feasibility(
    sample_infrastructure,
    sample_application,
):
    strategy = StaticStrategy({"gateway": "missing"})
    base_strategy = DummyStrategy()

    assert not strategy.is_feasible(sample_infrastructure, sample_application)
    assert (
        strategy.place(
            sample_infrastructure,
            sample_application,
            {},
            PlacementView(sample_infrastructure),
        )
        == {}
    )
    assert base_strategy.is_feasible(sample_infrastructure, sample_application)

    with pytest.raises(ValueError, match="valid mapping"):
        StaticStrategy({})
