from __future__ import annotations

import pytest

from eclypse.graph import Infrastructure
from eclypse.io import (
    GraphExporter,
    GraphImporter,
    IORegistry,
    default_registry,
)


class RegistryExporter(GraphExporter[Infrastructure, dict]):
    def to_data(self, graph: Infrastructure, *, context=None):
        del context
        return {"id": graph.id}

    def write_data(self, data, target, *, context=None):
        del data, target, context


class RegistryImporter(GraphImporter[Infrastructure, dict]):
    def read_data(self, source, *, context=None):
        del source, context
        return {"id": "registry"}

    def from_data(self, data, *, kind=None, context=None):
        del kind, context
        return Infrastructure(data["id"])


def test_registry_is_immutable_extensible_and_reports_errors():
    registry = IORegistry()

    with pytest.raises(ValueError):
        registry.get_importer("infrastructure", "missing")
    with pytest.raises(ValueError):
        registry.get_exporter("application", "missing")
    with pytest.raises(ValueError):
        registry.formats("application", direction="sideways")

    extended = registry.with_exporter("infrastructure", "memory", RegistryExporter)
    extended = extended.with_importer("infrastructure", "memory", RegistryImporter)

    assert registry.formats("infrastructure") == []
    assert extended.formats("infrastructure") == ["memory"]
    assert extended.formats("infrastructure", direction="import") == ["memory"]


def test_default_registry_exposes_builtin_formats():
    assert default_registry.formats("application") == [
        "docker-compose",
        "eclypse-json",
        "gml",
        "graphml",
        "node-link-json",
        "tosca",
    ]
    assert default_registry.formats("infrastructure") == [
        "eclypse-json",
        "gml",
        "graphml",
        "node-link-json",
        "tosca",
    ]
