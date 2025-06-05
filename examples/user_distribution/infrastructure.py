import networkx as nx
from metric import user_count_asset
from update_policy import (
    EdgeUpdatePolicy,
    UserDistributionPolicy,
    kill_policy,
)

from eclypse.builders.infrastructure import hierarchical


def get_infrastructure(seed: int):
    kill_probability = 0.1
    node_policy = kill_policy(kill_probability=kill_probability)
    edge_policy = EdgeUpdatePolicy(kill_probability=kill_probability)

    i = hierarchical(
        node_assets={"user_count": user_count_asset()},
        infrastructure_id="hierarchical",
        n=187,
        node_update_policy=[node_policy, UserDistributionPolicy()],
        include_default_assets=True,
        link_update_policy=edge_policy,
        symmetric=True,
        seed=seed,
    )

    mapping = {old_name: new_name for new_name, old_name in enumerate(i.nodes())}
    i = nx.relabel_nodes(i, mapping, copy=False)
    return i
