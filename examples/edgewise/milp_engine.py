from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from ortools.linear_solver import pywraplp
from swiplserver import PrologThread

from eclypse.graph import (
    Application,
    Infrastructure,
)
from examples.edgewise.utils import (
    DEPLOYED_QUERY,
    PL_UTILS_DIR,
    PREPROCESS_QUERY,
    parse_compatibles,
)

if TYPE_CHECKING:
    from swiplserver import PrologThread


def get_compatibles(
    prolog: PrologThread, app_path: Path, infr_path: Path, app_name: str
):
    prolog.query(f"consult('{app_path}')")
    prolog.query(f"consult('{infr_path}')")
    prolog.query(f"consult('{PL_UTILS_DIR / 'preprocess.pl'}')")
    prolog.query_async(PREPROCESS_QUERY.format(app_name=app_name), find_all=False)
    r = prolog.query_async_result()
    compatibles = parse_compatibles(r[0]["Compatibles"]) if r else None
    return compatibles


def edgewise(prolog: PrologThread, app: Application, infr: Infrastructure):

    compatibles = get_compatibles(
        prolog,
        app.graph["file"],
        infr.graph["file"],
        app.name,
    )
    if not compatibles:
        print("No compatibles found.")
        return None

    prolog.query("retract(deployed(_,_))")
    app.set_things_from_infr(infr)  # TODO

    instances = [i for i in app.nodes() if i not in app.graph["things"]]
    nodes = list(infr.nodes(data=True))
    links = list(infr.edges(data=True))

    nids = list(infr.nodes())  # list of node ids

    S = len(instances)
    N = len(nodes)

    # Create the solver.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # Create the variables for binpack B.
    b = {j: solver.BoolVar(f"b_{nids[j]}") for j in range(N)}

    # Create bool vars matrix X.
    # at the same time, create costs matrix C
    costs = np.zeros((S, N))
    x = {(i, j): 0 for i in range(S) for j in range(N)}
    for i, s in enumerate(instances):
        for j, n in enumerate(nids):
            if n in compatibles[s.id]:
                x[i, j] = solver.BoolVar(f"{s.id}_{n}")
                costs[i, j] = compatibles[s.id][n]

    # Constraint: one instance at most in one node.
    [
        solver.Add(
            solver.Sum([x[i, j] for j in range(N)]) == 1,
            name=f"one_node_{instances[i].id}",
        )
        for i in range(S)
    ]

    # Constraint: cannot exceed the hw capacity of a node.
    coeffs = [s.comp.hwreqs for s in instances]
    bounds = [a["hwcaps"] for _, a in nodes]

    [
        solver.Add(
            solver.Sum([coeffs[i] * x[i, j] for i in range(S)])
            <= (bounds[j] - infr.hwTh),
            name=f"hw_{nids[j]}",
        )
        for j in range(N)
    ]

    # Budgeting: no more than MAX_BIN nodes are used.
    [
        solver.Add(x[i, j] <= b[j], name=f"bin_{instances[i].id}_{nids[j]}")
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
                    i = instances.index(source)
                else:
                    continue

            if dest in app.graph["things"]:
                if app.graph["things"][dest]["node"] == n1:
                    i1 = -1
                else:
                    continue
            else:
                if n1 in compatibles[dest]:
                    i1 = instances.index(dest)
                else:
                    continue

            xij = x[i, j] if i != -1 else 1
            xi1j1 = x[i1, j1] if i1 != -1 else 1

            sec_reqs = set(attr["Sec"])
            if (a["lat"] > attr["latency"]) or (
                not (
                    sec_reqs.issubset(set(infr.nodes[n]["seccaps"]))
                    and sec_reqs.issubset(set(infr.nodes[n1]["seccaps"]))
                )
            ):
                solver.Add(xij + xi1j1 <= 1, name=f"{name}_no_reqs")
            else:
                # linearize the constraint
                c = solver.BoolVar(name)
                solver.Add(c >= xij + xi1j1 - 1, name=f"lin_3_{c.name()}")

                coeffs[c] = attr["bandwidth"]

        if len(coeffs):
            upper_bound = max(a["bw"] - infr.bwTh, 0)
            bw_constraint = solver.RowConstraint(0, upper_bound, f"{n}_{n1}_bw")
            for c, b in coeffs.items():
                bw_constraint.SetCoefficient(c, b)

    # OBJECTIVE FUNCTION
    obj_expr = [costs[i, j] * x[i, j] for i in range(S) for j in range(N)]
    solver.Minimize(solver.Sum(obj_expr))

    status = solver.Solve()
    n_distinct = set()
    placement = {}
    res = {}
    if status == pywraplp.Solver.OPTIMAL:
        for i in range(S):
            row = [
                x[i, j].solution_value() if not isinstance(x[i, j], int) else 0
                for j in range(N)
            ]
            j = row.index(max(row))
            s = instances[i].id
            n = nodes[j][0]
            placement[s] = n

        tot_cost = solver.Objective().Value()  # if only cost in Objective function
        tot_time = solver.WallTime() / 1000  # in seconds
        res = {
            "Time": tot_time,
            "Cost": round(tot_cost, 4),
            "Infs": solver.NumConstraints(),
        }

        str_pl = (
            "["
            + ", ".join(["({}, {})".format(s, n) for s, n in placement.items()])
            + "]"
        )
        prolog.query(f"assert({DEPLOYED_QUERY.format(app=app.name, placement=str_pl)})")
        print(f"Assert placement for {app.name}: {str_pl}\n")
    else:
        print("The problem does not have a solution.")
