"""Composable query builder for report frames."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.utils.defaults import (
    DEFAULT_REPORT_RANGE,
    DEFAULT_REPORT_STEP,
)

if TYPE_CHECKING:
    from eclypse.utils.types import EventType

    from .report import Report


class ReportQuery:
    """Composable query builder for report frames."""

    def __init__(self, report: Report, report_type: EventType):
        """Create a query builder bound to a report type."""
        self._report = report
        self._report_type = report_type
        self._report_range: tuple[int, int] = DEFAULT_REPORT_RANGE
        self._report_step = DEFAULT_REPORT_STEP
        self._filters: dict[str, Any] = {}

    def range(self, start: int, stop: int) -> ReportQuery:
        """Set the inclusive event range."""
        self._report_range = (start, stop)
        return self

    def step(self, step: int) -> ReportQuery:
        """Set the report step."""
        self._report_step = step
        return self

    def where(self, **filters: Any) -> ReportQuery:
        """Add equality or membership filters."""
        self._filters.update(filters)
        return self

    def to_frame(self) -> Any:
        """Materialise the current query into a backend frame."""
        return self._report.frame(
            self._report_type,
            report_range=self._report_range,
            report_step=self._report_step,
            **self._filters,
        )
