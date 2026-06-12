from __future__ import annotations

import pytest

from eclypse.graph import Application
from eclypse.remote.service.service import Service


class ConcreteService(Service):
    async def step(self):
        return None


def test_application_has_default_id():
    app = Application()

    assert app.id == "Application"
    assert app.node_assets == {}


def test_application_default_assets_are_explicit_opt_in():
    app = Application(include_default_assets=True)

    assert "gpu" in app.node_assets


def test_application_add_service_and_set_flows():
    app = Application("demo")
    gateway = ConcreteService("gateway")
    worker = ConcreteService("worker")

    app.add_service(gateway)
    app.add_service(worker)
    app.add_edge("gateway", "worker")
    app.set_flows()

    assert app.flows == [["gateway", "worker"]]
    assert app.has_service_implementations

    with pytest.raises(TypeError):
        app.add_service("not-a-service")  # type: ignore[arg-type]


def test_application_rejects_reassigning_service_to_another_app():
    gateway = ConcreteService("gateway")
    first = Application("first")
    second = Application("second")

    first.add_service(gateway)

    with pytest.raises(ValueError, match="already assigned"):
        second.add_service(gateway)


def test_application_set_flows_handles_missing_gateway_and_missing_path():
    app = Application("demo")
    worker = ConcreteService("worker")
    helper = ConcreteService("helper")

    app.add_service(worker)
    app.add_service(helper)
    app.set_flows()
    assert app.flows == []

    gateway = ConcreteService("gateway")
    app.add_service(gateway)
    app.add_edge("gateway", "worker")
    app.set_flows()

    assert app.flows == [["gateway", "worker"]]


def test_application_detects_missing_service_logic():
    app = Application("broken")
    app.add_node("orphan")

    assert not app.has_service_implementations
