"""Package for managing simulation reporters, including the off-the-shelf ones."""

from typing import Dict, Type
from eclypse_core.report.reporter import Reporter
from .csv import CSVReporter
from .gml import GMLReporter
from .tensorboard import TensorBoardReporter

__doc__ = Reporter.__doc__ if Reporter.__doc__ else ""


def get_default_reporters() -> Dict[str, Type[Reporter]]:
    """Get the default reporters, comprising CSV, GML, and TensorBoard.

    Returns:
        Dict[str, Type[Reporter]]: The default reporters.
    """
    return {
        "csv": CSVReporter,
        "gml": GMLReporter,
        "tensorboard": TensorBoardReporter,
    }


__all__ = [
    "get_default_reporters",
    "Reporter",
    "CSVReporter",
    "GMLReporter",
    "TensorBoardReporter",
]
