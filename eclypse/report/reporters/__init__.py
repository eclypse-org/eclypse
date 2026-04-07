"""Package for managing simulation reporters, including the off-the-shelf ones."""

from eclypse.report.reporter import Reporter
from eclypse.utils.defaults import (
    CSV_REPORT_DIR,
    GML_REPORT_DIR,
    JSON_REPORT_DIR,
    PARQUET_REPORT_DIR,
    TENSORBOARD_REPORT_DIR,
)
from .csv import CSVReporter
from .gml import GMLReporter
from .json import JSONReporter
from .parquet import ParquetReporter
from .tensorboard import TensorBoardReporter


def get_default_reporters(
    requested_reporters: list[str] | None,
) -> dict[str, type[Reporter]]:
    """Get the default reporters, comprising CSV, GML, JSON, Parquet, and TensorBoard.

    Args:
        requested_reporters (list[str] | None): The list of requested reporters.

    Returns:
        dict[str, type[Reporter]]: The default reporters.
    """
    default_reporters: dict[str, type[Reporter]] = {
        CSV_REPORT_DIR: CSVReporter,
        GML_REPORT_DIR: GMLReporter,
        JSON_REPORT_DIR: JSONReporter,
        PARQUET_REPORT_DIR: ParquetReporter,
        TENSORBOARD_REPORT_DIR: TensorBoardReporter,
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
    "TensorBoardReporter",
    "get_default_reporters",
]
