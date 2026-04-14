"""Application built entirely from off-the-shelf ECLYPSE components."""

from __future__ import annotations

from eclypse import policies
from eclypse.builders.application import get_sock_shop


def get_application(seed: int = 7):
    """Create a Sock Shop application using built-in policies only."""
    return get_sock_shop(
        application_id="SockShopBuiltins",
        include_default_assets=True,
        seed=seed,
        update_policies=[
            policies.every(
                2,
                policies.distribution.uniform(
                    node_assets=["cpu", "ram"],
                    edge_assets=["latency", "bandwidth"],
                    node_distribution=(1.02, 1.18),
                    edge_distribution=(0.98, 1.08),
                ),
                start=2,
            ),
            policies.after(
                6,
                policies.degrade.degrade(
                    reduce_factor=0.8,
                    reduce_epochs=14,
                    increase_factor=1.25,
                    increase_epochs=14,
                    reduce_node_assets=["cpu", "ram"],
                    reduce_edge_assets=["bandwidth"],
                    increase_edge_assets=["latency"],
                ),
            )
        ],
    )
