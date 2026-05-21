Builders
========

Builders create ready-to-use infrastructures, applications, and workflow graphs
without hiding the underlying model. They return regular
:class:`~eclypse.graph.infrastructure.Infrastructure` and
:class:`~eclypse.graph.application.Application` objects, so you can still add
nodes, edges, assets, update policies, and flows afterwards.

Infrastructure builders
-----------------------

Infrastructure builders live in :mod:`eclypse.builders.infrastructure`. They
cover generic graph generators, cloud-edge architecture patterns, and reference
topologies.

.. list-table::
   :header-rows: 1

   * - Category
     - Builders
   * - Generic generators
     - :func:`~eclypse.builders.infrastructure.get_star`,
       :func:`~eclypse.builders.infrastructure.get_random`,
       :func:`~eclypse.builders.infrastructure.get_hierarchical`,
       :func:`~eclypse.builders.infrastructure.get_fat_tree`,
       :func:`~eclypse.builders.infrastructure.get_b_cube`,
       :func:`~eclypse.builders.infrastructure.get_small_world`,
       :func:`~eclypse.builders.infrastructure.get_scale_free`
   * - Architecture patterns
     - :func:`~eclypse.builders.infrastructure.get_continuum_tiered`,
       :func:`~eclypse.builders.infrastructure.get_mec_5g`,
       :func:`~eclypse.builders.infrastructure.get_multi_region_wan`,
       :func:`~eclypse.builders.infrastructure.get_industrial_tsn`,
       :func:`~eclypse.builders.infrastructure.get_factory_cells`,
       :func:`~eclypse.builders.infrastructure.get_vehicular_edge`
   * - References
     - :func:`~eclypse.builders.infrastructure.get_orion_cev`,
       :func:`~eclypse.builders.infrastructure.get_topohub`,
       :func:`~eclypse.builders.infrastructure.get_topology_zoo`,
       :func:`~eclypse.builders.infrastructure.get_sndlib`,
       :func:`~eclypse.builders.infrastructure.get_backbone`,
       :func:`~eclypse.builders.infrastructure.get_caida`,
       :func:`~eclypse.builders.infrastructure.get_gabriel`

Example:

.. code-block:: python

   from eclypse.builders.infrastructure import get_hierarchical

   infrastructure = get_hierarchical(
       n=30,
       include_default_assets=True,
       seed=42,
   )

Application builders
--------------------

Application builders live in :mod:`eclypse.builders.application`. They provide
reference microservice applications and domain-specific pipelines.

Sock Shop is the main reference application used in examples:

.. code-block:: python

   from eclypse.builders.application import get_sock_shop

   application = get_sock_shop(
       include_default_assets=True,
       seed=42,
   )

For emulation, choose the communication interface when the builder supports
runtime services:

.. code-block:: python

   application = get_sock_shop(
       communication_interface="mpi",
       include_default_assets=True,
   )

Workflow builders
-----------------

For simulation-only task DAGs, ECLYPSE also provides
:func:`~eclypse.builders.workflow.get_workflow` in
:mod:`eclypse.builders.workflow`. These builders use WfCommons to generate
workflow-shaped applications and normalise file-size-derived ``storage`` and
dependency ``bandwidth`` values from bytes to MiB before assigning them to the
default ECLYPSE assets.

When to use builders
--------------------

Use builders when you need a stable scenario quickly: a benchmark, a smoke
test, or a baseline for policy and placement experiments.

Use manual graph construction when the topology itself is the object of study,
or when you need exact control over node identities, edge attributes, and asset
definitions.
