from __future__ import annotations

import pytest

from eclypse.graph.assets import Additive
from eclypse.io import (
    ApplicationContext,
    DockerComposeContext,
    InfrastructureContext,
    TOSCAApplicationContext,
    TOSCAInfrastructureContext,
)


def test_context_defaults_follow_include_default_assets():
    infrastructure_context = InfrastructureContext()
    application_context = ApplicationContext()
    custom_node_assets = {"cpu": Additive(0, 1)}
    custom_edge_assets = {"latency": Additive(0, 1)}
    custom_aggregators = {"latency": min}

    assert sorted(infrastructure_context.node_assets or {}) == [
        "availability",
        "cpu",
        "gpu",
        "processing_time",
        "ram",
        "storage",
    ]
    assert sorted(infrastructure_context.edge_assets or {}) == [
        "bandwidth",
        "latency",
    ]
    assert sorted(infrastructure_context.path_assets_aggregators or {}) == [
        "bandwidth",
        "latency",
    ]
    assert sorted(application_context.node_assets or {}) == [
        "availability",
        "cpu",
        "gpu",
        "processing_time",
        "ram",
        "storage",
    ]
    assert sorted(application_context.edge_assets or {}) == [
        "bandwidth",
        "latency",
    ]
    custom_infrastructure_context = InfrastructureContext(
        node_assets=custom_node_assets,
        edge_assets=custom_edge_assets,
        path_assets_aggregators=custom_aggregators,
    )
    custom_application_context = ApplicationContext(
        node_assets=custom_node_assets,
        edge_assets=custom_edge_assets,
    )

    assert custom_infrastructure_context.node_assets is custom_node_assets
    assert custom_infrastructure_context.edge_assets is custom_edge_assets
    assert custom_infrastructure_context.path_assets_aggregators is custom_aggregators
    assert custom_application_context.node_assets is custom_node_assets
    assert custom_application_context.edge_assets is custom_edge_assets


def test_context_defaults_are_empty_when_default_assets_are_disabled():
    infrastructure_context = InfrastructureContext(include_default_assets=False)
    application_context = ApplicationContext(include_default_assets=False)

    assert infrastructure_context.node_assets is None
    assert infrastructure_context.edge_assets is None
    assert infrastructure_context.path_assets_aggregators is None
    assert application_context.node_assets is None
    assert application_context.edge_assets is None


def test_context_reports_unknown_custom_entries():
    infrastructure_context = InfrastructureContext()
    application_context = ApplicationContext()

    with pytest.raises(ValueError):
        infrastructure_context.get_aggregator("unknown")
    with pytest.raises(ValueError):
        InfrastructureContext(include_default_assets=False).get_aggregator("latency")
    with pytest.raises(ValueError):
        application_context.get_service("unknown")


def test_standard_codec_context_defaults_are_strict():
    docker_context = DockerComposeContext()
    tosca_application_context = TOSCAApplicationContext()
    tosca_infrastructure_context = TOSCAInfrastructureContext()

    assert docker_context.require_services is True
    assert docker_context.require_service_image_or_build is True
    assert docker_context.allow_image_fallback_to_node is False
    assert tosca_application_context.require_definitions_version is True
    assert tosca_application_context.require_node_template_types is True
    assert tosca_infrastructure_context.require_definitions_version is True
    assert tosca_infrastructure_context.require_node_template_types is True
