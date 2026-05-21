Grid analysis
=============

The grid analysis example runs a Ray Tune sweep over infrastructure topology,
load, failure policy, random seed, and placement strategy choices.

Use it when you want to understand:

- how to wrap an ECLYPSE simulation in a parameter-search function,
- how to compare placement strategies across many generated infrastructures,
- how to write custom infrastructure assets and policies for experiments.

The full code lives in the
`examples/grid_analysis <https://github.com/eclypse-org/eclypse/tree/main/examples/grid_analysis>`_
directory.

Run it from the repository root with:

.. code-block:: bash

   uv run grid-analysis

Simulation sweep
----------------

.. dropdown:: Main sweep code

    .. literalinclude:: ../../../../examples/grid_analysis/main.py
        :language: python

Infrastructure
--------------

.. dropdown:: Infrastructure code

    .. literalinclude:: ../../../../examples/grid_analysis/infrastructure.py
        :language: python

Placement strategy
------------------

.. dropdown:: Strategy code

    .. literalinclude:: ../../../../examples/grid_analysis/strategy.py
        :language: python

What to inspect
---------------

Use this example as a template for repeated experiments. The main result is not
a single simulation trace, but a grid of runs that lets you compare placement
strategies and infrastructure choices under the same sweep logic.

Related concepts:

- :doc:`../concepts/placement-strategy`
- :doc:`../concepts/update-policy`
