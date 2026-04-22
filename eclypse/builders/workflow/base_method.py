"""Workflow generation base methods."""

from __future__ import annotations

from enum import StrEnum


class WorkflowBaseMethod(StrEnum):
    """Base graph selection strategies supported by WfCommons recipes."""

    ERROR_TABLE = "error_table"
    SMALLEST = "smallest"
    BIGGEST = "biggest"
    RANDOM = "random"


__all__ = ["WorkflowBaseMethod"]
