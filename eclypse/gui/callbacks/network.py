from __future__ import annotations

from typing import TYPE_CHECKING

from dash import (
    Input,
    Output,
    State,
)

if TYPE_CHECKING:
    from dash import Dash

    from eclypse.simulation import Simulation


def register_network_callbacks(app: Dash, _: Simulation):
    """Register callbacks for the network-related components in the GUI."""

    @app.callback(
        Output("cytoscape", "elements", allow_duplicate=True),
        Output("selected-node-id", "data"),
        Input("cytoscape", "tapNodeData"),
        State("selected-node-id", "data"),
        State("cytoscape", "elements"),
    )
    def highlight_selected_node(node_data, selected_id, elements):
        if not node_data:
            return elements, None

        current_id = node_data["id"]

        # Unselect if already selected
        if selected_id == current_id:
            for el in elements:
                el["classes"] = (
                    el.get("classes", "").replace("selected-node", "").strip()
                )
            return elements, None

        # Otherwise select
        for el in elements:
            el["classes"] = el.get("classes", "").replace("selected-node", "").strip()
            if el["data"].get("id") == current_id:
                el["classes"] += " selected-node"

        return elements, current_id

    @app.callback(
        Output("cytoscape", "elements", allow_duplicate=True),
        Output("selected-link-id", "data"),
        Input("cytoscape", "tapEdgeData"),
        State("selected-link-id", "data"),
        State("cytoscape", "elements"),
    )
    def highlight_selected_edge(edge_data, selected_id, elements):
        if not edge_data:
            for el in elements:
                el["classes"] = (
                    el.get("classes", "").replace("selected-node", "").strip()
                )

        current = (edge_data["source"], edge_data["target"])

        # Unselect if already selected
        if selected_id and tuple(selected_id) == current:
            for el in elements:
                el["classes"] = (
                    el.get("classes", "").replace("selected-edge", "").strip()
                )
            return elements, None

        # Otherwise select
        for el in elements:
            el["classes"] = el.get("classes", "").replace("selected-edge", "").strip()
            if (
                el["data"].get("source") == current[0]
                and el["data"].get("target") == current[1]
            ):
                el["classes"] += " selected-edge"

        return elements, current

    @app.callback(
        Output("cytoscape", "elements", allow_duplicate=True),
        Input("cytoscape", "elements"),
    )
    def constrain_node_positions(elements):
        # Trova limiti attuali (solo nodi)
        node_positions = [el["position"] for el in elements if "position" in el]
        if not node_positions:
            return elements

        # Applica vincoli
        for el in elements:
            if "position" in el:
                el["position"]["x"] = max(-20, min(el["position"]["x"], 120))
                el["position"]["y"] = max(-20, min(el["position"]["y"], 120))

        return elements

    @app.callback(
        Output("node-position-cache", "data", allow_duplicate=True),
        Input("cytoscape", "elements"),
    )
    def save_node_positions(elements):
        node_positions = {
            el["data"]["id"]: el["position"]
            for el in elements
            if "position" in el and "id" in el["data"]
        }

        return node_positions
