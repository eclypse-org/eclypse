"""Helper functions shared by workflow builders."""

from __future__ import annotations

import random
from contextlib import contextmanager
from importlib import import_module
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

import networkx as nx

from eclypse.builders._helpers import prune_assets
from eclypse.graph import Application
from eclypse.graph.assets.defaults import (
    get_default_edge_assets,
    get_default_node_assets,
)
from eclypse.simulation.config import _require_module

from .base_method import WorkflowBaseMethod
from .workflow_family import WorkflowFamily

if TYPE_CHECKING:
    from collections.abc import Iterator

    from eclypse.graph.assets import Asset
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


_MIN_TASKS = {
    WorkflowFamily.BLAST: 45,
    WorkflowFamily.BWA: 106,
    WorkflowFamily.CYCLES: 69,
    WorkflowFamily.EPIGENOMICS: 43,
    WorkflowFamily.GENOME: 54,
    WorkflowFamily.MONTAGE: 60,
    WorkflowFamily.RNASEQ: 65,
    WorkflowFamily.SEISMOLOGY: 103,
    WorkflowFamily.SOYKB: 98,
    WorkflowFamily.SRASEARCH: 24,
}

_BYTES_PER_MIB = 2**20


def coerce_workflow_family(
    workflow: WorkflowFamily | str,
) -> WorkflowFamily:
    """Return a workflow family enum from user input."""
    if isinstance(workflow, WorkflowFamily):
        return workflow

    normalized = workflow.strip().lower()
    for candidate in WorkflowFamily:
        if candidate.value == normalized:
            return candidate

    valid = ", ".join(member.value for member in WorkflowFamily)
    raise ValueError(f"Unknown workflow family: {workflow}. Expected one of: {valid}")


def coerce_workflow_base_method(
    base_method: WorkflowBaseMethod | str,
) -> WorkflowBaseMethod:
    """Return a workflow base-method enum from user input."""
    if isinstance(base_method, WorkflowBaseMethod):
        return base_method

    normalized = base_method.strip().lower()
    for candidate in WorkflowBaseMethod:
        if candidate.value == normalized:
            return candidate

    valid = ", ".join(member.value for member in WorkflowBaseMethod)
    raise ValueError(
        f"Unknown workflow base method: {base_method}. Expected one of: {valid}",
    )


def build_workflow_application(
    workflow: WorkflowFamily | str,
    num_tasks: int | None = None,
    data_footprint: int | None = 0,
    exclude_graphs: set[str] | None = None,
    runtime_factor: float | None = 1.0,
    input_file_size_factor: float | None = 1.0,
    output_file_size_factor: float | None = 1.0,
    base_method: WorkflowBaseMethod | str = WorkflowBaseMethod.ERROR_TABLE,
    workflow_name: str | None = None,
    application_id: str | None = None,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    edge_assets: dict[str, Asset] | None = None,
    requirement_init: InitPolicy = "min",
    flows: list[list[str]] | str = "default",
    seed: int | None = None,
) -> Application:
    """Build a simulation-only workflow application from WfCommons."""
    workflow_family = coerce_workflow_family(workflow)
    workflow_base_method = coerce_workflow_base_method(base_method)
    resolved_num_tasks = validate_num_tasks(workflow_family, num_tasks)

    recipe_class, wfcommons_base_method, workflow_generator_class = _load_wfcommons(
        workflow_family,
        workflow_base_method,
    )

    recipe = recipe_class(
        data_footprint=data_footprint,
        num_tasks=resolved_num_tasks,
        exclude_graphs=exclude_graphs,
        runtime_factor=runtime_factor,
        input_file_size_factor=input_file_size_factor,
        output_file_size_factor=output_file_size_factor,
        base_method=wfcommons_base_method,
    )

    generator = workflow_generator_class(recipe)
    with _temporary_random_seed(seed):
        generated_workflow = generator.build_workflow(workflow_name)

    _application_id = application_id or generated_workflow.name
    _flows = (
        derive_workflow_flows(generated_workflow)
        if flows == "default"
        else cast("list[list[str]]", flows)
    )
    default_node_assets = get_default_node_assets(with_init=False)
    default_edge_assets = get_default_edge_assets(with_init=False)
    default_node_assets.update(node_assets or {})
    default_edge_assets.update(edge_assets or {})

    application = Application(
        application_id=_application_id,
        update_policies=update_policies,
        node_assets=default_node_assets,
        edge_assets=default_edge_assets,
        include_default_assets=False,
        requirement_init=requirement_init,
        flows=_flows,
        seed=seed,
    )

    _copy_workflow_metadata(application, generated_workflow, workflow_family)

    for node_id, node_data in generated_workflow.nodes(data=True):
        task = node_data.get("task")
        node_requirements = _task_asset_values(task)
        metadata = _task_metadata(task)
        metadata.update(
            {key: value for key, value in node_data.items() if key != "task"}
        )
        application.add_node(
            str(node_id),
            strict=False,
            **prune_assets(application.node_assets, **node_requirements),
            **metadata,
        )

    for source, target, edge_data in generated_workflow.edges(data=True):
        source_task = generated_workflow.nodes[source].get("task")
        target_task = generated_workflow.nodes[target].get("task")
        edge_requirements = _edge_asset_values(source_task, target_task)
        metadata = _edge_metadata(source_task, target_task, edge_data)
        application.add_edge(
            str(source),
            str(target),
            symmetric=False,
            strict=False,
            **prune_assets(application.edge_assets, **edge_requirements),
            **metadata,
        )

    return application


