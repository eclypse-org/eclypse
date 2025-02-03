from __future__ import annotations

import signal
from pathlib import Path
from typing import Optional

from swiplserver import (
    PrologResultNotAvailableError,
    PrologThread,
    prolog_args,
)

PL_UTILS_DIR = Path(__file__).parent / "pl-utils"
PL_STRATEGY_DIR = Path(__file__).parent / "strategy" / "prolog"
PREPROCESS_FILE = PL_UTILS_DIR / "preprocessing.pl"
REQUIREMENTS_FILE = PL_UTILS_DIR / "requirements.pl"
COSTS_FILE = PL_UTILS_DIR / "costs.pl"

PREPROCESS_QUERY = "preprocess({app_name}, Compatibles)"
PL_QUERY = "stats({app}, Placement, Cost, Bins, Infs, Time)"
COST_QUERY = "cost({ntype}, {compid}, Cost)"
DEPLOYED_QUERY = "deployed({app}, {placement})"


def prolog_to_dict(p):
    return dict(list(map((lambda x: prolog_args(x)), p)))


def parse_compatibles(r):
    compatibles = {}
    for t in r:
        name, comps = prolog_args(t)
        compatibles[name] = {}
        for c in comps:
            n, cost = prolog_args(c)
            compatibles[name][n] = round(float(cost), 4)
    return compatibles


class TimeoutException(Exception):
    """Custom exception for handling timeouts."""

    pass


def timeout(func):
    """Decorator that applies a timeout based on the instance's `timeout` attribute."""

    def wrapper(self, *args, **kwargs):
        timeout_value = getattr(self, "timeout", None)
        if not isinstance(timeout_value, (int, float)) or timeout_value <= 0:
            raise ValueError(f"Invalid timeout value: {timeout_value}")

        def handler(signum, frame):
            raise TimeoutException()

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(int(timeout_value))

        try:
            result = func(self, *args, **kwargs)
        except TimeoutException:
            print(f"Timeout: {func.__name__} took longer than {timeout_value} seconds.")
            result = None
        finally:
            signal.alarm(0)

        return result

    return wrapper


def timed_query(
    prolog: PrologThread,
    query: str,
    timeout: Optional[int] = None,
    find_all: Optional[bool] = True,
):
    try:
        prolog.query_async(query, find_all=find_all)
        r = prolog.query_async_result(wait_timeout_seconds=timeout)
        r = r[0] if isinstance(r, list) else r
    except PrologResultNotAvailableError:
        print(f"Timeout: {query} took longer than {timeout} seconds.")
        prolog.cancel_query_async()
        r = None

    return r
