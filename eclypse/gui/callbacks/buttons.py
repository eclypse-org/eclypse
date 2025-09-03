# pylint: disable=protected-access
from __future__ import annotations

from typing import TYPE_CHECKING

from dash import (
    Input,
    Output,
    State,
    callback_context,
    no_update,
)

from eclypse.gui.utils import to_cytoscape_elements

if TYPE_CHECKING:
    from dash import Dash

    from eclypse.simulation import Simulation


def register_button_callbacks(app: Dash, sim: Simulation):
    """Register callbacks for the buttons in the GUI."""

    @app.callback(
        Output("auto-step-interval", "disabled"),
        Output("start-btn", "disabled"),
        Output("pause-btn", "disabled"),
        Output("step-btn", "disabled"),
        Input("start-btn", "n_clicks"),
        Input("pause-btn", "n_clicks"),
        Input("stop-btn", "n_clicks"),
        State("auto-step-interval", "disabled"),
        State("cytoscape", "elements"),
    )
    def toggle_auto_step(start, _, stop, disabled, __):
        ctx = callback_context.triggered_id
        if ctx == "start-btn" and disabled:
            if start == 1:
                sim.start()
            return False, True, False, True
        if ctx == "pause-btn" and not disabled:
            return True, False, True, False
        if ctx == "stop-btn":
            if stop == 1:
                sim.stop()

            return True, True, True, True

        return no_update

    @app.callback(
        Output("cytoscape", "elements", allow_duplicate=True),
        Input("auto-step-interval", "n_intervals"),
        Input("step-btn", "n_clicks"),
        State("node-position-cache", "data"),
    )
    def step_simulation(_, __):
        sim.step()
        return to_cytoscape_elements(sim)
