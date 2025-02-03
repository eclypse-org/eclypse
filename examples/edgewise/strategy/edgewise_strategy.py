from __future__ import annotations

import multiprocessing
import random
import threading
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
)

from eclypse.placement.strategies import PlacementStrategy

from .milp_engine import edgewise
from .pl_engine import pl_process

from examples.edgewise.utils import timed_query

if TYPE_CHECKING:
    from swiplserver import PrologThread

    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import (
        Placement,
        PlacementView,
    )


def place_thing_instances(
    prolog: PrologThread, things: Dict[str, Any], infrastructure: Infrastructure
) -> Dict[str, Any]:

    all_nodes = list(infrastructure.nodes)
    partial_placement = {}

    for n, nthings in infrastructure.nodes(data="IoT"):
        for t in nthings:
            if t in things:
                things[t].update({"node": n})
                partial_placement[t] = n

    unplaced_things = set(things) - set(partial_placement)
    for t in unplaced_things:
        random_node = random.choice(all_nodes)
        things[t]["node"] = random_node
        partial_placement[t] = random_node

    for n, nattr in infrastructure.nodes(data=True):
        timed_query(prolog, f"retractall(node({n}, _, (_,_) , _, _))")
        timed_query(
            prolog,
            f"assert(node({n}, {nattr['SW']}, ({nattr['Arch']}, {nattr['HW']}), {nattr['Sec']}, {nattr['IoT']}))".replace(
                "'", ""
            ),
        )

    return partial_placement


class EdgeWiseStrategy(PlacementStrategy):

    def __init__(
        self,
        prolog: PrologThread,
        declarative: bool = False,
        preprocess: bool = False,
        cr: bool = False,
        timeout: Optional[int] = None,
    ):
        self.prolog = prolog
        self.cost = float("inf")
        self.exec_time = float("inf")

        self.declarative = declarative
        self.preprocess = preprocess
        self.cr = cr
        self.timeout = timeout

        self.moved_services = 0
        self.init_nodes = []

        self.first_iteration = True

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        placements: Dict[str, Placement],
        _: PlacementView,
    ) -> Dict[Any, Any]:

        if self.first_iteration:
            timed_query(self.prolog, "dynamic node/5.")
            timed_query(self.prolog, f"consult('{application.graph['file']}')")
            timed_query(self.prolog, f"consult('{infrastructure.graph['file']}')")
            self.init_nodes = list(infrastructure.nodes())
            self.first_iteration = False

        mapping = place_thing_instances(
            self.prolog, application.graph["things"], infrastructure=infrastructure
        )
        if len(mapping) != len(application.graph["things"]):
            infrastructure.logger.error("Not all things have been placed.")
            return None

        self.sync_available_nodes(infr=infrastructure)

        if self.declarative:
            result = pl_process(
                self.prolog,
                application.name,
                preprocess=self.preprocess,
                cr=self.cr,
                timeout=self.timeout,
            )
        else:
            result = edgewise(
                self.prolog,
                application,
                infrastructure,
                preprocess=self.preprocess,
                cr=self.cr,
                timeout=self.timeout,
            )

        components_mapping, self.cost, self.exec_time = result

        if components_mapping:
            mapping.update(components_mapping)
            self.moved_services = len(
                [
                    s
                    for s, n in mapping.items()
                    if placements[application.name].mapping.get(s, "") not in ["", n]
                    and s not in application.graph["things"]
                ]
            )

        return mapping

    def sync_available_nodes(self, infr: Infrastructure):
        timed_query(self.prolog, "retractall(node(_, _, _, _, _))")
        for n, nattr in infr.nodes(data=True):
            pl_str = f"assert(node({n}, {nattr['SW']}, ({nattr['Arch']}, {nattr['HW']}), {nattr['Sec']}, {nattr['IoT']}))".replace(
                "'", ""
            )
            timed_query(self.prolog, pl_str)
