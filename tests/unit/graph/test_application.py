from __future__ import annotations

import pytest

from eclypse.graph import Application
from eclypse.remote.service.service import Service


def test_application_add_service_and_set_flows():
    app = Application("demo")
    gateway = Service("gateway")
    worker = Service("worker")

    app.add_service(gateway)
    app.add_service(worker)
    app.add_edge("gateway", "worker")
    app.set_flows()

    assert app.flows == [["gateway", "worker"]]
    assert app.has_logic

    with pytest.raises(TypeError):
        app.add_service("not-a-service")  # type: ignore[arg-type]


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


def test_application_detects_missing_service_logic():
    app = Application("broken")
    app.add_node("orphan")

    assert not app.has_logic
