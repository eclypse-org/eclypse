Placement Strategy
==================

Placement strategies in ECLYPSE determine how services are deployed across the simulated infrastructure.
By defining these strategies, you can experiment with various deployment approaches, optimize resource utilisation, and analsze their effects on application performance.

You can choose to define a strategy for each application in your simulation, or use a *global* one, to be assigned to the infrastructure on which you are deploying your applications

What is a Placement Strategy?
-----------------------------

A Placement Strategy is a set of rules or logic that determines how services in your application are allocated to the available infrastructure.
This can include considerations like resource availability, network latency, or service-specific requirements.

ECLYPSE provides built-in strategies, but you can also define custom strategies to fit your specific needs.

Key Benefits
""""""""""""

- Simulate real-world deployment scenarios.
- Test and optimize strategies before deploying to production environments.
- Gain insights into the impact of different placement decisions.

Implement your own strategy
---------------------------------

Creating a custom Placement Strategy in ECLYPSE involves writing a Python class that implements the logic for your desired strategy. Below is a step-by-step guide:

1. **Define a python class for your strategy:**

   Your class must inherit from the :py:class:`~eclypse.placement.strategies.strategy.PlacementStrategy` provided by ECLYPSE.

2. **Implement the required method:**

   Override the :py:meth:`~eclypse.placement.strategies.strategy.PlacementStrategy.place` method in your class.

   This method takes information about the infrastructure *I*, the application *A*, and the other placed applications,
   and outputs a mapping of services of *A* to infrastructure nodes of *I*.

3. **Add custom logic:**

   Access to node/link resources, service/interaction requirements related to the current simulation status,
   to customise your placement rules.

Example
-------

The ``EnergyMinimizationStrategy`` is an example of a placement strategy that aims to minimize
energy consumption when allocating services. It considers the energy required by various resources
(CPU, GPU, RAM, and storage) and assigns services to nodes that minimize overall energy usage.

- **Objective**: Place services to minimize energy consumption based on weighted factors for resource usage (CPU, GPU, RAM, and storage).
- **Customizability**: The strategy allows for weights to be adjusted, enabling a focus on specific resources for energy optimization.
- **Logic**:

  - Iterate through services in the application.
  - For each service, calculate the energy usage for all feasible nodes.
  - Select the node with the lowest energy cost that satisfies the resource requirements.
  - Update the available resources of the selected node for subsequent placements.
  - Return the final **mapping** of services to nodes.

.. dropdown:: EnergyMinizationStrategy code

    .. literalinclude:: ../../../../examples/grid-analysis/strategy.py
        :language: python

Include the strategy into your Simulation
-----------------------------------------

Once you've defined a Placement Strategy, you can add it to your simulation in two ways:

1. **app-dependent**: by passing it to the :py:meth:`~eclypse_core.simulation.simulation.Simulation.register` method when adding a new application to the simulation.
2. **global**: by setting it in the :py:class:`~eclypse.graph.infrastructure.Infrastructure` object during its creation using the constructor or the off-the-shelf builder methods.

**N.B.** The second method (setting it in the ``Infrastructure``) always overrides the strategy set via the ``register`` method.

.. dropdown:: App-dependent strategy
   :open:

   .. code-block:: python

      from eclypse.simulation import Simulation
      from eclypse.graph import Application
      from my_strategies import EnergyMinimizationStrategy

      simulation = Simulation(...)
      application = Application(...)

      strategy = EnergyMinimizationStrategy(
         cpu_weight=0.4,
         gpu_weight=0.3,
         ram_weight=0.2,
         storage_weight=0.1
      )
      simulation.register(application, strategy) # <-- Include the strategy

      # <your code to run the simulation>

.. dropdown:: Global strategy

   .. code-block:: python
      :force:

      from eclypse.graph import Infrastructure
      from my_strategies import EnergyMinimizationStrategy

      strategy = EnergyMinimizationStrategy(
         cpu_weight=0.4,
         gpu_weight=0.3,
         ram_weight=0.2,
         storage_weight=0.1
      )
      # Include the strategy
      infrastructure = Infrastructure(..., placement_strategy=strategy)


      # <your code to run the simulation>
