from __future__ import annotations

from pathlib import Path

import pytest

from eclypse.graph import (
    Application,
    Infrastructure,
)
from eclypse.io import (
    TOSCAApplicationContext,
    dump_application,
    dump_infrastructure,
    load_application,
    load_infrastructure,
)
from eclypse.io.context import InfrastructureContext
from eclypse.io.defaults.tosca import (
    COMPUTE_TYPE,
    DEPENDS_ON_RELATIONSHIP,
    HOSTED_ON_RELATIONSHIP,
    LINKS_TO_RELATIONSHIP,
    NETWORK_TYPE,
    PORT_TYPE,
    SOFTWARE_COMPONENT_TYPE,
    TOSCA_VERSION,
    TOSCAExporter,
    TOSCAImporter,
)


def test_tosca_application_round_trip(
    tmp_path: Path,
    sample_application: Application,
):
    path = tmp_path / "app.tosca.yaml"

    dump_application(sample_application, path)
    loaded = load_application(path)
    data = TOSCAImporter().read_data(path)

    assert data["tosca_definitions_version"] == TOSCA_VERSION
    assert data["topology_template"]["node_templates"]["frontend"]["type"] == (
        SOFTWARE_COMPONENT_TYPE
    )
    dependency = data["topology_template"]["node_templates"]["frontend"][
        "requirements"
    ][0]["dependency"]
    assert dependency == {
        "node": "worker",
        "relationship": DEPENDS_ON_RELATIONSHIP,
    }
    assert loaded.id == "app"
    assert loaded.has_edge("frontend", "worker")
    assert loaded.edges["frontend", "worker"]["latency"] == 10
    assert loaded.flows == [["frontend", "worker"]]


def test_tosca_infrastructure_round_trip(
    tmp_path: Path,
    sample_infrastructure: Infrastructure,
):
    path = tmp_path / "infra.tosca.yaml"

    dump_infrastructure(sample_infrastructure, path)
    loaded = load_infrastructure(path)
    data = TOSCAImporter().read_data(path)
    node_templates = data["topology_template"]["node_templates"]

    assert node_templates["n1"]["type"] == COMPUTE_TYPE
    assert node_templates["n1"]["capabilities"]["host"]["properties"] == {
        "num_cpus": 4,
        "mem_size": "8 GB",
    }
    assert node_templates["n1_n2_network"]["type"] == NETWORK_TYPE
    assert node_templates["n1_n2_n1_port"]["type"] == PORT_TYPE
    assert node_templates["n1_n2_n1_port"]["requirements"] == [
        {
            "binding": {
                "node": "n1",
                "relationship": HOSTED_ON_RELATIONSHIP,
            },
        },
        {
            "link": {
                "node": "n1_n2_network",
                "relationship": LINKS_TO_RELATIONSHIP,
            },
        },
    ]
    assert loaded.id == "infra"
    assert loaded.has_edge("n1", "n2")
    assert loaded.edges["n1", "n2"]["bandwidth"] == 20


def test_tosca_importer_reads_standard_application_tosca():
    data = {
        "tosca_definitions_version": TOSCA_VERSION,
        "metadata": {"template_name": "standard-app"},
        "node_types": {
            "AppComponent": {
                "derived_from": SOFTWARE_COMPONENT_TYPE,
            },
        },
        "topology_template": {
            "node_templates": {
                "frontend": {
                    "type": "AppComponent",
                    "requirements": [
                        {
                            "backend": {
                                "node": "api",
                                "relationship": DEPENDS_ON_RELATIONSHIP,
                            },
                        },
                    ],
                },
                "api": {
                    "type": SOFTWARE_COMPONENT_TYPE,
                },
                "host": {
                    "type": COMPUTE_TYPE,
                },
            },
        },
    }

    loaded = TOSCAImporter().from_data(data, kind="application")

    assert isinstance(loaded, Application)
    assert loaded.id == "standard-app"
    assert sorted(loaded.nodes) == ["api", "frontend"]
    assert loaded.has_edge("frontend", "api")


def test_tosca_importer_reads_standard_infrastructure_tosca():
    data = {
        "tosca_definitions_version": TOSCA_VERSION,
        "metadata": {"template_name": "standard-infra"},
        "topology_template": {
            "node_templates": {
                "node_a": {
                    "type": "Compute",
                    "capabilities": {
                        "host": {
                            "properties": {
                                "num_cpus": 2,
                                "mem_size": "4 GB",
                            },
                        },
                    },
                },
                "node_b": {
                    "type": COMPUTE_TYPE,
                },
                "private_net": {
                    "type": NETWORK_TYPE,
                    "properties": {
                        "network_name": "private_net",
                    },
                },
                "port_a": {
                    "type": PORT_TYPE,
                    "requirements": [
                        {"binding": "node_a"},
                        {"link": "private_net"},
                    ],
                },
                "port_b": {
                    "type": PORT_TYPE,
                    "requirements": [
                        {"binding": "node_b"},
                        {"link": "private_net"},
                    ],
                },
            },
        },
    }

    loaded = TOSCAImporter().from_data(
        data,
        kind="infrastructure",
        context=InfrastructureContext(include_default_assets=False),
    )

    assert isinstance(loaded, Infrastructure)
    assert loaded.id == "standard-infra"
    assert loaded.nodes["node_a"] == {"cpu": 2, "ram": 4}
    assert loaded.has_edge("node_a", "node_b")
    assert loaded.has_edge("node_b", "node_a")
    assert loaded.edges["node_a", "node_b"]["network_name"] == "private_net"


