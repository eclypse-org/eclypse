"""Registry of built-in ECLYPSE graph importers and exporters."""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
    replace,
)
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from eclypse.io.base import (
        GraphExporter,
        GraphImporter,
    )
    from eclypse.utils.types import GraphKind


@dataclass(slots=True, frozen=True)
class IORegistry:
    """Immutable registry of importer and exporter classes.

    Args:
        importers (Mapping[tuple[GraphKind, str], type[GraphImporter]]):
            Importer classes
            keyed by ``(kind, format)``.
        exporters (Mapping[tuple[GraphKind, str], type[GraphExporter]]):
            Exporter classes
            keyed by ``(kind, format)``.
    """

    importers: Mapping[tuple[GraphKind, str], type[GraphImporter]] = field(
        default_factory=dict
    )
    exporters: Mapping[tuple[GraphKind, str], type[GraphExporter]] = field(
        default_factory=dict
    )

    def __post_init__(self):
        """Freeze registry mappings after initialisation."""
        object.__setattr__(self, "importers", MappingProxyType(dict(self.importers)))
        object.__setattr__(self, "exporters", MappingProxyType(dict(self.exporters)))

    def get_importer(self, kind: GraphKind, format: str) -> type[GraphImporter]:
        """Return the importer class registered for a graph kind and format.

        Args:
            kind (GraphKind): The graph kind, such as ``"infrastructure"``.
            format (str): The IO format, such as ``"gml"``.

        Returns:
            type[GraphImporter]: The registered importer class.

        Raises:
            ValueError: If no importer is registered for the pair.
        """
        key = (kind, format)
        try:
            return self.importers[key]
        except KeyError as exc:
            raise ValueError(
                f"No importer registered for kind {kind!r} and format {format!r}."
            ) from exc

    def get_exporter(self, kind: GraphKind, format: str) -> type[GraphExporter]:
        """Return the exporter class registered for a graph kind and format.

        Args:
            kind (GraphKind): The graph kind, such as ``"application"``.
            format (str): The IO format, such as ``"graphml"``.

        Returns:
            type[GraphExporter]: The registered exporter class.

        Raises:
            ValueError: If no exporter is registered for the pair.
        """
        key = (kind, format)
        try:
            return self.exporters[key]
        except KeyError as exc:
            raise ValueError(
                f"No exporter registered for kind {kind!r} and format {format!r}."
            ) from exc

    def with_importer(
        self,
        kind: GraphKind,
        format: str,
        importer: type[GraphImporter],
    ) -> IORegistry:
        """Return a copy of the registry with an additional importer.

        Args:
            kind (GraphKind): The graph kind.
            format (str): The IO format.
            importer (type[GraphImporter]): The importer class to register.

        Returns:
            IORegistry: A new registry containing the additional importer.
        """
        return replace(self, importers={**self.importers, (kind, format): importer})

    def with_exporter(
        self,
        kind: GraphKind,
        format: str,
        exporter: type[GraphExporter],
    ) -> IORegistry:
        """Return a copy of the registry with an additional exporter.

        Args:
            kind (GraphKind): The graph kind.
            format (str): The IO format.
            exporter (type[GraphExporter]): The exporter class to register.

        Returns:
            IORegistry: A new registry containing the additional exporter.
        """
        return replace(self, exporters={**self.exporters, (kind, format): exporter})

    def formats(self, kind: GraphKind, *, direction: str = "export") -> list[str]:
        """Return registered formats for a graph kind.

        Args:
            kind (GraphKind): The graph kind.
            direction (str): Either ``"export"`` or ``"import"``.

        Returns:
            list[str]: The registered format names sorted alphabetically.

        Raises:
            ValueError: If ``direction`` is not supported.
        """
        if direction == "export":
            mapping: Mapping[tuple[GraphKind, str], Any] = self.exporters
        elif direction == "import":
            mapping = self.importers
        else:
            raise ValueError("direction must be 'export' or 'import'.")

        return sorted(
            format for registered_kind, format in mapping if registered_kind == kind
        )
