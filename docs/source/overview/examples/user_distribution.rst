User distribution
=================

The user distribution example customises a generated infrastructure with a
``user_count`` asset and updates latency and placement conditions as the user
distribution evolves.

Use it when you want to understand:

- how to add a custom infrastructure asset,
- how to write metrics around domain-specific infrastructure state,
- how update policies can drive a longer-running simulation.

The full code lives in the
`examples/user_distribution <https://github.com/eclypse-org/eclypse/tree/main/examples/user_distribution>`_
directory.

Run it from the repository root with:

.. code-block:: bash

   poetry run user-distribution

Infrastructure
--------------

.. dropdown:: Infrastructure code

    .. literalinclude:: ../../../../examples/user_distribution/infrastructure.py
        :language: python

Metrics
-------

.. dropdown:: Metrics code

    .. literalinclude:: ../../../../examples/user_distribution/metric.py
        :language: python

Simulation
----------

.. dropdown:: Simulation code

    .. literalinclude:: ../../../../examples/user_distribution/main.py
        :language: python
