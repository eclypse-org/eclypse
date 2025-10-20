from __future__ import annotations

import random as rnd
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
)

from eclypse.placement.strategies import PlacementStrategy
from eclypse.utils.constants import MAX_FLOAT

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import (
        Placement,
        PlacementView,
    )


class EnergyMinimizationStrategy(PlacementStrategy):
    """A placement strategy that minimizes energy consumption based on the allocated
    CPU, GPU, RAM, and storage."""

    def __init__(
        self,
        cpu_weight: float = 0.25,
        gpu_weight: float = 0.25,
        ram_weight: float = 0.25,
        storage_weight: float = 0.25,
    ):
        """Initializes the strategy with specific weights for the energy function.

        Args:
            cpu_weight (float): Weight of the CPU energy consumption.
            gpu_weight (float): Weight of the GPU energy consumption.
            ram_weight (float): Weight of the RAM energy consumption.
            storage_weight (float): Weight of the storage energy consumption.
        """
        self.cpu_weight = cpu_weight
        self.gpu_weight = gpu_weight
        self.ram_weight = ram_weight
        self.storage_weight = storage_weight

        self.initial_resources = None

    def _energy_consumption(
        self,
        idle: float,
        cpu: float,
        gpu: float,
        ram: float,
        storage: float,
    ) -> float:
        """Calculates the energy based on the allocated resources.

        Args:
            cpu (float): Allocated CPU.
            gpu (float): Allocated GPU.
            ram (float): Allocated RAM.
            storage (float): Allocated storage.

        Returns:
            float: The calculated energy.
        """
        return (
            idle
            + self.cpu_weight * cpu
            + self.gpu_weight * gpu
            + self.ram_weight * ram
            + self.storage_weight * storage
        )

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[Any, Any]:
        """Places the services of an application on the infrastructure nodes to minimize
        energy consumption.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the application on.
            application (Application): The application to place on the infrastructure.

        Returns:
            Dict[str, str]: A mapping of services to infrastructure nodes.
        """
        if self.initial_resources is None:
            self.initial_resources = infrastructure.nodes(data=True)
        if not self.is_feasible(infrastructure, application):
            return {}

        mapping = {}
        infrastructure_nodes = list(infrastructure.available.nodes(data=True))
        rnd.shuffle(infrastructure_nodes)

        for service, sattr in application.nodes(data=True):
            min_energy: Optional[float] = MAX_FLOAT
            best_fit: Optional[str] = None
            best_nattr: Optional[Dict[str, Any]] = None

            for node, nattr in infrastructure_nodes:
                if infrastructure.node_assets.satisfies(nattr, sattr):
                    allocated_nattr = infrastructure.node_assets.consume(
                        self.initial_resources[node], nattr
                    )
                    energy = self._energy_consumption(
                        allocated_nattr.get("energy", 0),
                        allocated_nattr.get("cpu", 0),
                        allocated_nattr.get("gpu", 0),
                        allocated_nattr.get("ram", 0),
                        allocated_nattr.get("storage", 0),
                    )

                    if energy < min_energy and energy > 0:
                        min_energy = energy
                        best_fit = node
                        best_nattr = nattr

            mapping[service] = best_fit
            if best_fit is None or best_nattr is None:
                continue

            new_res = infrastructure.node_assets.consume(best_nattr, sattr)
            infrastructure_nodes.remove((best_fit, best_nattr))
            infrastructure_nodes.append((best_fit, new_res))
        return mapping
