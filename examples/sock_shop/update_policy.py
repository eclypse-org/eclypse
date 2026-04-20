from __future__ import annotations

from eclypse import policies


def get_update_policies():
    """Build the shared Sock Shop infrastructure update policies.

    Returns:
        list[callable]: Built-in update policies for availability flapping and
            multiplicative node and edge drift.
    """
    return [
        policies.failure.availability_flap(
            down_probability=0.02,
            up_probability=0.5,
        ),
        policies.distribution.uniform(
            node_asset_distributions={
                "cpu": (0.95, 1.05),
                "gpu": (0.9, 1.1),
                "ram": (0.8, 1.2),
                "storage": (0.9, 1.1),
            },
            edge_asset_distributions={
                "latency": (0.9, 1.1),
                "bandwidth": (0.95, 1.05),
            },
        ),
    ]
