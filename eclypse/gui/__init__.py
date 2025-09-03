# pylint: disable=import-outside-toplevel,protected-access
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.simulation import Simulation


def launch_gui(
    simulation: Simulation,
    host: str = "127.0.0.1",
    port: int = 8050,
    **dash_kwargs,
):
    """Launch the GUI for the simulation.

    Args:
        simulation (Simulation): The simulation to visualize.
        host (str, optional): The host to run the GUI on. Defaults to "127.0.0.1".
        port (int, optional): The port to run the GUI on. Defaults to 8050.
        **dash_kwargs: Additional keyword arguments to pass to the Dash app.
    """

    import dash_bootstrap_components as dbc
    from dash import Dash

    from eclypse.gui.callbacks import register_callbacks
    from eclypse.gui.layout import serve_layout
    from eclypse.gui.reporter import GUIReporter
    from eclypse.gui.utils import FONT_AWESOME_ICONS

    app = Dash(
        "ECLYPSE GUI",
        external_stylesheets=[
            dbc.themes.ZEPHYR,
            FONT_AWESOME_ICONS,
        ],
        prevent_initial_callbacks=True,
        suppress_callback_exceptions=True,
    )
    app.layout = serve_layout(simulation)

    simulation.simulator._reporter.add_reporter("gui", GUIReporter)
    for e in simulation._sim_config.events:
        if e.is_callback:
            e.report_types.append("gui")

    register_callbacks(app, simulation)
    app.run(host=host, port=port, **dash_kwargs)
