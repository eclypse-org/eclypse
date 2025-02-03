from typing import (
    Any,
    Dict,
    Optional,
)

from swiplserver import (
    PrologResultNotAvailableError,
    PrologThread,
)

from examples.edgewise.utils import (
    DEPLOYED_QUERY,
    PL_QUERY,
    PL_STRATEGY_DIR,
    prolog_to_dict,
    timed_query,
)


def pl_process(
    prolog: PrologThread,
    app_name: str,
    preprocess: bool = False,
    cr: bool = False,
    timeout: Optional[int] = None,
) -> Optional[Dict[str, Any]]:

    if preprocess:
        timed_query(prolog, f"consult('{PL_STRATEGY_DIR / 'binpack.pl'}')")
        if not cr:
            timed_query(prolog, query="retract(deployed(_,_))")
    else:
        timed_query(prolog, f"consult('{PL_STRATEGY_DIR / 'binpack_num.pl'}')")

    r = timed_query(prolog, query=PL_QUERY.format(app=app_name), timeout=timeout)
    mapping = prolog_to_dict(r["Placement"]) if r else {}
    cost = r["Cost"] if r else float("inf")
    exec_time = r["Time"] if r else float("inf")

    if mapping:
        str_pl = r["Placement"]
        timed_query(
            prolog,
            queryy=f"assert({DEPLOYED_QUERY.format(app=app_name, placement=str_pl)})",
        )

    return mapping, cost, exec_time
