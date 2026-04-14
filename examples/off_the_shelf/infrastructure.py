"""Infrastructure built entirely from off-the-shelf ECLYPSE components."""

from __future__ import annotations

from eclypse import policies
from eclypse.builders.infrastructure import hierarchical


def get_infrastructure(seed: int = 7):
    """Create a generated infrastructure with built-in update policies."""
    return hierarchical(
        n=64,
        infrastructure_id="BuiltinsInfrastructure",
        symmetric=True,
        update_policies=[
            policies.availability_flap(
                down_probability=0.04,
                up_probability=0.15,
            ),
            policies.uniform(
                node_assets=["cpu", "ram", "storage"],
                edge_assets=["latency", "bandwidth"],
                node_asset_distributions={
                    "cpu": (0.85, 1.12),
                    "ram": (0.8, 1.15),
                    "storage": (0.92, 1.08),
                },
                edge_asset_distributions={
                    "latency": (0.95, 1.2),
                    "bandwidth": (0.82, 1.08),
                },
            ),
            policies.every(
                2,
                policies.latency_spike(
                    probability=0.35,
                    min_increase=2.0,
                    max_increase=6.0,
                ),
                start=2,
            ),
            policies.after(
                5,
                policies.degrade(
                    target_degradation=0.82,
                    epochs=12,
                    node_assets=["cpu", "ram", "storage"],
                    edge_assets=["latency", "bandwidth"],
                ),
            ),
        ],
        include_default_assets=True,
        resource_init="max",
        seed=seed,
    )
