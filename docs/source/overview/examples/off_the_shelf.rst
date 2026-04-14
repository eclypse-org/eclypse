Off-the-shelf
=============

This example shows a complete local simulation built only from reusable ECLYPSE
components:

- the :func:`~eclypse.builders.application.get_sock_shop` application builder
- the :func:`~eclypse.builders.infrastructure.hierarchical` infrastructure builder
- built-in update policies from :mod:`eclypse.policies`
- a built-in placement strategy

Use it when you want a minimal reference for composing existing building blocks
without writing custom services, topologies, or policy callables.

The full code lives in the
`examples/off_the_shelf <https://github.com/eclypse-org/eclypse/tree/main/examples/off_the_shelf>`_
directory.

Application
-----------

The application is the standard Sock Shop graph created through the built-in
builder, with built-in uniform-distribution and degradation policies that
progressively make placement harder.

.. dropdown:: Application code

    .. literalinclude:: ../../../../examples/off_the_shelf/application.py
        :language: python


Infrastructure
--------------

The infrastructure is a generated hierarchical topology using the default
assets and a built-in policy mix for flapping availability, uniform
perturbations, periodic latency spikes, and scheduled degradation. Together with
``BestFitStrategy``, this makes the example exercise repeated placement under a
changing environment.

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
