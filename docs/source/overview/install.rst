===============
Install ECLYPSE
===============

ECLYPSE currently supports only installation **from source**, which still remains very simple, given the framework's few dependencies.

.. note::

    Do not use the global environment to install ECLYPSE.
    It is recommended to create a `virtual environment <https://docs.python.org/3/library/venv.html>`_ first.

Building from source
====================

To install ECLYPSE, you can follow these steps:

1. **Clone the Repository**:

   .. code-block:: bash

      git clone https://github/eclypse-org/eclypse
      cd eclypse

2. **Build and Install**:

   You can use the provided `Makefile <https://github.com/eclypse-org/eclypse/blob/main/Makefile>`_ to build and install ECLYPSE:

   .. code-block:: bash

      make install

   This command will download all the necessary requirements and install ECLYPSE
   in your environment, as a standalone library.