def derive_workflow_flows(workflow: nx.DiGraph) -> list[list[str]]:
    """Derive default root-to-leaf flows from a workflow DAG."""
    roots = list(_workflow_roots(workflow))
    leaves = list(_workflow_leaves(workflow))
    resolved: set[tuple[str, ...]] = set()

    for root in roots:
        for leaf in leaves:
            if not nx.has_path(workflow, root, leaf):
                continue
            for path in nx.all_simple_paths(workflow, root, leaf):
                resolved.add(tuple(str(node_id) for node_id in path))

    return [list(path) for path in sorted(resolved)]


def validate_num_tasks(
    workflow_family: WorkflowFamily,
    num_tasks: int | None,
) -> int:
    """Resolve and validate the number of tasks for a workflow family."""
    minimum = _MIN_TASKS[workflow_family]
    resolved = minimum if num_tasks is None else num_tasks

    if resolved < minimum:
        raise ValueError(
            f"Workflow family '{workflow_family.value}' requires "
            f"num_tasks >= {minimum}, got {resolved}.",
        )

    return resolved


def _load_wfcommons(
    workflow_family: WorkflowFamily,
    base_method: WorkflowBaseMethod,
) -> tuple[type[Any], Any, type[Any]]:
    """Resolve the WfCommons recipe, base method, and generator classes."""
    _require_module("wfcommons")

    wfcommons = import_module("wfcommons")
    wfcommons_abstract_recipe = import_module("wfcommons.wfchef.wfchef_abstract_recipe")
    WfCommonsBaseMethod = wfcommons_abstract_recipe.BaseMethod

    recipe_names = {
        WorkflowFamily.BLAST: "BlastRecipe",
        WorkflowFamily.BWA: "BwaRecipe",
        WorkflowFamily.CYCLES: "CyclesRecipe",
        WorkflowFamily.EPIGENOMICS: "EpigenomicsRecipe",
        WorkflowFamily.GENOME: "GenomeRecipe",
        WorkflowFamily.MONTAGE: "MontageRecipe",
        WorkflowFamily.RNASEQ: "RnaseqRecipe",
        WorkflowFamily.SEISMOLOGY: "SeismologyRecipe",
        WorkflowFamily.SOYKB: "SoykbRecipe",
        WorkflowFamily.SRASEARCH: "SrasearchRecipe",
    }

    recipe_class = getattr(wfcommons, recipe_names[workflow_family])
    wfcommons_base_method = getattr(WfCommonsBaseMethod, base_method.name)
    return recipe_class, wfcommons_base_method, wfcommons.WorkflowGenerator


@contextmanager
def _temporary_random_seed(seed: int | None) -> Iterator[None]:
    """Temporarily seed the Python random module for WfCommons generation."""
    if seed is None:
        yield
        return

    state = random.getstate()
    random.seed(seed)
    try:
        yield
    finally:
        random.setstate(state)


def _workflow_roots(workflow: nx.DiGraph) -> list[Any]:
    """Return the roots of a workflow graph."""
    if hasattr(workflow, "roots") and callable(workflow.roots):
        return list(workflow.roots())
    return [node_id for node_id, degree in workflow.in_degree() if degree == 0]


def _workflow_leaves(workflow: nx.DiGraph) -> list[Any]:
    """Return the leaves of a workflow graph."""
    if hasattr(workflow, "leaves") and callable(workflow.leaves):
        return list(workflow.leaves())
    return [node_id for node_id, degree in workflow.out_degree() if degree == 0]


def _copy_workflow_metadata(
    application: Application,
    workflow: Any,
    workflow_family: WorkflowFamily,
) -> None:
    """Copy graph-level workflow metadata into the application graph."""
    application.graph["workflow_backend"] = "wfcommons"
    application.graph["workflow_family"] = workflow_family.value

    for key in (
        "name",
        "description",
        "workflow_id",
        "created_at",
        "executed_at",
        "makespan",
        "schema_version",
        "runtime_system_name",
        "runtime_system_url",
        "runtime_system_version",
        "author_name",
        "author_email",
        "author_institution",
        "author_country",
    ):
        value = getattr(workflow, key, None)
        if value is not None:
            application.graph[key] = value

    graph_metadata = getattr(workflow, "graph", {})
    if isinstance(graph_metadata, dict):
        application.graph.update(
            {key: value for key, value in graph_metadata.items() if key not in {"task"}}
        )


