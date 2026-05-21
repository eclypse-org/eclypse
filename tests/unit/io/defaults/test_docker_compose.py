from __future__ import annotations

from pathlib import Path

import pytest

from eclypse.graph import Application
from eclypse.io import (
    DockerComposeContext,
    dump_application,
    load_application,
)
from eclypse.io.defaults.docker_compose import DockerComposeImporter


def test_docker_compose_application_round_trip(
    tmp_path: Path,
    sample_application: Application,
):
    path = tmp_path / "docker-compose.yaml"
    sample_application.nodes["frontend"]["image"] = "frontend"
    sample_application.nodes["worker"]["image"] = "worker"

    dump_application(sample_application, path)
    loaded = load_application(path)

    assert loaded.id == "app"
    assert loaded.has_edge("frontend", "worker")
    assert loaded.edges["frontend", "worker"]["latency"] == 10
    assert loaded.flows == [["frontend", "worker"]]
    assert loaded.nodes["frontend"]["image"] == "frontend"
    assert loaded.nodes["frontend"]["cpu"] == 1


def test_docker_compose_importer_rejects_infrastructure_kind():
    with pytest.raises(ValueError):
        DockerComposeImporter().from_data({"services": {}}, kind="infrastructure")


def test_docker_compose_exporter_requires_image_or_build(
    tmp_path: Path,
    sample_application: Application,
):
    path = tmp_path / "docker-compose.yaml"

    with pytest.raises(ValueError, match="requires 'image' or 'build'"):
        dump_application(sample_application, path)


def test_docker_compose_exporter_accepts_build_without_image(
    tmp_path: Path,
    sample_application: Application,
):
    path = tmp_path / "docker-compose.yaml"
    sample_application.nodes["frontend"]["build"] = "."
    sample_application.nodes["worker"]["image"] = "worker"

    dump_application(sample_application, path)
    loaded = load_application(path)

    assert loaded.nodes["frontend"]["build"] == "."


def test_docker_compose_exporter_can_fallback_to_node_name(
    tmp_path: Path,
    sample_application: Application,
):
    path = tmp_path / "docker-compose.yaml"
    context = DockerComposeContext(allow_image_fallback_to_node=True)

    dump_application(sample_application, path, application_context=context)
    loaded = load_application(path)

    assert loaded.nodes["frontend"]["image"] == "frontend"
    assert loaded.nodes["worker"]["image"] == "worker"


def test_docker_compose_importer_requires_services_mapping():
    with pytest.raises(ValueError, match="top-level 'services' mapping"):
        DockerComposeImporter().from_data({})


def test_docker_compose_importer_requires_service_mapping():
    with pytest.raises(ValueError, match="must be a mapping"):
        DockerComposeImporter().from_data({"services": {"frontend": None}})


def test_docker_compose_importer_requires_image_or_build():
    with pytest.raises(ValueError, match="requires 'image' or 'build'"):
        DockerComposeImporter().from_data({"services": {"frontend": {}}})


def test_docker_compose_importer_can_relax_image_or_build_requirement():
    context = DockerComposeContext(require_service_image_or_build=False)

    loaded = DockerComposeImporter().from_data(
        {
            "services": {
                "frontend": {
                    "depends_on": {
                        "worker": {"condition": "service_started"},
                    },
                },
                "worker": {},
                "cache": {"depends_on": "worker"},
            },
        },
        context=context,
    )

    assert list(loaded.nodes) == ["frontend", "worker", "cache"]
    assert loaded.has_edge("frontend", "worker")
    assert loaded.has_edge("cache", "worker")

    loaded_without_services = DockerComposeImporter().from_data(
        {},
        context=DockerComposeContext(require_services=False),
    )
    assert list(loaded_without_services.nodes) == []
