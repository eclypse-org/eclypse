"""Module to configure the loguru logger and print exceptions."""

from __future__ import annotations

import os
import traceback
from sys import (
    stderr,
    stdout,
)
from typing import (
    TYPE_CHECKING,
    Any,
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

    It adds custom ECLYPSE levels for library logs and async exception reports.
    Regular logs are printed to stdout, exception reports are printed to stderr,
    and all logs are saved to a file if the LOG_FILE environment variable is set.
    """
    head = "{time:HH:mm:ss.SSS} | <level>{level}</level> | "
    fmt = head + "<b><level>{extra[id]}</level></b> - <level>{message}</level>"

    # eclypse_head = "{time:HH:mm:ss} | <level>{level.icon} {level}</level> | "
    eclypse_fmt = head + "<b><level>{extra[id]}</level></b> - <white>{message}</white>"
    if "ECLYPSE" not in logger.__dict__["_core"].__dict__["levels"]:
        logger.level("ECLYPSE", no=15, color="<b><magenta>", icon="🌘")
    if "ECLYPSE_EXCEPTION" not in logger.__dict__["_core"].__dict__["levels"]:
        logger.level("ECLYPSE_EXCEPTION", no=45, color="<red>", icon="!")

    exception_fmt = head + "<red>{extra[id]}</red> - <level>{message}</level>"

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
        {
            "sink": stderr,
            "filter": _is_eclypse_exception,
            "format": exception_fmt,
            "colorize": True,
            "level": level,
            "enqueue": True,
        },
    ]
    if file:
        handlers.append({"sink": file, "format": fmt, "enqueue": True, "level": level})
    logger.configure(handlers=handlers)


def _is_eclypse(record: dict[str, Any]):
    return record["level"].name == "ECLYPSE"


def _is_eclypse_exception(record: dict[str, Any]):
    return record["level"].name == "ECLYPSE_EXCEPTION"


def _is_not_eclypse(record: dict[str, Any]):
    return record["level"].name not in {"ECLYPSE", "ECLYPSE_EXCEPTION"}


def print_exception(e: Exception, raised_by: str, exception_logger: Logger):
    """Log an exception traceback and message.

    This is an internal helper used to surface exceptions from asyncio tasks.

    Args:
        e (Exception): The exception raised.
        raised_by (str): The name of the function that raised the exception.
        exception_logger (Logger): Logger bound to the component that caught it.
    """
    tb_lines = traceback.format_tb(e.__traceback__)
    tb_string = "".join(tb_lines)
    exception_logger.log(
        "ECLYPSE_EXCEPTION",
        "Traceback (most recent call last):\n"
        + tb_string
        + f"{e.__class__.__name__} in {raised_by}: {e}",
    )


def format_log_kv(separator: str = " | ", **values: Any) -> str:
    """Format keyword details as compact ``key=value`` pairs.

    Args:
        separator (str): The separator used between key-value pairs.
        **values: The values to format.
    """
    return separator.join(
        f"{key}={value}" for key, value in values.items() if value is not None
    )


def log_placement_violations(vlogger: Logger, violations: dict[str, dict[str, Any]]):
    """Logs each placement violation with aligned formatting using the provided logger.

    Args:
        vlogger (loguru.Logger): A logger instance used to emit warning messages.
        violations (dict[str, dict[str, Any]]):
            A dictionary of violations, where each key maps to a dict
            with 'asset' and 'constraint' values.
    """
    total_pad = max(len(key) for key in violations) + 3  # space +2 accounts for [ and ]

    for key, v in violations.items():
        label = f" [{key}]"
        padded_label = label.rjust(total_pad)
        vlogger.trace(
            f"{padded_label} "
            + format_log_kv(
                available=v["featured"],
                required=v["required"],
            )
        )


def log_assets_violations(
    vlogger: Logger,
    bucket: AssetBucket,
    violations: dict[str, dict[str, Any]],
):
    """Logs each asset violation with aligned formatting using the provided logger.

    Args:
        vlogger (loguru.Logger): A logger instance used to emit warning messages.
        bucket (AssetBucket): The AssetBucket instance containing the assets.
        violations (dict[str, dict[str, Any]]):
            A dictionary of violations, where each key maps to a dict
            with 'asset' and 'constraint' values.
    """
    total_pad = max(len(key) for key in violations) + 3  # space +2 accounts for [ and ]

    for key, v in violations.items():
        label = f" [{key}]"
        padded_label = label.rjust(total_pad)
        vlogger.trace(
            f"{padded_label} "
            + format_log_kv(
                value=v,
                lower_bound=bucket[key].lower_bound,
                upper_bound=bucket[key].upper_bound,
            )
        )


__all__ = [
    "Logger",
    "format_log_kv",
    "log_assets_violations",
    "print_exception",
]

# Configure the default ECLYPSE logging format at import time so components
# created before simulation runtime setup still emit consistently formatted logs.
config_logger()
