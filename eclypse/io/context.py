"""Import/export context objects used by ECLYPSE IO codecs."""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.graph.assets.defaults import (
    get_default_edge_assets,
    get_default_node_assets,
    get_default_path_aggregators,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from eclypse.graph.assets import Asset
    from eclypse.remote.service import Service
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


@dataclass(slots=True)
class IOContext:
    """Common customisation context for AssetGraph import and export.

    The context contains only options that map to the common
    :class:`~eclypse.graph.asset_graph.AssetGraph` construction and population
    behaviour.

    Args:
        node_assets (dict[str, Asset] | None): Node asset schema used when an import
            format does not carry asset definitions.
        edge_assets (dict[str, Asset] | None): Edge asset schema used when an import
            format does not carry asset definitions.
        update_policies (UpdatePolicies): Graph update policies attached on import.
        seed (int | None): Seed forwarded to imported graphs.
    """

    node_assets: dict[str, Asset] | None = None
    edge_assets: dict[str, Asset] | None = None
    update_policies: UpdatePolicies = None
    seed: int | None = None


@dataclass(slots=True)
class InfrastructureContext(IOContext):
    """Customisation context for infrastructure import and export.

    Args:
        strict (bool): Whether imported nodes and edges should be validated strictly.
            Defaults to ``False``, matching
            :class:`~eclypse.graph.infrastructure.Infrastructure`.
        include_default_assets (bool): Whether the imported infrastructure should
            include default assets when the format does not carry asset definitions.
            Defaults to ``True``, matching
            :class:`~eclypse.graph.infrastructure.Infrastructure`.
        resource_init (InitPolicy): Resource initialisation policy used when a format
            does not carry one. Defaults to ``"min"``, matching
            :class:`~eclypse.graph.infrastructure.Infrastructure`.
        path_assets_aggregators (dict[str, Callable[[list[Any]], Any]] | None):
            Named path aggregators used to reconstruct infrastructure path-resource
            aggregation. Defaults to ECLYPSE path aggregators only when
            ``include_default_assets`` is ``True``.
    """

    strict: bool = False
    include_default_assets: bool = True
    resource_init: InitPolicy = "min"
    path_assets_aggregators: dict[str, Callable[[list[Any]], Any]] | None = None

    def __post_init__(self):
        """Fill default assets and path aggregators when requested."""
        if not self.include_default_assets:
            return
        if self.node_assets is None:
            self.node_assets = get_default_node_assets()
        if self.edge_assets is None:
            self.edge_assets = get_default_edge_assets()
        if self.path_assets_aggregators is None:
            self.path_assets_aggregators = get_default_path_aggregators()

    def get_aggregator(self, name: str) -> Callable[[list[Any]], Any]:
        """Return a registered path aggregator.

        Args:
            name (str): The aggregator name.

        Returns:
            Callable[[list[Any]], Any]: The registered aggregator.

        Raises:
            ValueError: If no aggregator is registered with the given name.
        """
        if self.path_assets_aggregators is None:
            raise ValueError(f"Unknown path aggregator: {name}")
        try:
            return self.path_assets_aggregators[name]
        except KeyError as exc:
            raise ValueError(f"Unknown path aggregator: {name}") from exc


@dataclass(slots=True)
class ApplicationContext(IOContext):
    """Customisation context for application import and export.

    Args:
        strict (bool): Whether imported nodes and edges should be validated strictly.
            Defaults to ``True``, matching
            :class:`~eclypse.graph.application.Application` through
            :class:`~eclypse.graph.asset_graph.AssetGraph`.
        include_default_assets (bool): Whether the imported application should include
            default assets when the format does not carry asset definitions. Defaults
            to ``True``, matching :class:`~eclypse.graph.application.Application`.
        requirement_init (InitPolicy): Requirement initialisation policy used when a
            format does not carry one. Defaults to ``"min"``, matching
            :class:`~eclypse.graph.application.Application`.
        services (dict[str, type[Service]]): Service classes used when an
            application importer needs to instantiate service implementations.
    """

    strict: bool = True
    include_default_assets: bool = True
    requirement_init: InitPolicy = "min"
    services: dict[str, type[Service]] = field(default_factory=dict)

    def __post_init__(self):
        """Fill default assets when requested."""
        if not self.include_default_assets:
            return
        if self.node_assets is None:
            self.node_assets = get_default_node_assets()
        if self.edge_assets is None:
            self.edge_assets = get_default_edge_assets()

    def get_service(self, name: str) -> type[Service]:
        """Return a registered service class.

        Args:
            name (str): The service registry name.

        Returns:
            type[Service]: The registered service class.

        Raises:
            ValueError: If no service is registered with the given name.
        """
        try:
            return self.services[name]
        except KeyError as exc:
            raise ValueError(f"Unknown service implementation: {name}") from exc


@dataclass(slots=True)
class DockerComposeContext(ApplicationContext):
    """Customisation context for Docker Compose application import and export.

    Args:
        require_services (bool): Whether imported Docker Compose data must contain
            the required top-level ``services`` mapping. Defaults to ``True``.
        require_service_image_or_build (bool): Whether every service must define
            either ``image`` or ``build``. Defaults to ``True``.
        allow_image_fallback_to_node (bool): Whether exports may use the ECLYPSE node
            id as Docker image when neither ``image`` nor ``container_image`` nor
            ``build`` is present. Defaults to ``False``.
    """

    require_services: bool = True
    require_service_image_or_build: bool = True
    allow_image_fallback_to_node: bool = False


@dataclass(slots=True)
class TOSCAApplicationContext(ApplicationContext):
    """Customisation context for TOSCA application import and export.

    Args:
        require_definitions_version (bool): Whether imported TOSCA data must contain
            the required ``tosca_definitions_version`` field. Defaults to ``True``.
        require_node_template_types (bool): Whether every imported node template must
            contain the required ``type`` field. Defaults to ``True``.
    """

    require_definitions_version: bool = True
    require_node_template_types: bool = True


@dataclass(slots=True)
class TOSCAInfrastructureContext(InfrastructureContext):
    """Customisation context for TOSCA infrastructure import and export.

    Args:
        require_definitions_version (bool): Whether imported TOSCA data must contain
            the required ``tosca_definitions_version`` field. Defaults to ``True``.
        require_node_template_types (bool): Whether every imported node template must
            contain the required ``type`` field. Defaults to ``True``.
    """

    require_definitions_version: bool = True
    require_node_template_types: bool = True
