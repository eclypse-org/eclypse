"""Base I/O plugin interface for Infrastructure/Application data handling."""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path
from typing import (
    Literal,
    Optional,
    Union,
)

from rpds import List

from eclypse.graph import (
    Application,
    Infrastructure,
)
from eclypse.io.registry import get_validator


class BaseIOPlugin(ABC):
    """Abstract base class for I/O plugins.

    Plugins must implement the `load` and `dump` methods.
    """

    def load(
        self,
        path: Union[str, Path],
        as_type: Literal["application", "infrastructure"] = "infrastructure",
        validators: Optional[List[str]] = None,
        fallback: Literal["strict", "warning", "ignore"] = "strict",
    ) -> Union[Infrastructure, Application]:
        """Load a graph (infrastructure or application) from a file.

        Args:
            path (str): Path to the file.
            as_type (Literal["application", "infrastructure"]): Type of graph to load.
                Defaults to "infrastructure".
            validators (Optional[List[str]]): List of validator names to apply.
                Defaults to None.
            fallback (Literal["strict", "warning", "ignore"]): Fallback behaviour
                if validation fails. Defaults to "strict".

        Returns:
            Union[Infrastructure, Application]: The loaded graph object.
        """
        if as_type not in {"application", "infrastructure"}:
            raise ValueError(
                f"Invalid type '{as_type}'. Expected 'application' or 'infrastructure'."
            )
        if fallback not in {"strict", "warning", "ignore"}:
            raise ValueError(
                f"Invalid fallback '{fallback}'. Expected 'strict', 'warning', or 'ignore'."
            )

        raw_graph = self.parse(path)
        # TODO: allow AssetGraph to be built from a raw_graph
        graph = (
            Infrastructure(raw_graph)
            if as_type == "infrastructure"
            else Application(raw_graph)
        )

        if validators:
            for name in validators:
                validator_fn = get_validator(name)
                try:
                    validator_fn(graph)
                except Exception as e:
                    if fallback == "strict":
                        raise
                    elif fallback == "warning":
                        graph.logger.warning(f"Validator '{name}' failed: {e}")
                    # if fallback == "ignore", skip silently

        return graph

    @abstractmethod
    def parse(self, path: Union[str, Path]) -> Union[Application, Infrastructure]:
        """Load a graph (infrastructure or application) from a file."""

    @abstractmethod
    def serialize(
        self, graph: Union[Application, Infrastructure], path: Union[str, Path]
    ):
        """Dump a graph (infrastructure or application) to a file.

        Args:
            graph (Union[Application, Infrastructure]): The graph to dump.
            path (Union[str, Path]): Path to the output file.
        """
