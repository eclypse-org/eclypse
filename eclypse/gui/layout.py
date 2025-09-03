from __future__ import annotations

from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
from dash import (
    dcc,
    html,
)

from eclypse.gui.components import (
    control_buttons,
    graph_component,
    info_card,
    metrics_tabs,
    simulation_status_card,
)
from eclypse.gui.utils import to_cytoscape_elements

if TYPE_CHECKING:
    from eclypse.simulation import Simulation


def serve_layout(sim: Simulation):

    elements = to_cytoscape_elements(sim)

    return dbc.Container(
        [
            html.H2("ECLYPSE Simulation Dashboard", className="mt-4 text-center"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            control_buttons(),
                            simulation_status_card(sim),
                            info_card("node", "services"),
                            info_card("link", "interactions"),
                        ],
                        width=3,
                        className="mx-auto",
                    ),
                    dbc.Col(
                        graph_component(elements, "grid"),
                        width=5,
                    ),
                    dbc.Col(
                        [
                            metrics_tabs(sim, kind="node"),
                            metrics_tabs(sim, kind="link"),
                        ],
                        width=4,
                    ),
                ],
                className="mb-3",
            ),
            dcc.Store(id="selected-node-id", data=None),
            dcc.Store(id="selected-link-id", data=None),
            dcc.Store(id="node-position-cache", data=None),
            dcc.Store(id="step-counter", data=0),
            dcc.Interval(
                id="auto-step-interval",
                interval=1000,
                n_intervals=0,
                disabled=True,
            ),
        ],
        fluid=True,
    )
