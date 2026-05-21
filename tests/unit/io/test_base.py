from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from eclypse.graph import Infrastructure
from eclypse.graph.assets import Asset
from eclypse.io import (
    GraphExporter,
    GraphImporter,
    IOContext,
    dump_infrastructure,
    load_infrastructure,
)


def test_asset_is_enforced_as_abstract_base_class():
    with pytest.raises(TypeError):
        Asset(0, 1)  # type: ignore[abstract]


@dataclass(slots=True)
class MemoryExporter(GraphExporter[Infrastructure, dict[str, Any]]):
    seen: dict[str, Any] | None = None

    def to_data(self, graph: Infrastructure, *, context: IOContext | None = None):
        del context
        return {"id": graph.id, "nodes": list(graph.nodes)}

    def write_data(self, data, target, *, context: IOContext | None = None):
        del target, context
        self.seen = data


class MemoryImporter(GraphImporter[Infrastructure, dict[str, Any]]):
    def read_data(self, source, *, context: IOContext | None = None):
        del source, context
        return {"id": "memory", "nodes": ["n1"]}

    def from_data(self, data, *, kind=None, context: IOContext | None = None):
        del kind, context
        infrastructure = Infrastructure(data["id"])
        for node in data["nodes"]:
            infrastructure.add_node(node, strict=False)
        return infrastructure


def test_custom_exporter_and_importer_can_be_passed_directly(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
):
    exporter = MemoryExporter()

    dump_infrastructure(sample_infrastructure, tmp_path / "unused.mem", exporter)
    loaded_from_class = load_infrastructure(tmp_path / "unused.mem", MemoryImporter)
    loaded_from_instance = load_infrastructure(tmp_path / "unused.mem", MemoryImporter())

    assert exporter.seen == {"id": "infra", "nodes": ["n1", "n2"]}
    assert loaded_from_class.id == "memory"
    assert loaded_from_instance.has_node("n1")
