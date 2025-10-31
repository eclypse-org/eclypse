"""Module to configure the loguru logger and print exceptions."""

from __future__ import annotations

import os
import traceback
from sys import stdout
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

from loguru import logger
from loguru._logger import Logger

from eclypse.utils.constants import (
    LOG_FILE,
    LOG_LEVEL,
)

if TYPE_CHECKING:
    from eclypse.graph.assets.bucket import AssetBucket


def config_logger():
    """Configure the loguru logger.

    It adds a custom level ECLYPSE for the logs related to the Eclypse library. The logs
    are printed to stdout and saved to a file if the LOG_FILE environment variable is
    set.
    """
    head = "{time:HH:mm:ss.SSS} | <level>{level}</level> | "
    fmt = head + "<b><level>{extra[id]}</level></b> - <level>{message}</level>"

    # eclypse_head = "{time:HH:mm:ss} | <level>{level.icon} {level}</level> | "
    eclypse_fmt = head + "<b><level>{extra[id]}</level></b> - <white>{message}</white>"
    if "ECLYPSE" not in logger.__dict__["_core"].__dict__["levels"]:
        logger.level("ECLYPSE", no=15, color="<b><magenta>", icon="🌘")

    level = os.getenv(LOG_LEVEL, "ECLYPSE")
    file = os.getenv(LOG_FILE)

    handlers = [
        {
            "sink": stdout,
            "filter": _is_not_eclypse,
            "format": fmt,
            "colorize": True,
            "level": level,
            "enqueue": True,
        },
        {
            "sink": stdout,
            "filter": _is_eclypse,
            "format": eclypse_fmt,
            "colorize": True,
            "level": level,
            "enqueue": True,
        },
    ]
    if file:
        handlers.append({"sink": file, "format": fmt, "enqueue": True, "level": level})
    logger.configure(handlers=handlers)


def _is_eclypse(record: Dict[str, Any]):
    return record["level"].name == "ECLYPSE"


def _is_not_eclypse(record: Dict[str, Any]):
    return record["level"].name != "ECLYPSE"


def print_exception(e: Exception, raised_by: str):
    """Print the exception traceback and message.

    This is an internal function used to catch and print exception from asyncio tasks.

    Args:
        e (Exception): The exception raised.
        raised_by (str): The name of the function that raised the exception.
    """
    tb_lines = traceback.format_tb(e.__traceback__)
    tb_string = "".join(tb_lines)
    print("Traceback (most recent call last):")
    print(tb_string)
    print(f"{e.__class__.__name__} in {raised_by}: {e}")


def log_placement_violations(vlogger: Logger, violations: Dict[str, Dict[str, Any]]):
    """Logs each placement violation with aligned formatting using the provided logger.

    Args:
        vlogger (loguru.Logger): A logger instance used to emit warning messages.
        violations (Dict[str, Dict[str, Any]]): A dictionary of violations, where each key
            maps to a dict with 'asset' and 'constraint' values.
    """
    total_pad = max(len(key) for key in violations) + 3  # +2 accounts for [ and ]

    for key, v in violations.items():
        label = f" [{key}]"
        padded_label = label.rjust(total_pad)
        vlogger.warning(
            f"{padded_label} featured {v['featured']} | required {v['required']}"
        )


def log_assets_violations(
    vlogger: Logger,
    bucket: AssetBucket,
    violations: Dict[str, Dict[str, Any]],
):
    """Logs each asset violation with aligned formatting using the provided logger.

    Args:
        vlogger (loguru.Logger): A logger instance used to emit warning messages.
        bucket (AssetBucket): The AssetBucket instance containing the assets.
        violations (Dict[str, Dict[str, Any]]): A dictionary of violations, where each key
            maps to a dict with 'asset' and 'constraint' values.
    """
    total_pad = max(len(key) for key in violations) + 3  # +2 accounts for [ and ]

    for key, v in violations.items():
        label = f" [{key}]"
        padded_label = label.rjust(total_pad)
        vlogger.warning(
            f"{padded_label} | "
            f"{v} upper_bound {bucket[key].upper_bound} | "
            f"lower_bound {bucket[key].lower_bound}"
        )


__all__ = ["Logger", "log_placement_violations", "print_exception"]
