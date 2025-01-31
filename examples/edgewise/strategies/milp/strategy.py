from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

from eclypse.placement.strategies import PlacementStrategy
from .engine import edgewise

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
    things: Dict[str, Any], infrastructure: Infrastructure
) -> Dict[str, Any]:
    partial_placement = {}
    for n, nthings in infrastructure.nodes(data="IoT"):
        for t in nthings:
            if t in things:
                things[t].update({"node": n})
                partial_placement[t] = n
    return partial_placement


class EdgeWiseStrategy(PlacementStrategy):

    def __init__(
        self,
        prolog: PrologThread,
        preprocess: bool = False,
        cr: bool = False,
    ):
        self.prolog = prolog
        self.cost = float("inf")
        self.exec_time = float("inf")
        self.moved_services = 0
        self.preprocess = preprocess
        self.cr = cr
        self.timeout = 60

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        placements: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[Any, Any]:

        things_mapping = place_thing_instances(
            application.graph["things"], infrastructure=infrastructure
        )
        if len(things_mapping) != len(application.graph["things"]):
            infrastructure.logger.error("Not all things have been placed.")
            return None

        components_mapping, self.cost, self.exec_time = edgewise(
            self.prolog,
            application,
            infrastructure,
            preprocess=self.preprocess,
            cr=self.cr,
        )

        # Compute difference between last placement and current placement
        mapping = {**things_mapping, **components_mapping}

        self.moved_services = len(
            [
                s
                for s, n in mapping.items()
                if placements[application.name].mapping.get(s, "") not in ["", n]
            ]
        )

        return {**things_mapping, **components_mapping}
