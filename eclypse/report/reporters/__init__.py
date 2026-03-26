"""Package for managing simulation reporters, including the off-the-shelf ones."""

from typing import (
    Callable,
    Dict,
    List,
    Optional,
)

from eclypse.report import Reporter

from .csv import CSVReporter
from .gml import GMLReporter
from .json import JSONReporter
from .parquet import ParquetReporter
from .tensorboard import TensorBoardReporter


def get_default_reporters(
    requested_reporters: Optional[List[str]],
) -> Dict[str, Callable[..., Reporter]]:
    """Get the default reporters, comprising CSV, GML, JSON, Parquet, and TensorBoard.

    Args:
        requested_reporters (Optional[List[str]]): The list of requested reporters.

    Returns:
        Dict[str, Type[Reporter]]: The default reporters.
    """
    default_reporters = {
        "csv": CSVReporter,
        "gml": GMLReporter,
        "json": JSONReporter,
        "parquet": ParquetReporter,
        "tensorboard": TensorBoardReporter,
    }

    return (
        {k: v for k, v in default_reporters.items() if k in requested_reporters}
        if requested_reporters
        else {}
    )


__all__ = [
    "CSVReporter",
    "GMLReporter",
    "JSONReporter",
    "ParquetReporter",
    "Reporter",
    "TensorBoardReporter",
    "get_default_reporters",
]
