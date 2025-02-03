from collections import defaultdict
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
    Tuple,
)

import numpy as np
from ortools.linear_solver import pywraplp
from swiplserver import PrologThread

from eclypse.graph import (
    Application,
    Infrastructure,
)
from examples.edgewise.utils import (
    COST_QUERY,
    DEPLOYED_QUERY,
    PREPROCESS_FILE,
    PREPROCESS_QUERY,
    parse_compatibles,
    timed_query,
)

if TYPE_CHECKING:
    from swiplserver import PrologThread


def get_compatibles(
    prolog: PrologThread,
    app: Application,
    infr: Infrastructure,
    preprocess: bool = False,
    cr: bool = False,
):
    timed_query(prolog, f"consult('{PREPROCESS_FILE}')")

    compatibles = defaultdict(dict)
    if preprocess:
        if not cr:
            timed_query(prolog, query="retract(deployed(_,_))")
        r = timed_query(
            prolog,
            PREPROCESS_QUERY.format(app_name=app.name),
        )
        compatibles = parse_compatibles(r["Compatibles"]) if r else None
    else:
        instances = [
            (i, attr)
            for i, attr in app.nodes(data=True)
            if i not in app.graph["things"]
        ]

        for s, _ in instances:
            for n, nattr in infr.nodes(data=True):
                r = timed_query(
                    prolog,
                    COST_QUERY.format(ntype=nattr["Type"], compid=s),
                    find_all=False,
                )
                if r:
                    compatibles[s][n] = r["Cost"]
                else:
                    print(ValueError("No cost for {} in {}".format(nattr["Type"], s)))
                    return None
    return compatibles


def edgewise(
    prolog: PrologThread,
    app: Application,
    infr: Infrastructure,
    preprocess: bool = False,
    cr: bool = False,
    timeout: Optional[int] = None,
) -> Tuple[Dict[str, str], float, float]:
    """Uses EdgeWise methodology to compute a placement, then retrieves it
    together with the cost and execution time."""

    compatibles = get_compatibles(prolog, app, infr, preprocess, cr)

    if compatibles is None:
        print("No compatibles found.")
        return None, float("inf"), float("inf")

    timed_query(prolog, query="retractall(deployed(_,_))", find_all=False)

    instances = [
        (i, attr) for i, attr in app.nodes(data=True) if i not in app.graph["things"]
    ]

    nodes = list(infr.nodes(data=True))
    links = list(infr.edges(data=True))

    nids = list(infr.nodes())  # list of node ids

    S = len(instances)
    N = len(nodes)

    # Create the solver.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if timeout:
        solver.SetTimeLimit(timeout * 1000)  # in milliseconds

    # Create the variables for binpack B.
    b = {j: solver.BoolVar(f"b_{nids[j]}") for j in range(N)}

    # Create bool vars matrix X.
    # at the same time, create costs matrix C
    costs = np.zeros((S, N))
    x = {(i, j): 0 for i in range(S) for j in range(N)}
    for i, (s, _) in enumerate(instances):
        for j, n in enumerate(nids):
            if n in compatibles[s]:
                x[i, j] = solver.BoolVar(f"{s}_{n}")
                costs[i, j] = compatibles[s][n]

    # Constraint: one instance at most in one node.
    [
        solver.Add(
            solver.Sum([x[i, j] for j in range(N)]) == 1,
            name=f"one_node_{instances[i][0]}",
        )
        for i in range(S)
    ]

    # Constraint: cannot exceed the hw capacity of a node.
    coeffs = [sattr["HW"] for _, sattr in instances]
    bounds = [nattr["HW"] for _, nattr in nodes]

    [
        solver.Add(
            solver.Sum([coeffs[i] * x[i, j] for i in range(S)])
            <= (bounds[j] - infr.graph["hwTh"]),
            name=f"hw_{nids[j]}",
        )
        for j in range(N)
    ]

    # Budgeting: no more than MAX_BIN nodes are used.
    [
        solver.Add(x[i, j] <= b[j], name=f"bin_{instances[i][0]}_{nids[j]}")
        for j in range(N)
        for i in range(S)
    ]

    solver.Add(solver.Sum([b[j] for j in range(N)]) <= S, name="budget")

    # Constraints:
    # - cannot exceed the bandwidth of a link. (FeatBW >= sum(ReqBW))
    # - satisfy latency requirements of data flows. (FeatLat <= ReqLat)
    for n, n1, a in links:  # foreach link
        coeffs = {}
        j = nids.index(n)
        j1 = nids.index(n1)
        for source, dest, attr in app.edges(data=True):  # foreach data flow

            name = f"{source}_{dest}_{n}_{n1}"
            if source in app.graph["things"]:
                if app.graph["things"][source]["node"] == n:
                    i = -1
                else:
                    continue
            else:
                if n in compatibles[source]:
                    # i = instances.index(source)
                    i = next(i for i, (x, _) in enumerate(instances) if x == source)
                else:
                    continue

            if dest in app.graph["things"]:
                if app.graph["things"][dest]["node"] == n1:
                    i1 = -1
                else:
                    continue
            else:
                if n1 in compatibles[dest]:
                    # i1 = instances.index(dest)
                    i1 = next(i for i, (x, _) in enumerate(instances) if x == dest)
                else:
                    continue

            xij = x[i, j] if i != -1 else 1
            xi1j1 = x[i1, j1] if i1 != -1 else 1

            sec_reqs = set(attr["Sec"])
            if (a["latency"] > attr["latency"]) or (
                preprocess
                and not (
                    sec_reqs.issubset(set(infr.nodes[n]["Sec"]))
                    and sec_reqs.issubset(set(infr.nodes[n1]["Sec"]))
                )
            ):
                solver.Add(xij + xi1j1 <= 1, name=f"{name}_no_reqs")
            else:
                # linearize the constraint
                c = solver.BoolVar(name)
                solver.Add(c >= xij + xi1j1 - 1, name=f"lin_3_{c.name()}")

                coeffs[c] = attr["bandwidth"]

        if len(coeffs):
            upper_bound = max(a["bandwidth"] - infr.graph["bwTh"], 0)
            bw_constraint = solver.RowConstraint(0, upper_bound, f"{n}_{n1}_bw")
            for c, b in coeffs.items():
                bw_constraint.SetCoefficient(c, b)

    # OBJECTIVE FUNCTION
    obj_expr = [costs[i, j] * x[i, j] for i in range(S) for j in range(N)]
    solver.Minimize(solver.Sum(obj_expr))

    status = solver.Solve()
    placement = {}
    tot_time = float("inf")
    tot_cost = float("inf")
    if status == pywraplp.Solver.OPTIMAL:
        for i in range(S):
            row = [
                x[i, j].solution_value() if not isinstance(x[i, j], int) else 0
                for j in range(N)
            ]
            j = row.index(max(row))
            s = instances[i][0]
            n = nodes[j][0]
            placement[s] = n

        tot_cost = solver.Objective().Value()
        tot_time = solver.WallTime() / 1000

        str_pl = (
            "["
            + ", ".join(["({}, {})".format(s, n) for s, n in placement.items()])
            + "]"
        )
        timed_query(
            prolog,
            query=f"assert({DEPLOYED_QUERY.format(app=app.name, placement=str_pl)})",
        )
        print(f"\nAssert placement for {app.name}: {str_pl}\n")
    elif status == pywraplp.Solver.INFEASIBLE:
        print("Problem is infeasible")
    elif status == pywraplp.Solver.ABNORMAL or status == pywraplp.Solver.NOT_SOLVED:
        print(f"Time limit reached")

    return placement, tot_cost, tot_time
