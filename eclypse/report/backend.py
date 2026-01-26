"""Abstract base class for Report DataFrame backends.

This module defines the FrameBackend abstract base class used by Report to
perform IO and filtering operations without depending on a specific DataFrame
library (e.g. pandas or polars).

Backends are implemented as subclasses providing concrete behaviour.
"""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Iterable,
    Set,
)


class FrameBackend(ABC):
    """Abstract base class defining the minimal DataFrame backend API.

    Subclasses must implement CSV reading and filtering primitives required by
    Report. This keeps Report independent from a concrete DataFrame library.
    """

    def __init__(self, name: str):
        """Initialize the FrameBackend.

        Args:
            name: The backend name.
        """
        self._name = name

    @abstractmethod
    def read_csv(self, path: str) -> Any:
        """Read a CSV file into a backend-specific DataFrame.

        Args:
            path: Path to the CSV file.

        Returns:
            A backend-specific DataFrame instance.
        """
        raise NotImplementedError

    @abstractmethod
    def is_empty(self, df: Any) -> bool:
        """Return whether the DataFrame is empty.

        Args:
            df: The DataFrame to inspect.

        Returns:
            True if the DataFrame has no rows, otherwise False.
        """
        raise NotImplementedError

    @abstractmethod
    def columns(self, df: Any) -> Set[str]:
        """Return the set of column names.

        Args:
            df: The DataFrame to inspect.

        Returns:
            A set containing the DataFrame column names.
        """
        raise NotImplementedError

    @abstractmethod
    def max(self, df: Any, col: str) -> int:
        """Return the maximum value of an integer-like column.

        Args:
            df: The DataFrame to inspect.
            col: The name of the column.

        Returns:
            The maximum value as a Python int.
        """
        raise NotImplementedError

    @abstractmethod
    def filter_events(self, df: Any, col: str, events: Iterable[int]) -> Any:
        """Filter rows where `col` is contained in `events`.

        Args:
            df: The DataFrame to filter.
            col: The column name to test membership against.
            events: The allowed values for `col`.

        Returns:
            A filtered DataFrame.
        """
        raise NotImplementedError

    @abstractmethod
    def filter_eq(self, df: Any, col: str, value: Any) -> Any:
        """Filter rows where `col` equals `value`.

        Args:
            df: The DataFrame to filter.
            col: The column name to compare.
            value: The value to match.

        Returns:
            A filtered DataFrame.
        """
        raise NotImplementedError

    @abstractmethod
    def filter_in(self, df: Any, col: str, values: Iterable[Any]) -> Any:
        """Filter rows where `col` is contained in `values`.

        Args:
            df: The DataFrame to filter.
            col: The column name to test membership against.
            values: The allowed values for `col`.

        Returns:
            A filtered DataFrame.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Return the backend name.

        Returns:
            A short backend identifier (e.g. "pandas", "polars", "polars_lazy").
        """
        return self._name
