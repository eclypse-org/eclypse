from __future__ import annotations

import ast
from itertools import pairwise
from pathlib import Path

import pytest

from eclypse.builders.application import (
    get_anomaly_detection,
    get_crud_api,
    get_hotel_reservation,
    get_keyword_spotting,
    get_sock_shop,
    get_thumbnailer,
    get_video_analytics_serving,
)

_FLOW_CONSISTENT_BUILDERS = [
    get_video_analytics_serving,
    get_hotel_reservation,
    get_crud_api,
    get_keyword_spotting,
    get_anomaly_detection,
    get_thumbnailer,
]

_CALL_CONSISTENT_BUILDERS = [
    *_FLOW_CONSISTENT_BUILDERS,
    get_sock_shop,
]

_REST_METHODS = {"delete", "get", "patch", "post", "put"}


class _RuntimeCallCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls: set[tuple[str, str]] = set()
        self._class_name: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        previous_class_name = self._class_name
        self._class_name = node.name
        self.generic_visit(node)
        self._class_name = previous_class_name

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if self._class_name is not None:
            mpi_target = _extract_mpi_send_target(node)
            if mpi_target is not None:
                self.calls.add((self._class_name, mpi_target))

            rest_target = _extract_rest_target(node)
            if rest_target is not None:
                self.calls.add((self._class_name, rest_target))

        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:  # noqa: N802
        if self._class_name is not None:
            target = _extract_return_target(node.value)
            if target is not None:
                self.calls.add((self._class_name, target))

        self.generic_visit(node)


def _extract_mpi_send_target(node: ast.Call) -> str | None:
    if _is_self_method_call(node, namespace="mpi", methods={"send"}):
        return _first_string_argument(node)
    return None


def _extract_rest_target(node: ast.Call) -> str | None:
    if not _is_self_method_call(node, namespace="rest", methods=_REST_METHODS):
        return None

    endpoint = _first_string_argument(node)
    if endpoint is None:
        return None
    return endpoint.split("/", maxsplit=1)[0]


def _extract_return_target(node: ast.AST | None) -> str | None:
    if not isinstance(node, ast.Tuple):
        return None
    if not node.elts:
        return None
    first_element = node.elts[0]
    if isinstance(first_element, ast.Constant) and isinstance(
        first_element.value,
        str,
    ):
        return first_element.value
    return None


def _first_string_argument(node: ast.Call) -> str | None:
    if not node.args:
        return None
    first_argument = node.args[0]
    if isinstance(first_argument, ast.Constant) and isinstance(
        first_argument.value,
        str,
    ):
        return first_argument.value
    return None


def _is_self_method_call(
    node: ast.Call,
    namespace: str,
    methods: set[str],
) -> bool:
    if not isinstance(node.func, ast.Attribute):
        return False
    if node.func.attr not in methods:
        return False
    if not isinstance(node.func.value, ast.Attribute):
        return False
    if node.func.value.attr != namespace:
        return False
    if not isinstance(node.func.value.value, ast.Name):
        return False
    return node.func.value.value.id == "self"


def _collect_runtime_calls(builder) -> set[tuple[str, str]]:
    package_path = Path(builder.__globals__["__file__"]).resolve().parent
    calls: set[tuple[str, str]] = set()
    for services_directory in ("mpi_services", "rest_services"):
        for file_path in sorted((package_path / services_directory).glob("*.py")):
            if file_path.name == "__init__.py":
                continue
            collector = _RuntimeCallCollector()
            collector.visit(ast.parse(file_path.read_text(), filename=str(file_path)))
            calls.update(collector.calls)
    return calls


@pytest.mark.parametrize("builder", _FLOW_CONSISTENT_BUILDERS)
def test_flows_match_topology(builder):
    app = builder()

    for flow in app.flows:
        for source, target in pairwise(flow):
            assert app.has_edge(source, target), (builder.__name__, source, target)


@pytest.mark.parametrize("builder", _CALL_CONSISTENT_BUILDERS)
def test_calls_match_topology(builder):
    app = builder()

    for source, target in sorted(_collect_runtime_calls(builder)):
        assert app.has_edge(source, target), (builder.__name__, source, target)
