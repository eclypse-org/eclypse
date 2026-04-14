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
                policies.degradation.degrade(
                    target_degradation=0.8,
                    epochs=14,
                    node_assets=["cpu", "ram"],
                    edge_assets=["latency", "bandwidth"],
                ),
            )
        ],
    )
