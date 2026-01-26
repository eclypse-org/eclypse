"""Package for managing simulation reporters, including the off-the-shelf ones.

If you are interested in creating HTML reports, use the
`eclypse-html-report <https://pypi.org/project/eclypse-html-report>` CLI tool.
"""

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
from .tensorboard import TensorBoardReporter


def get_default_reporters(
    requested_reporters: Optional[List[str]],
) -> Dict[str, Callable[..., Reporter]]:
    """Get the default reporters, comprising CSV, GML, JSON, and TensorBoard.

    Args:
        requested_reporters (Optional[List[str]]): The list of requested reporters.

    Returns:
        Dict[str, Type[Reporter]]: The default reporters.
    """
    default_reporters = {
        "csv": CSVReporter,
        "gml": GMLReporter,
        "json": JSONReporter,
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
    "Reporter",
    "TensorBoardReporter",
    "get_default_reporters",
]
