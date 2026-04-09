from __future__ import annotations

from eclypse.placement.strategies import (
    BestFitStrategy,
    FirstFitStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    StaticStrategy,
)
from eclypse.placement.strategies.strategy import PlacementStrategy
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
    assert rr_mapping == {"gateway": "edge-a", "worker": "edge-b"}
    assert static_mapping == {"gateway": "edge-a", "worker": "edge-b"}


def test_static_strategy_validation_and_base_strategy_feasibility(
    sample_infrastructure,
    sample_application,
):
    strategy = StaticStrategy({"gateway": "missing"})
    base_strategy = DummyStrategy()

    assert not strategy.is_feasible(sample_infrastructure, sample_application)
    assert base_strategy.is_feasible(sample_infrastructure, sample_application)
