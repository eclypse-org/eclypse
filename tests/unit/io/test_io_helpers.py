from __future__ import annotations

from pathlib import Path

import pytest

from eclypse.graph import (
    Application,
    AssetGraph,
    Infrastructure,
)
from eclypse.io._helpers import (
    graph_kind,
    infer_format,
    normalize_json_value,
)
from eclypse.io.functions import (
    dump_infrastructure,
    load_infrastructure,
)


def test_graph_kind_resolves_supported_graphs():
    assert graph_kind(Infrastructure("infra")) == "infrastructure"
    assert graph_kind(Application()) == "application"

    with pytest.raises(TypeError):
        graph_kind(AssetGraph("plain"))


def test_infer_format_from_suffix_and_yaml_names(tmp_path: Path):
    assert infer_format(tmp_path / "infra.json") == "eclypse-json"
    assert infer_format(tmp_path / "infra.gml") == "gml"
    assert infer_format(tmp_path / "infra.graphml") == "graphml"
    assert infer_format(tmp_path / "docker-compose.yaml") == "docker-compose"
    assert infer_format(tmp_path / "infra.tosca.yaml") == "tosca"
    assert normalize_json_value(
        {
            "tuple": ("a", 1),
            "set": {3, 1, 2},
        }
    ) == {
        "tuple": ["a", 1],
        "set": [1, 2, 3],
    }

    with pytest.raises(ValueError):
        infer_format(tmp_path / "infra.unknown")
    with pytest.raises(ValueError):
        infer_format(tmp_path / "ambiguous.yaml")


def test_public_functions_report_inference_errors(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
):
    with pytest.raises(ValueError):
        dump_infrastructure(sample_infrastructure, tmp_path / "infra.unknown")

    with pytest.raises(ValueError):
        load_infrastructure(tmp_path / "infra.unknown")
