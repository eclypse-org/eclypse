from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.simulation import Simulation

FONT_AWESOME_ICONS = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.0/css/all.min.css"
)
DEFAULT_STYLESHEET = [
    {
        "selector": "node",
        "style": {
            "label": "data(id)",
            "text-valign": "center",
            "text-halign": "center",
            "width": "12",
            "height": "12",
            "font-size": "4",
            "color": "#fff",
            "background-color": "#88f",
        },
    },
    {"selector": ".high", "style": {"background-color": "#f55"}},
    {"selector": "edge", "style": {"width": ".5", "line-color": "#888"}},
    {
        "selector": ".selected-node",
        "style": {
            "border-color": "#ffc107",
            "border-width": 0.8,
            "border-style": "solid",
        },
    },
    {"selector": ".selected-edge", "style": {"line-color": "#ffc107", "width": 1}},
]


def to_cytoscape_elements(sim: Simulation):
    infr = sim.infrastructure.available
    nodes = []

    for node_id in infr.nodes():
        node = {
            "data": {"id": str(node_id)},
        }

        nodes.append(node)

    edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in infr.edges()]

    return nodes + edges
