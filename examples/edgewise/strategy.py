from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

from eclypse.placement.strategies import PlacementStrategy

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import (
        Placement,
        PlacementView,
    )


class EdgeWiseStrategy(PlacementStrategy):

    def __init__(self):
        pass

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[Any, Any]:
        pass
