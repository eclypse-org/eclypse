# Builders

Builders create ready-to-use infrastructures, applications, and workflow graphs
without hiding the underlying model. They return regular
[Infrastructure][eclypse.graph.infrastructure.Infrastructure] and
[Application][eclypse.graph.application.Application] objects, so you can still add
nodes, edges, assets, update policies, and flows afterwards.

## Infrastructure builders

Infrastructure builders live in [eclypse.builders.infrastructure][eclypse.builders.infrastructure]. They
cover generic graph generators, cloud-edge architecture patterns, and reference
topologies.

| Category | Builders |
| --- | --- |
| Generic generators | [get_star][eclypse.builders.infrastructure.get_star], [get_random][eclypse.builders.infrastructure.get_random], [get_hierarchical][eclypse.builders.infrastructure.get_hierarchical], [get_fat_tree][eclypse.builders.infrastructure.get_fat_tree], [get_b_cube][eclypse.builders.infrastructure.get_b_cube], [get_small_world][eclypse.builders.infrastructure.get_small_world], [get_scale_free][eclypse.builders.infrastructure.get_scale_free] |
| Architecture patterns | [get_continuum_tiered][eclypse.builders.infrastructure.get_continuum_tiered], [get_mec_5g][eclypse.builders.infrastructure.get_mec_5g], [get_multi_region_wan][eclypse.builders.infrastructure.get_multi_region_wan], [get_industrial_tsn][eclypse.builders.infrastructure.get_industrial_tsn], [get_factory_cells][eclypse.builders.infrastructure.get_factory_cells], [get_vehicular_edge][eclypse.builders.infrastructure.get_vehicular_edge] |
| References | [get_orion_cev][eclypse.builders.infrastructure.get_orion_cev], [get_topohub][eclypse.builders.infrastructure.get_topohub], [get_topology_zoo][eclypse.builders.infrastructure.get_topology_zoo], [get_sndlib][eclypse.builders.infrastructure.get_sndlib], [get_backbone][eclypse.builders.infrastructure.get_backbone], [get_caida][eclypse.builders.infrastructure.get_caida], [get_gabriel][eclypse.builders.infrastructure.get_gabriel] |

Example:

```python
from eclypse.builders.infrastructure import get_hierarchical

infrastructure = get_hierarchical(
    n=30,
    include_default_assets=True,
    seed=42,
)
```

## Application builders

Application builders live in [eclypse.builders.application][eclypse.builders.application]. They provide
reference microservice applications and domain-specific pipelines.

Sock Shop is the main reference application used in examples:

```python
from eclypse.builders.application import get_sock_shop

application = get_sock_shop(
    include_default_assets=True,
    seed=42,
)
```

For emulation, choose the communication interface when the builder supports
runtime services:

```python
application = get_sock_shop(
    communication_interface="mpi",
    include_default_assets=True,
)
```

## Workflow builders

For simulation-only task DAGs, ECLYPSE also provides
[get_workflow][eclypse.builders.workflow.get_workflow] in
[eclypse.builders.workflow][eclypse.builders.workflow]. These builders use WfCommons to generate
workflow-shaped applications and normalise file-size-derived `storage` and
dependency `bandwidth` values from bytes to MiB before assigning them to the
default ECLYPSE assets.

## When to use builders

Use builders when you need a stable scenario quickly: a benchmark, a smoke
test, or a baseline for policy and placement experiments.

Use manual graph construction when the topology itself is the object of study,
or when you need exact control over node identities, edge attributes, and asset
definitions.
