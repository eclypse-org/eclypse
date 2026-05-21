from __future__ import annotations

import json
from pathlib import Path

import pytest

from eclypse.graph import (
    Application,
    Infrastructure,
)
from eclypse.graph.assets.defaults import get_default_path_aggregators
from eclypse.io import (
    ApplicationContext,
    InfrastructureContext,
    IOContext,
    dump_application,
    dump_graph,
    dump_infrastructure,
    load_application,
    load_graph,
    load_infrastructure,
)
from eclypse.io.defaults.json import JSONImporter


def test_json_infrastructure_round_trip(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
):
    path = tmp_path / "infra.json"

    dump_infrastructure(sample_infrastructure, path)
    loaded = load_infrastructure(path)

    assert loaded.id == "infra"
    assert loaded.graph["owner"] == "unit"
    assert loaded.nodes["n1"]["cpu"] == 4
    assert loaded.nodes["n1"]["tier"] == "edge"
    assert loaded.edges["n1", "n2"]["latency"] == 5
    assert loaded.path_resources("n1", "n2")["bandwidth"] == 20


def test_json_application_round_trip_graph_only_and_services(
    tmp_path: Path,
    sample_application_with_service: Application,
    demo_service_cls,
):
    path = tmp_path / "app.json"
    context = ApplicationContext(services={"demo": demo_service_cls})

    dump_application(sample_application_with_service, path, application_context=context)
    loaded = load_application(path, application_context=context)

    assert loaded.id == "app"
    assert loaded.flows == [["frontend", "worker"]]
    assert loaded.nodes["frontend"]["cpu"] == 1
    assert isinstance(loaded.services["frontend"], demo_service_cls)
    assert loaded.has_service_implementations is False


def test_dump_graph_and_load_graph_use_kind_resolution(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
):
    path = tmp_path / "infra.json"

    dump_graph(sample_infrastructure, path)
    loaded = load_graph(path, "infrastructure")

    assert isinstance(loaded, Infrastructure)


def test_importer_rejects_wrong_schema_and_kind(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"eclypse_schema": "0", "kind": "infrastructure"}))

    with pytest.raises(ValueError):
        load_infrastructure(path)

    path.write_text(json.dumps({"eclypse_schema": "1.0", "kind": "application"}))

    with pytest.raises(ValueError):
        JSONImporter().load(path, kind="infrastructure")

    with pytest.raises(ValueError, match="Unsupported graph kind"):
        JSONImporter().from_data({"eclypse_schema": "1.0", "kind": "plain"})


def test_unknown_path_aggregator_and_service_fail_on_import(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
    sample_application_with_service: Application,
):
    path = tmp_path / "infra.json"
    dump_infrastructure(sample_infrastructure, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["extras"]["path_assets_aggregators"]["latency"] = "unknown"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError):
        load_infrastructure(path)

    app_path = tmp_path / "app.json"
    dump_application(sample_application_with_service, app_path)
    app_data = json.loads(app_path.read_text(encoding="utf-8"))
    app_data["extras"]["services"]["frontend"] = "missing"
    app_path.write_text(json.dumps(app_data), encoding="utf-8")

    with pytest.raises(ValueError):
        load_application(app_path)


def test_canonical_graphs_handle_context_fallbacks_and_null_services(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
    sample_application_with_service: Application,
    demo_service_cls,
):
    infra_path = tmp_path / "infra-context.json"
    app_path = tmp_path / "app-context.json"
    infra_context = InfrastructureContext(
        node_assets=sample_infrastructure.node_assets,
        edge_assets=sample_infrastructure.edge_assets,
        include_default_assets=False,
        path_assets_aggregators=get_default_path_aggregators(),
    )
    app_context = ApplicationContext(
        node_assets=sample_application_with_service.node_assets,
        edge_assets=sample_application_with_service.edge_assets,
        services={"demo": demo_service_cls},
    )

    dump_infrastructure(
        sample_infrastructure,
        infra_path,
        infrastructure_context=infra_context,
    )
    infra_data = json.loads(infra_path.read_text(encoding="utf-8"))
    infra_data.pop("node_assets")
    infra_data.pop("edge_assets")
    infra_path.write_text(json.dumps(infra_data), encoding="utf-8")
    loaded_infra = load_infrastructure(infra_path, infrastructure_context=infra_context)

    assert loaded_infra.nodes["n1"]["cpu"] == 4

    dump_application(
        sample_application_with_service,
        app_path,
        application_context=app_context,
    )
    app_data = json.loads(app_path.read_text(encoding="utf-8"))
    app_data["extras"]["services"]["frontend"] = None
    app_path.write_text(json.dumps(app_data), encoding="utf-8")
    loaded_app = load_application(app_path, application_context=app_context)

    assert "frontend" not in loaded_app.services


def test_wrong_context_type_for_canonical_graphs(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
    sample_application: Application,
):
    infra_path = tmp_path / "infra.json"
    app_path = tmp_path / "app.json"
    dump_infrastructure(sample_infrastructure, infra_path)
    dump_application(sample_application, app_path)

    with pytest.raises(TypeError):
        load_infrastructure(
            infra_path,
            infrastructure_context=IOContext(),  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError):
        load_application(
            app_path,
            application_context=IOContext(),  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError):
        dump_infrastructure(
            sample_infrastructure,
            tmp_path / "other.json",
            infrastructure_context=IOContext(),  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError):
        dump_application(
            sample_application,
            tmp_path / "other-app.json",
            application_context=IOContext(),  # type: ignore[arg-type]
        )
