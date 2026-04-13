import networkx as nx
from metric import user_count_asset
from update_policy import (
    LatencyUpdatePolicy,
    UserDistributionPolicy,
    kill_policy,
)

from eclypse.builders.infrastructure import hierarchical


def get_infrastructure(seed: int):
    kill_probability = 0.1
    i = hierarchical(
        node_assets={"user_count": user_count_asset()},
        infrastructure_id="hierarchical",
        n=187,
        update_policies=[
            kill_policy(kill_probability=kill_probability),
            LatencyUpdatePolicy(kill_probability=kill_probability),
            UserDistributionPolicy(),
        ],
        include_default_assets=True,
        symmetric=True,
        seed=seed,
    )

    mapping = {old_name: new_name for new_name, old_name in enumerate(i.nodes())}
    i = nx.relabel_nodes(i, mapping, copy=False)
    return i
