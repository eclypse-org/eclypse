from __future__ import annotations

from typing import TYPE_CHECKING

from dash import (
    Input,
    Output,
    State,
    html,
)

if TYPE_CHECKING:
    from dash import Dash

    from eclypse.simulation import Simulation


def register_info_box_callbacks(app: Dash, sim: Simulation):
    """Register callbacks for the buttons in the GUI."""

    @app.callback(
        Output("node-info-header", "children"),
        Output("hosted-services", "children"),
        Output("node-resources", "children"),
        Input("selected-node-id", "data"),
        Input("step-btn", "n_clicks"),
        Input("auto-step-interval", "n_intervals"),
    )
    def update_node_info(node_id, _, __):
        if not node_id:
            return "No node selected", "--", "--"

        services = {
            app: placement.services_on_node(node_id)
            for app, placement in sim.simulator.placements.items()
        }
        node_data = sim.infrastructure.nodes[node_id]

        # Hosted services section
        if services:
            services_items = []
            for app, servs in services.items():
                label = f"{app}" + (": -- " if not servs else "")
                services_items.append(html.Div(f"{label}", className="fw-semibold"))
                services_items.append(
                    html.Ul([html.Li(s) for s in servs], className="mb-2")
                )
        else:
            services_items = [html.Div("--", className="text-muted")]

        # Node resources section
        if node_data:
            resources_items = [
                html.Li([html.Strong(f"{k}: \t"), f"{round(v,2)}"])
                for k, v in node_data.items()
            ]
        else:
            resources_items = [html.Div("--", className="text-muted")]

        return (
            f"Node: {node_id}",
            html.Ul(services_items, className="mb-2"),
            html.Ul(resources_items, className="mb-2"),
        )

    @app.callback(
        Output("link-info-header", "children"),
        Output("hosted-interactions", "children"),
        Output("link-resources", "children"),
        Input("selected-link-id", "data"),
        Input("step-btn", "n_clicks"),
        Input("auto-step-interval", "n_intervals"),
    )
    def update_edge_info_card(link_id, _, __):
        if not link_id:
            return "No link selected", "--", "--"

        src, tgt = link_id
        interactions = {
            app: placement.interactions_on_link(src, tgt)
            for app, placement in sim.simulator.placements.items()
        }

        # Hosted interactions section
        if interactions:
            interactions_items = []
            for app, inters in interactions.items():
                if not inters:
                    continue
                interactions_items.append(html.Div(f"{app}", className="fw-semibold"))
                interactions_items.append(
                    html.Ul(
                        [html.Li(f"{s} → {d}") for s, d in inters], className="mb-2"
                    )
                )
        else:
            interactions_items = [html.Div("No interactions", className="text-muted")]

        # Link resources section
        link_data = sim.infrastructure.edges[src, tgt]
        if link_data:
            resources_items = [
                html.Li([html.Strong(f"{k}: \t"), f"{round(v,2)}"])
                for k, v in link_data.items()
            ]
        else:
            resources_items = [html.Div("--", className="text-muted")]

        return (
            f"Link: {src} → {tgt}",
            html.Ul(interactions_items, className="mb-2"),
            html.Ul(resources_items, className="mb-2"),
        )

    @app.callback(
        Output("step-counter", "data"),
        Input("step-btn", "n_clicks"),
        Input("auto-step-interval", "n_intervals"),
        State("step-counter", "data"),
    )
    def increment_step(_, __, step):
        return step + 1

    @app.callback(
        Output("step-display", "children"),
        Input("step-counter", "data"),
    )
    def show_step(step):
        return str(step)
