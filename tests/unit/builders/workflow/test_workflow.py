from __future__ import annotations

import re
import sys
import types
from dataclasses import (
    dataclass,
    field,
)
from types import SimpleNamespace

import networkx as nx
import pytest

from eclypse.builders.workflow import get_workflow
from eclypse.builders.workflow._helpers import (
    _copy_workflow_metadata,
    _edge_asset_values,
    _shared_output_input_files,
    _task_asset_values,
    _task_metadata,
    coerce_workflow_base_method,
    coerce_workflow_family,
    derive_workflow_flows,
)
from eclypse.builders.workflow.base_method import WorkflowBaseMethod
from eclypse.builders.workflow.workflow_family import WorkflowFamily
from eclypse.graph import Application

_BYTES_PER_MIB = 2**20


@dataclass
class _FakeFile:
    file_id: str
    size: int


@dataclass
class _FakeTaskType:
    name: str


@dataclass
class _FakeTask:
    name: str
    task_id: str
    runtime: float
    cores: int
    memory: int | None = None
    bytes_read: int | None = None
    bytes_written: int | None = None
    input_files: list[_FakeFile] = field(default_factory=list)
    output_files: list[_FakeFile] = field(default_factory=list)
    category: str | None = None
    program: str | None = None
    args: list[str] = field(default_factory=list)
    machines: list[str] = field(default_factory=list)
    priority: int | None = None
    type: _FakeTaskType | None = None
    start_time: str | None = None


class _FakeWorkflow(nx.DiGraph):
    def __init__(self):
        super().__init__()
        self.name = "Montage-synthetic-instance"
        self.description = "Synthetic workflow"
        self.workflow_id = "wf-1"
        self.created_at = "2026-01-01T00:00:00+00:00"
        self.executed_at = None
        self.makespan = 42.0
        self.schema_version = "1.5"
        self.runtime_system_name = "WfCommons"
        self.runtime_system_url = "https://wfcommons.org"
        self.runtime_system_version = "1.0"
        self.author_name = "OpenAI"
        self.author_email = "test@example.com"
        self.author_institution = "OpenAI"
        self.author_country = "IT"
        self.graph["source"] = "fake"

    def roots(self):
        return [node_id for node_id, degree in self.in_degree() if degree == 0]

    def leaves(self):
        return [node_id for node_id, degree in self.out_degree() if degree == 0]


def _install_fake_wfcommons(monkeypatch: pytest.MonkeyPatch):
    calls: dict[str, object] = {}

    class _FakeBaseMethod:
        ERROR_TABLE = "ERROR_TABLE"
        SMALLEST = "SMALLEST"
        BIGGEST = "BIGGEST"
        RANDOM = "RANDOM"

    class _FakeRecipe:
        def __init__(self, **kwargs):
            calls["recipe_kwargs"] = kwargs

    class _FakeWorkflowGenerator:
        def __init__(self, recipe):
            calls["recipe"] = recipe

        def build_workflow(self, workflow_name=None):
            calls["workflow_name"] = workflow_name

            workflow = _FakeWorkflow()

            raw = _FakeFile("raw.fits", 100)
            projected = _FakeFile("projected.fits", 200)
            diff = _FakeFile("diff.tbl", 300)

            source = _FakeTask(
                name="mProject",
                task_id="mProject_0001",
                runtime=12.5,
                cores=2,
                memory=64,
                input_files=[raw],
                output_files=[projected],
                program="mProject",
                args=["--input", "raw.fits"],
                type=_FakeTaskType("COMPUTE"),
                start_time="2026-01-01T00:00:00+00:00",
            )
            middle = _FakeTask(
                name="mDiffFit",
                task_id="mDiffFit_0002",
                runtime=20.0,
                cores=4,
                bytes_read=200,
                bytes_written=300,
                input_files=[projected],
                output_files=[diff],
                program="mDiffFit",
                type=_FakeTaskType("AUXILIARY"),
            )
            sink = _FakeTask(
                name="mAdd",
                task_id="mAdd_0003",
                runtime=5.0,
                cores=1,
                input_files=[diff],
                output_files=[],
                program="mAdd",
                type=_FakeTaskType("TRANSFER"),
            )

            workflow.add_node(source.task_id, task=source, label=source.task_id)
            workflow.add_node(middle.task_id, task=middle, label=middle.task_id)
            workflow.add_node(sink.task_id, task=sink, label=sink.task_id)
            workflow.add_edge(source.task_id, middle.task_id, weight=1)
            workflow.add_edge(middle.task_id, sink.task_id, weight=2)
            return workflow

    wfcommons = types.ModuleType("wfcommons")
    for recipe_name in (
        "BlastRecipe",
        "BwaRecipe",
        "CyclesRecipe",
        "EpigenomicsRecipe",
        "GenomeRecipe",
        "MontageRecipe",
        "RnaseqRecipe",
        "SeismologyRecipe",
        "SoykbRecipe",
        "SrasearchRecipe",
    ):
        setattr(wfcommons, recipe_name, _FakeRecipe)
    wfcommons.WorkflowGenerator = _FakeWorkflowGenerator

    wfchef_module = types.ModuleType("wfcommons.wfchef")
    abstract_module = types.ModuleType("wfcommons.wfchef.wfchef_abstract_recipe")
    abstract_module.BaseMethod = _FakeBaseMethod

    monkeypatch.setitem(sys.modules, "wfcommons", wfcommons)
    monkeypatch.setitem(sys.modules, "wfcommons.wfchef", wfchef_module)
    monkeypatch.setitem(
        sys.modules,
        "wfcommons.wfchef.wfchef_abstract_recipe",
        abstract_module,
    )
    monkeypatch.setattr(
        "eclypse.builders.workflow._helpers._require_module",
        lambda *_args, **_kwargs: None,
    )
    return calls


