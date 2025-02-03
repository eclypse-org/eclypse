from typing import Any, Dict
from .edgewise_strategy import EdgeWiseStrategy


def get_strategy(prolog, **config):
    return EdgeWiseStrategy(
        prolog=prolog,
        declarative=config["declarative"],
        preprocess=config["preprocess"],
        cr=config["cr"],
        timeout=config["timeout"],
    )


__all__ = [
    "get_strategy",
]
