# Echo

The Echo example showcases a small service-based application in which messages
are exchanged repeatedly among neighbouring services.

Use it when you want to understand:

- how to build an application and an infrastructure from Python code,
- how to run a remote emulation end to end,
- how MPI-style communication behaves in a simple topology.

The full code lives in the
[examples/echo](https://github.com/eclypse-org/eclypse/tree/main/examples/echo)
directory.

Run it from the repository root with:

```bash
uv run python -m examples.echo.main
```

## Application

The Echo Application consists of several identical services, each of which receives a message and echoes it back to all of its neighbors. This symmetrical architecture ensures that each service behaves identically.

As each service echoes messages both by broadcasting to all neighbors and unicasting individually to each neighbour, it is useful to compare the expected results of these two communication methods.
Broadcasting is expected to be faster than unicasting, as it involves sending messages to all neighbors simultaneously. Unicasting, on the other hand, requires sending a separate message to each neighbor, which can result in a longer total communication time.

??? example "Application code"

    ```python
    --8<-- "examples/echo/application.py"
    ```

## Echo Service

The `EchoService` class is the runtime component responsible for sending
messages to neighbour services and measuring the difference between unicast and
broadcast communication.

??? example "Service code"

    ```python linenums="1"
    --8<-- "examples/echo/echo.py"
    ```

The service inherits from
[Service][eclypse.remote.service.service.Service] and implements
[step][eclypse.remote.service.service.Service.step], which is the unit of
behaviour executed during emulation.

## Infrastructure

The Echo application is deployed on a small infrastructure made of heterogeneous
nodes connected through links with different latency and bandwidth values.

??? example "Infrastructure code"

    ```python
    --8<-- "examples/echo/infrastructure.py"
    ```

The infrastructure is also updated at each iteration through a graph update
policy that mutates both nodes and links to simulate changing runtime
conditions.

??? example "Update policy code"

    ```python
    --8<-- "examples/echo/update_policy.py"
    ```

## Simulation

The example configures a reproducible run with metrics enabled and stores the
results under the default simulation path.

??? example "Simulation code"

    ```python
    --8<-- "examples/echo/main.py"
    ```

## What to inspect

After the run, compare the communication metrics produced by unicast and
broadcast exchanges. This example is a good template when you want to test a
small emulated service loop before moving to a larger application.

Related concepts:

- [Messaging](../advanced/emulation/messaging.md)
- [Reporting](../advanced/reporting.md)
