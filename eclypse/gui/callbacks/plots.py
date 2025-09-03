# pylint: disable=protected-access
from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.express as px
from dash import (
    Input,
    Output,
    State,
)
from dash.exceptions import PreventUpdate

if TYPE_CHECKING:
    from dash import Dash

    from eclypse.simulation import Simulation


def register_plots_callbacks(app: Dash, sim: Simulation):
    """Register callbacks for the plots in the GUI."""

    gui_reporter = sim.simulator._reporter.reporters["gui"]

    node_metrics = [
        e.name for e in sim._sim_config.events if e.type == "node" and e.is_callback
    ]
    link_metrics = [
        e.name for e in sim._sim_config.events if e.type == "link" and e.is_callback
    ]

    @app.callback(
        Output("node-metric-tabs", "children", allow_duplicate=True),
        Input("selected-node-id", "data"),
        State("node-metric-tabs", "children"),
    )
    def build_node_tabs(node_id, current_tabs):
        if not node_id:
            raise PreventUpdate
        return current_tabs

    @app.callback(
        Output("link-metric-tabs", "children", allow_duplicate=True),
        Input("selected-link-id", "data"),
        State("link-metric-tabs", "children"),
    )
    def build_link_tabs(link_data, current_tabs):
        if not link_data:
            raise PreventUpdate
        return current_tabs

    for node_metric in node_metrics:
        graph_id = f"graph-node-{node_metric}"

        @app.callback(
            Output(graph_id, "figure"),  # pylint: disable=cell-var-from-loop
            Input("auto-step-interval", "n_intervals"),
            Input("start-btn", "n_clicks"),
            Input("step-btn", "n_clicks"),
            Input("selected-node-id", "data"),
            prevent_initial_call=True,
        )
        def update_node_fig(_, __, ___, node_id, metric=node_metric):
            if not node_id:
                raise PreventUpdate

            df = gui_reporter.get_dataframe("node", callback_id=metric, node_id=node_id)
            if df.empty:
                return px.line(title=f"No data for {metric} on Node {node_id}")
            return px.line(
                df, x="n_event", y="value", title=f"{metric} - Node {node_id}"
            )

    for link_metric in link_metrics:
        graph_id = f"graph-link-{link_metric}"

        @app.callback(
            Output(graph_id, "figure"),  # pylint: disable=cell-var-from-loop
            Input("auto-step-interval", "n_intervals"),
            Input("start-btn", "n_clicks"),
            Input("step-btn", "n_clicks"),
            Input("selected-link-id", "data"),
            prevent_initial_call=True,
        )
        def update_link_fig(_, __, ___, link_data, metric=link_metric):
            if not link_data or len(link_data) < 2:
                raise PreventUpdate

            src, tgt = link_data
            df = gui_reporter.get_dataframe(
                "link", callback_id=metric, source=src, target=tgt
            )
            if df.empty:
                return px.line(title=f"No data for {metric} on Link {src} → {tgt}")
            return px.line(
                df, x="n_event", y="value", title=f"{metric} - {src} → {tgt}"
            )
