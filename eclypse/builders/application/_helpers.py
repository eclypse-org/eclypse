"""Helper functions shared by application builders."""

from __future__ import annotations

from importlib import import_module
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
)

from eclypse.builders._helpers import prune_assets
from eclypse.graph import Application
from eclypse.utils.defaults import SUPPORTED_COMMUNICATION_INTERFACES

if TYPE_CHECKING:
    from collections.abc import Callable

    from eclypse.graph.assets import Asset
    from eclypse.utils.types import (
        CommunicationInterface,
        InitPolicy,
        UpdatePolicies,
    )

    AddFunction = Callable[..., Any]
    IdentifierFactory = Callable[[str], Any]
    EdgeRequirements = tuple[str, str, dict[str, Any]]
    NodeRequirements = dict[str, dict[str, Any]]


def resolve_flows(
    flows: Literal["default"] | list[list[str]],
    default_flows: list[list[str]],
) -> list[list[str]]:
    """Resolve the application flows passed to a builder.

    Args:
        flows (Literal["default"] | list[list[str]]):
            Application flows requested by the caller. Builders pass
            ``"default"`` to select their bundled flow definitions.
        default_flows (list[list[str]]):
            Built-in flows exposed by the builder.

    Returns:
        list[list[str]]: The flows to install on the application.
    """
    if flows == "default":
        return default_flows
    return flows


def build_application(
    application_id: str,
    update_policies: UpdatePolicies,
    node_assets: dict[str, Asset] | None,
    edge_assets: dict[str, Asset] | None,
    include_default_assets: bool,
    requirement_init: InitPolicy,
    flows: list[list[str]],
    seed: int | None,
) -> Application:
    """Create an application instance for a builder.

    Args:
        application_id (str): Identifier assigned to the application.
        update_policies (Callable | list[Callable] | None):
            Graph update policies executed during ``evolve()``.
        node_assets (dict[str, Asset] | None):
            Optional assets attached to application nodes.
        edge_assets (dict[str, Asset] | None):
            Optional assets attached to application edges.
        include_default_assets (bool):
            Whether default graph assets should be included in the application.
        requirement_init (InitPolicy):
            Initialisation strategy applied to node and edge requirements.
        flows (list[list[str]]):
            Application flows to install on the graph.
        seed (int | None):
            Seed forwarded to the application random generator.

    Returns:
        Application: The newly created application instance.
    """
    return Application(
        application_id=application_id,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=edge_assets,
        include_default_assets=include_default_assets,
        requirement_init=requirement_init,
        flows=flows,
        seed=seed,
    )


def resolve_builder_functions(
    app: Application,
    communication_interface: CommunicationInterface | None,
    package_name: str,
    service_names: list[str],
    store_step: bool = False,
) -> tuple[AddFunction, IdentifierFactory]:
    """Resolve the node-creation functions for an application builder.

    Args:
        app (Application): Application being populated by the builder.
        communication_interface (CommunicationInterface | None):
            Communication backend requested by the caller. When ``None``, the
            builder returns graph nodes instead of executable services.
        package_name (str): Package that owns the service implementations.
        service_names (list[str]): Service classes to resolve for the builder.
        store_step (bool): Whether instantiated services should store their
            step outputs in the internal step queue.

    Returns:
        tuple[AddFunction, IdentifierFactory]:
            A pair containing the application add function and an identifier
            factory that returns either service ids or instantiated services.

    Raises:
        ValueError: If ``communication_interface`` is not supported.
    """
    if communication_interface is None:
        return app.add_node, lambda service_id: service_id

    if communication_interface not in SUPPORTED_COMMUNICATION_INTERFACES:
        raise ValueError(
            f"Unknown communication interface: {communication_interface}",
        )

    services = import_module(
        f".{communication_interface}_services",
        package=package_name,
    )
    classes = {
        service_name: getattr(services, service_name) for service_name in service_names
    }
    return app.add_service, lambda service_id: classes[service_id](
        service_id,
        store_step=store_step,
    )


