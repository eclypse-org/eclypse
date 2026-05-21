Off-the-shelf
=============

This example shows a complete local simulation built only from reusable ECLYPSE
components:

- the :func:`~eclypse.builders.application.get_hotel_reservation` application builder
- an infrastructure builder from :mod:`eclypse.builders.infrastructure`
- built-in update policies from :mod:`eclypse.policies`
- a built-in placement strategy

Use it when you want a minimal reference for composing existing building blocks
without writing custom services, topologies, or policy callables.

The full code lives in the
`examples/off_the_shelf <https://github.com/eclypse-org/eclypse/tree/main/examples/off_the_shelf>`_
directory.

Run it from the repository root with:

.. code-block:: bash

   uv run off-the-shelf

Application
-----------

The application is the built-in hotel reservation graph, paired with built-in
uniform-distribution and degradation policies that progressively make
placement harder.

ECLYPSE also provides several other ready-made application builders collected
in :mod:`eclypse.builders.application`.

.. dropdown:: Application code

    .. literalinclude:: ../../../../examples/off_the_shelf/application.py
        :language: python


Infrastructure
--------------

The infrastructure is a generated hierarchical topology using the default
assets and a built-in policy mix for flapping availability, uniform
perturbations, periodic latency spikes, and scheduled degradation. ECLYPSE also
provides several other off-the-shelf infrastructure builders collected in
:mod:`eclypse.builders.infrastructure`. Together with ``BestFitStrategy``, this
example exercises repeated placement under a changing environment.

.. dropdown:: Infrastructure code

    .. literalinclude:: ../../../../examples/off_the_shelf/infrastructure.py
        :language: python


Simulation
----------

The simulation registers the built-in application on the generated
infrastructure with a built-in placement strategy and runs it locally.

.. dropdown:: Simulation code

    .. literalinclude:: ../../../../examples/off_the_shelf/main.py
        :language: python

What to inspect
---------------

This example is the quickest template for a local experiment built from
existing components. Inspect placement changes and application-level metrics as
the infrastructure policies make resources less stable.

Related concepts:

- :doc:`../concepts/builders`
- :doc:`../concepts/update-policy`
- :doc:`../concepts/placement-strategy`