def test_get_workflow(monkeypatch: pytest.MonkeyPatch):
    calls = _install_fake_wfcommons(monkeypatch)

    application = get_workflow(
        workflow="montage",
        num_tasks=100,
        data_footprint=1024,
        runtime_factor=2.0,
        input_file_size_factor=3.0,
        output_file_size_factor=4.0,
        base_method="random",
        workflow_name="wf-name",
        seed=7,
    )

    assert calls["recipe_kwargs"] == {
        "data_footprint": 1024,
        "num_tasks": 100,
        "exclude_graphs": None,
        "runtime_factor": 2.0,
        "input_file_size_factor": 3.0,
        "output_file_size_factor": 4.0,
        "base_method": "RANDOM",
    }
    assert calls["workflow_name"] == "wf-name"

    assert application.id == "Montage-synthetic-instance"
    assert application.graph["workflow_backend"] == "wfcommons"
    assert application.graph["workflow_family"] == "montage"
    assert application.graph["source"] == "fake"

    assert application.flows == [
        ["mProject_0001", "mDiffFit_0002", "mAdd_0003"],
    ]

    assert application.nodes["mProject_0001"]["cpu"] == 2.0
    assert application.nodes["mProject_0001"]["ram"] == 64.0
    assert application.nodes["mProject_0001"]["storage"] == pytest.approx(
        300 / _BYTES_PER_MIB,
    )
    assert application.nodes["mProject_0001"]["processing_time"] == 12.5
    assert application.nodes["mProject_0001"]["workflow_task_type"] == "COMPUTE"
    assert application.nodes["mProject_0001"][
        "workflow_input_size_mib"
    ] == pytest.approx(
        100 / _BYTES_PER_MIB,
    )
    assert application.nodes["mProject_0001"][
        "workflow_output_size_mib"
    ] == pytest.approx(
        200 / _BYTES_PER_MIB,
    )

    assert application.nodes["mDiffFit_0002"]["storage"] == pytest.approx(
        500 / _BYTES_PER_MIB,
    )
    assert application["mProject_0001"]["mDiffFit_0002"]["bandwidth"] == pytest.approx(
        200 / _BYTES_PER_MIB,
    )
    assert application["mProject_0001"]["mDiffFit_0002"][
        "workflow_transferred_size_mib"
    ] == pytest.approx(200 / _BYTES_PER_MIB)
    assert application["mProject_0001"]["mDiffFit_0002"]["weight"] == 1

    assert "latency" in application["mProject_0001"]["mDiffFit_0002"]
    assert "availability" in application.nodes["mProject_0001"]
    assert coerce_workflow_family(WorkflowFamily.MONTAGE) is WorkflowFamily.MONTAGE
    assert (
        coerce_workflow_base_method(WorkflowBaseMethod.RANDOM)
        is WorkflowBaseMethod.RANDOM
    )

    plain_workflow = nx.DiGraph()
    plain_workflow.add_edges_from([("a", "b"), ("c", "d")])
    assert derive_workflow_flows(plain_workflow) == [["a", "b"], ["c", "d"]]

    metadata_application = Application()
    _copy_workflow_metadata(
        metadata_application,
        SimpleNamespace(graph=object()),
        WorkflowFamily.MONTAGE,
    )
    assert metadata_application.graph["workflow_backend"] == "wfcommons"
    assert metadata_application.graph["workflow_family"] == "montage"

    partial_task = SimpleNamespace(
        cores=None,
        memory=None,
        runtime=None,
        input_files=[],
        output_files=[],
        bytes_read=None,
        bytes_written=None,
    )
    assert _task_asset_values(None) == {}
    assert _task_asset_values(partial_task) == {}
    assert _task_metadata(None) == {}
    assert _edge_asset_values(None, None) == {}
    assert _shared_output_input_files(None, partial_task) == {}
    assert (
        _shared_output_input_files(
            SimpleNamespace(output_files=[SimpleNamespace(file_id=None, size=1)]),
            partial_task,
        )
        == {}
    )


def test_get_workflow_uses_family_minimum_when_num_tasks_is_omitted(
    monkeypatch: pytest.MonkeyPatch,
):
    calls = _install_fake_wfcommons(monkeypatch)

    get_workflow(workflow="genome")

    assert calls["recipe_kwargs"]["num_tasks"] == 54


def test_get_workflow_allows_custom_application_id_and_flows(
    monkeypatch: pytest.MonkeyPatch,
):
    _install_fake_wfcommons(monkeypatch)

    application = get_workflow(
        workflow="montage",
        application_id="custom-workflow",
        flows=[["mProject_0001", "mAdd_0003"]],
    )

    assert application.id == "custom-workflow"
    assert application.flows == [["mProject_0001", "mAdd_0003"]]


def test_get_workflow_rejects_too_small_num_tasks(
    monkeypatch: pytest.MonkeyPatch,
):
    _install_fake_wfcommons(monkeypatch)

    with pytest.raises(
        ValueError,
        match=re.escape("Workflow family 'genome' requires num_tasks >= 54, got 10."),
    ):
        get_workflow("genome", num_tasks=10)

    with pytest.raises(ValueError, match="Unknown workflow family"):
        coerce_workflow_family("unknown")
    with pytest.raises(ValueError, match="Unknown workflow base method"):
        coerce_workflow_base_method("unknown")


def test_get_workflow_requires_wfcommons(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "eclypse.builders.workflow._helpers._require_module",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ImportError(
                "wfcommons is not installed. Please install it with 'pip install wfcommons'."
            )
        ),
    )

    with pytest.raises(ImportError, match="pip install wfcommons"):
        get_workflow("montage")
