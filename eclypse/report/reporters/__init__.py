from eclypse_core.report.reporter import Reporter
from .csv import CSVReporter
from .gml import GMLReporter
from .tensorboard import TensorBoardReporter

__doc__ = Reporter.__doc__ if Reporter.__doc__ else ""


def get_default_reporters():
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