def _task_asset_values(task: Any) -> dict[str, float]:
    """Map task metadata onto default ECLYPSE node assets.

    Workflow storage requirements are normalised from raw WfCommons byte counts to MiB
    before they are assigned to the ECLYPSE ``storage`` asset.
    """
    if task is None:
        return {}

    task_storage = _task_storage(task)
    values: dict[str, float] = {}

    if getattr(task, "cores", None) is not None:
        values["cpu"] = float(task.cores)
    if getattr(task, "memory", None) is not None:
        values["ram"] = float(task.memory)
    if task_storage is not None:
        values["storage"] = float(task_storage)
    if getattr(task, "runtime", None) is not None:
        values["processing_time"] = float(task.runtime)

    return values


def _task_metadata(task: Any) -> dict[str, Any]:
    """Return task metadata that does not map to default assets."""
    if task is None:
        return {}

    input_files = list(getattr(task, "input_files", []))
    output_files = list(getattr(task, "output_files", []))
    task_type = getattr(task, "type", None)

    metadata: dict[str, Any] = {
        "workflow_task_name": getattr(task, "name", None),
        "workflow_task_program": getattr(task, "program", None),
        "workflow_task_category": getattr(task, "category", None),
        "workflow_task_priority": getattr(task, "priority", None),
        "workflow_task_start_time": getattr(task, "start_time", None),
        "workflow_task_type": getattr(task_type, "name", None),
        "workflow_input_files": [
            getattr(file, "file_id", None) for file in input_files
        ],
        "workflow_output_files": [
            getattr(file, "file_id", None) for file in output_files
        ],
        "workflow_input_size_mib": _bytes_to_mib(_total_file_size(input_files)),
        "workflow_output_size_mib": _bytes_to_mib(_total_file_size(output_files)),
        "workflow_args": list(getattr(task, "args", [])),
        "workflow_machines": list(getattr(task, "machines", [])),
        "workflow_bytes_read": getattr(task, "bytes_read", None),
        "workflow_bytes_written": getattr(task, "bytes_written", None),
    }
    return {key: value for key, value in metadata.items() if value is not None}


def _edge_asset_values(source_task: Any, target_task: Any) -> dict[str, float]:
    """Map workflow dependency metadata onto default ECLYPSE edge assets.

    Dependency transfer sizes are normalised from raw WfCommons byte counts to MiB
    before they are assigned to the ECLYPSE ``bandwidth`` asset.
    """
    transferred_size = _transferred_size(source_task, target_task)
    if transferred_size is None:
        return {}
    return {"bandwidth": float(transferred_size)}


def _edge_metadata(
    source_task: Any,
    target_task: Any,
    edge_data: dict[str, Any],
) -> dict[str, Any]:
    """Return edge metadata for a workflow dependency."""
    transferred_files = _shared_output_input_files(source_task, target_task)
    metadata = dict(edge_data)
    metadata["workflow_transferred_files"] = list(transferred_files)
    metadata["workflow_transferred_size_mib"] = _bytes_to_mib(
        sum(transferred_files.values()),
    )
    return metadata


def _task_storage(task: Any) -> float | None:
    """Return the storage footprint associated with a workflow task in MiB."""
    input_size = _total_file_size(getattr(task, "input_files", []))
    output_size = _total_file_size(getattr(task, "output_files", []))
    bytes_read = getattr(task, "bytes_read", None) or 0
    bytes_written = getattr(task, "bytes_written", None) or 0
    storage = max(int(input_size + output_size), int(bytes_read + bytes_written))
    return _bytes_to_mib(storage)


def _transferred_size(source_task: Any, target_task: Any) -> float | None:
    """Return the total size of files transferred across a workflow edge in MiB."""
    shared_files = _shared_output_input_files(source_task, target_task)
    transferred_size = sum(shared_files.values())
    return _bytes_to_mib(transferred_size)


def _shared_output_input_files(source_task: Any, target_task: Any) -> dict[str, int]:
    """Return the files produced by the source and consumed by the target."""
    if source_task is None or target_task is None:
        return {}

    source_outputs: dict[str, int] = {}
    for file in getattr(source_task, "output_files", []):
        file_id = getattr(file, "file_id", None)
        if file_id is None:
            continue
        source_outputs[str(file_id)] = int(getattr(file, "size", 0) or 0)

    target_inputs = {
        str(getattr(file, "file_id", None))
        for file in getattr(target_task, "input_files", [])
        if getattr(file, "file_id", None)
    }

    return {
        file_id: size
        for file_id, size in source_outputs.items()
        if file_id in target_inputs
    }


def _total_file_size(files: list[Any]) -> int:
    """Return the total size of a list of workflow files."""
    return sum(int(getattr(file, "size", 0) or 0) for file in files)


def _bytes_to_mib(size_in_bytes: int) -> float | None:
    """Convert a byte count into MiB, returning ``None`` for zero values."""
    return (size_in_bytes / _BYTES_PER_MIB) or None


__all__ = [
    "WorkflowBaseMethod",
    "WorkflowFamily",
    "build_workflow_application",
    "coerce_workflow_base_method",
    "coerce_workflow_family",
    "derive_workflow_flows",
    "validate_num_tasks",
]