def populate_application_topology(
    app: Application,
    add_fn: AddFunction,
    id_fn: IdentifierFactory,
    node_requirements: NodeRequirements,
    edge_requirements: list[EdgeRequirements],
) -> None:
    """Populate the nodes and edges of an application.

    Args:
        app (Application): Application being populated.
        add_fn (AddFunction): Function used to add nodes or services.
        id_fn (IdentifierFactory): Factory returning the object to add for each
            service identifier.
        node_requirements (dict[str, dict[str, Any]]):
            Resource and QoS requirements keyed by service name.
        edge_requirements (list[EdgeRequirements]):
            Communication requirements keyed by source-target service pairs.
            Each item contains source id, target id, and edge attributes.
    """
    for service_id, requirements in node_requirements.items():
        add_fn(
            id_fn(service_id),
            **prune_assets(app.node_assets, **requirements),
        )

    for source, target, requirements in edge_requirements:
        edge_data = dict(requirements)
        symmetric = edge_data.pop("symmetric", True)
        app.add_edge(
            source,
            target,
            symmetric=symmetric,
            **prune_assets(app.edge_assets, **edge_data),
        )


def build_application_from_specs(
    application_id: str,
    communication_interface: CommunicationInterface | None,
    update_policies: UpdatePolicies,
    node_assets: dict[str, Asset] | None,
    edge_assets: dict[str, Asset] | None,
    include_default_assets: bool,
    requirement_init: InitPolicy,
    flows: Literal["default"] | list[list[str]],
    default_flows: list[list[str]],
    service_names: list[str],
    node_requirements: NodeRequirements,
    edge_requirements: list[EdgeRequirements],
    seed: int | None,
    package_name: str,
    store_step: bool = False,
) -> Application:
    """Build and populate an application from declarative builder specs.

    Args:
        application_id (str): Identifier assigned to the generated application.
        communication_interface (CommunicationInterface | None):
            Communication backend used to instantiate executable services. When
            ``None``, the builder returns a graph-only application.
        update_policies (Callable | list[Callable] | None):
            Graph update policies executed during ``evolve()``.
        node_assets (dict[str, Asset] | None):
            Optional assets attached to application nodes.
        edge_assets (dict[str, Asset] | None):
            Optional assets attached to application edges.
        include_default_assets (bool):
            Whether default graph assets should be included in the application.
        requirement_init (InitPolicy):
            Initialisation strategy applied to node and edge requirements.
        flows (Literal["default"] | list[list[str]]):
            Application flows requested by the caller.
        default_flows (list[list[str]]):
            Built-in flows exposed by the builder.
        service_names (list[str]):
            Service classes to resolve for the builder.
        node_requirements (NodeRequirements):
            Resource and QoS requirements keyed by service name.
        edge_requirements (list[EdgeRequirements]):
            Communication requirements keyed by source-target service pairs.
        seed (int | None):
            Seed forwarded to the application random generator.
        package_name (str): Package that owns the service implementations.
        store_step (bool):
            Whether instantiated services should store their step outputs in
            the internal step queue. Ignored when ``communication_interface``
            is ``None``.

    Returns:
        Application: The configured application instance.

    Raises:
        ValueError: If ``communication_interface`` is not supported.
    """
    app = build_application(
        application_id=application_id,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=edge_assets,
        include_default_assets=include_default_assets,
        requirement_init=requirement_init,
        flows=resolve_flows(flows, default_flows),
        seed=seed,
    )
    add_fn, id_fn = resolve_builder_functions(
        app=app,
        communication_interface=communication_interface,
        package_name=package_name,
        service_names=service_names,
        store_step=store_step,
    )
    populate_application_topology(
        app=app,
        add_fn=add_fn,
        id_fn=id_fn,
        node_requirements=node_requirements,
        edge_requirements=edge_requirements,
    )
    return app


__all__ = [
    "build_application",
    "build_application_from_specs",
    "populate_application_topology",
    "resolve_builder_functions",
    "resolve_flows",
]
