"""Abstract base classes for ECLYPSE graph importers and exporters."""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    Generic,
)

from eclypse.utils.types import (
    TData,
    TGraph,
)

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.io.context import IOContext
    from eclypse.utils.types import GraphKind


class GraphExporter(ABC, Generic[TGraph, TData]):
    """Base class for graph exporters.

    Exporters convert an ECLYPSE graph object into an intermediate data representation,
    then write that representation to a destination. Subclasses normally implement
    :meth:`to_data` and :meth:`write_data`.
    """

    def dump(
        self, graph: TGraph, target: str | Path, *, context: IOContext | None = None
    ) -> None:
        """Export a graph object to the provided target.

        Args:
            graph (TGraph): The graph object to export.
            target (str | Path): The target path where the graph is written.
            context (IOContext | None): Optional import/export customisation.
        """
        data = self.to_data(graph, context=context)
        self.write_data(data, target, context=context)

    @abstractmethod
    def to_data(self, graph: TGraph, *, context: IOContext | None = None) -> TData:
        """Convert a graph object into the exporter intermediate representation.

        Args:
            graph (TGraph): The graph object to convert.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            TData: The intermediate representation handled by :meth:`write_data`.
        """

    @abstractmethod
    def write_data(
        self, data: TData, target: str | Path, *, context: IOContext | None = None
    ) -> None:
        """Write exporter data to a target.

        Args:
            data (TData): The intermediate representation to write.
            target (str | Path): The target path where data is written.
            context (IOContext | None): Optional import/export customisation.
        """


class GraphImporter(ABC, Generic[TGraph, TData]):
    """Base class for graph importers.

    Importers read a source into an intermediate data representation, then build an
    ECLYPSE graph object from that representation. Subclasses normally implement
    :meth:`read_data` and :meth:`from_data`.
    """

    def load(
        self,
        source: str | Path,
        *,
        kind: GraphKind | None = None,
        context: IOContext | None = None,
    ) -> TGraph:
        """Import a graph object from the provided source.

        Args:
            source (str | Path): The source path to read.
            kind (GraphKind | None): Optional graph kind requested by the caller.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            TGraph: The imported graph object.
        """
        data = self.read_data(source, context=context)
        return self.from_data(data, kind=kind, context=context)

    @abstractmethod
    def read_data(
        self, source: str | Path, *, context: IOContext | None = None
    ) -> TData:
        """Read importer data from a source.

        Args:
            source (str | Path): The source path to read.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            TData: The intermediate representation handled by :meth:`from_data`.
        """

    @abstractmethod
    def from_data(
        self,
        data: TData,
        *,
        kind: GraphKind | None = None,
        context: IOContext | None = None,
    ) -> TGraph:
        """Convert importer data into a graph object.

        Args:
            data (TData): The intermediate representation to convert.
            kind (GraphKind | None): Optional graph kind requested by the caller.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            TGraph: The imported graph object.
        """
