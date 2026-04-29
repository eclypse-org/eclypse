Image prediction
================

The image prediction example shows a remote application with trainer,
predictor, and end-user services. It combines service implementations, custom
metrics, and a degradation policy in emulation mode.

Use it when you want to understand:

- how to attach concrete service implementations to an application,
- how to configure a remote simulation,
- how to collect custom metrics from remote service behaviour.

The full code lives in the
`examples/image_prediction <https://github.com/eclypse-org/eclypse/tree/main/examples/image_prediction>`_
directory.

Run it from the repository root with:

.. code-block:: bash

   uv run image-prediction

Application
-----------

.. dropdown:: Application code

    .. literalinclude:: ../../../../examples/image_prediction/application.py
        :language: python

Simulation
----------

.. dropdown:: Simulation code

    .. literalinclude:: ../../../../examples/image_prediction/main.py
        :language: python

Metrics
-------

.. dropdown:: Metrics code

    .. literalinclude:: ../../../../examples/image_prediction/metrics.py
        :language: python