def test_tosca_importer_rejects_kind_conflicts():
    data = {
        "tosca_definitions_version": TOSCA_VERSION,
        "metadata": {"eclypse_kind": "application"},
        "topology_template": {"node_templates": {}},
    }

    with pytest.raises(ValueError):
        TOSCAImporter().from_data(data, kind="infrastructure")

    data["metadata"]["eclypse_kind"] = "unsupported"
    with pytest.raises(ValueError, match="Unsupported graph kind"):
        TOSCAImporter().from_data(data)


@pytest.mark.parametrize(
    ("topology", "message"),
    [
        ([], "'topology_template' must be a mapping"),
        ({"node_templates": []}, "node_templates' must be a mapping"),
        ({"node_templates": {"bad": []}}, "'bad' must be a mapping"),
    ],
)
def test_tosca_importer_rejects_malformed_mappings(topology, message):
    with pytest.raises(ValueError, match=message):
        TOSCAImporter().from_data(
            {
                "tosca_definitions_version": TOSCA_VERSION,
                "topology_template": topology,
            }
        )


@pytest.mark.parametrize(
    ("node_type", "graph_type"),
    [(SOFTWARE_COMPONENT_TYPE, Application), (COMPUTE_TYPE, Infrastructure)],
)
def test_tosca_importer_infers_kind_without_metadata(node_type, graph_type):
    loaded = TOSCAImporter().from_data(
        {
            "tosca_definitions_version": TOSCA_VERSION,
            "topology_template": {
                "node_templates": {"node": {"type": node_type}},
            },
        }
    )

    assert isinstance(loaded, graph_type)
    assert list(loaded.nodes) == ["node"]


@pytest.mark.parametrize("memory", [4, "4.5 GB", "unknown"])
def test_tosca_importer_preserves_numeric_and_unrecognised_sizes(memory):
    loaded = TOSCAImporter().from_data(
        {
            "tosca_definitions_version": TOSCA_VERSION,
            "topology_template": {
                "node_templates": {
                    "node": {
                        "type": COMPUTE_TYPE,
                        "capabilities": {"host": {"properties": {"mem_size": memory}}},
                    },
                },
            },
        },
        context=InfrastructureContext(include_default_assets=False),
    )

    assert loaded.nodes["node"]["ram"] == (4.5 if memory == "4.5 GB" else memory)


def test_tosca_importer_requires_definitions_version():
    data = {
        "topology_template": {
            "node_templates": {
                "frontend": {
                    "type": SOFTWARE_COMPONENT_TYPE,
                },
            },
        },
    }

    with pytest.raises(ValueError, match="tosca_definitions_version"):
        TOSCAImporter().from_data(data, kind="application")


def test_tosca_importer_requires_node_template_type():
    data = {
        "tosca_definitions_version": TOSCA_VERSION,
        "topology_template": {
            "node_templates": {
                "frontend": {},
            },
        },
    }

    with pytest.raises(ValueError, match="requires a 'type' field"):
        TOSCAImporter().from_data(data, kind="application")


def test_tosca_importer_can_relax_required_fields():
    context = TOSCAApplicationContext(
        require_definitions_version=False,
        require_node_template_types=False,
    )
    data = {
        "metadata": {"template_name": "loose"},
        "topology_template": {
            "node_templates": {
                "frontend": {},
            },
        },
    }

    loaded = TOSCAImporter().from_data(
        data,
        kind="application",
        context=context,
    )

    assert isinstance(loaded, Application)
    assert list(loaded.nodes) == ["frontend"]


@pytest.mark.parametrize("attrs", [{}, {"ram": "8 GB"}, {"cpu": 2}])
def test_tosca_exports_partial_host_capabilities(attrs):
    graph = Infrastructure("partial")
    graph.add_node("node", **attrs)
    template = TOSCAExporter().to_data(graph)["topology_template"]["node_templates"][
        "node"
    ]
    assert template["type"] == COMPUTE_TYPE
    expected = {}
    if "ram" in attrs:
        expected["mem_size"] = attrs["ram"]
    if "cpu" in attrs:
        expected["num_cpus"] = attrs["cpu"]
    if expected:
        assert template["capabilities"]["host"]["properties"] == expected
    else:
        assert "capabilities" not in template


def test_tosca_ignores_malformed_unresolved_and_incomplete_requirements():
    data = {
        "tosca_definitions_version": TOSCA_VERSION,
        "topology_template": {
            "node_templates": {
                "frontend": {
                    "type": SOFTWARE_COMPONENT_TYPE,
                    "requirements": [None, {}, {"bad": 42}, {"external": "missing"}],
                },
                "port": {"type": PORT_TYPE, "requirements": [{"link": "network"}]},
            }
        },
    }
    application = TOSCAImporter().from_data(data, kind="application")
    assert list(application.nodes) == ["frontend"]
    assert list(application.edges) == []
    infrastructure = TOSCAImporter().from_data(data, kind="infrastructure")
    assert list(infrastructure.edges) == []
