import os

__version__ = "0.8.2"

os.environ["RAY_DEDUP_LOGS"] = "0"
os.environ["RAY_COLOR_PREFIX"] = "1"
