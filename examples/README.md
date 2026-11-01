# ECLYPSE Examples

Run examples from the repository root, after `make setup`. Examples with a `requirements.txt` install their extra dependencies on the fly.

| Name | Demonstrates | How to run | Docs |
| --- | --- | --- | --- |
| Echo | A small application comparing service communication patterns. | `uv run python -m examples.echo.main` | `docs/source/overview/examples/echo.rst` |
| Off the shelf | Built-in infrastructure, application, placement, and metrics. | `uv run python -m examples.off_the_shelf.main` | `docs/source/overview/examples/off_the_shelf.rst` |
| Sock Shop MPI | Remote emulation of the Sock Shop application using MPI communication. | `uv run python -m examples.sock_shop.mpi` | `docs/source/overview/examples/sock_shop.rst` |
| Sock Shop REST | Remote emulation of the Sock Shop application using REST communication. | `uv run python -m examples.sock_shop.rest` | `docs/source/overview/examples/sock_shop.rst` |
| Grid analysis | Ray Tune parameter sweeps over topologies, policies, and strategies. | `uv run --with-requirements examples/grid_analysis/requirements.txt python -m examples.grid_analysis.main` | `docs/source/overview/examples/grid_analysis.rst` |
| Image prediction | Remote image-prediction services with custom metrics and degradation. | `uv run --with-requirements examples/image_prediction/requirements.txt python -m examples.image_prediction.main` | `docs/source/overview/examples/image_prediction.rst` |
| User distribution | User-distribution-driven infrastructure changes and custom metrics. | `uv run --with-requirements examples/user_distribution/requirements.txt python -m examples.user_distribution.main` | `docs/source/overview/examples/user_distribution.rst` |
