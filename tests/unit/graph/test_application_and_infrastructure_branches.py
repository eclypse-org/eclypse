from __future__ import annotations

import pytest

from eclypse.graph import Application
from eclypse.placement.strategies import StaticStrategy
from eclypse.remote.service.service import Service


def test_application_rejects_reassigning_service_to_another_app():
    gateway = Service("gateway")
    first = Application("first")
    second = Application("second")

    first.add_service(gateway)

    with pytest.raises(ValueError, match="already assigned"):
        second.add_service(gateway)


def test_application_set_flows_handles_missing_gateway_and_missing_path():
    app = Application("demo")
    worker = Service("worker")
    helper = Service("helper")

    app.add_service(worker)
    app.add_service(helper)
    app.set_flows()
    assert app.flows == []

    gateway = Service("gateway")
    app.add_service(gateway)
    app.add_edge("gateway", "worker")
    app.set_flows()

    assert app.flows == [["gateway", "worker"]]


def test_infrastructure_same_node_resources_and_strategy_flag(sample_infrastructure):
    assert sample_infrastructure.path_resources("edge-a", "edge-a") == (
        sample_infrastructure.edge_assets.upper_bound
    )
    assert sample_infrastructure.processing_time("edge-a", "edge-a") == 0.0
    assert sample_infrastructure.has_strategy is False

    sample_infrastructure.strategy = StaticStrategy({"gateway": "edge-a"})

    assert sample_infrastructure.has_strategy is True
