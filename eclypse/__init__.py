# pylint: disable=missing-module-docstring
import os

__version__ = "0.6.19"

os.environ["RAY_DEDUP_LOGS"] = "0"
os.environ["RAY_COLOR_PREFIX"] = "1"
