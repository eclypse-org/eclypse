from __future__ import annotations

from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import (
    dcc,
    html,
)

from eclypse.gui.utils import DEFAULT_STYLESHEET

if TYPE_CHECKING:
    from eclypse.simulation import Simulation


def simulation_status_card(simulation: Simulation):

    infrastructure_id = simulation.infrastructure.id
    application_ids = ",".join(simulation.applications.keys())
    return dbc.Card(
        [
            dbc.CardHeader("Simulation Status", className="fw-bold"),
            dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        ["Step: ", html.Span(id="step-display", className="fw-bold")]
                    ),
                    dbc.ListGroupItem(["Infrastructure: ", html.Em(infrastructure_id)]),
                    dbc.ListGroupItem(["Application(s): ", html.Em(application_ids)]),
                ],
                flush=True,
            ),
        ],
        className="mb-3",
    )


def control_buttons():
    return dbc.ButtonGroup(
        [
            dbc.Button(
                [html.I(className="fa-solid fa-play"), "Start"],
                id="start-btn",
                color="success",
                disabled=False,
            ),
            dbc.Button(
                [html.I(className="fa-solid fa-pause me-2"), "Pause"],
                id="pause-btn",
                color="warning",
                disabled=False,
            ),
            dbc.Button(
                [html.I(className="fa-solid fa-step-forward me-2"), "Step"],
                id="step-btn",
                color="primary",
                disabled=True,
            ),
            dbc.Button(
                [html.I(className="fa-solid fa-stop me-2"), "Stop"],
                id="stop-btn",
                color="danger",
                disabled=False,
            ),
        ],
        className="mb-3",
    )


def graph_component(elements, layout):
    return cyto.Cytoscape(
        id="cytoscape",
        layout=(
            (
                {
                    "name": layout,
                    "animate": False,
                    "boundingBox": {"x1": 0, "y1": 0, "x2": 100, "y2": 100},
                    "responsive": True,
                }
            )
            if layout
            else "preset"
        ),
        userZoomingEnabled=False,
        boxSelectionEnabled=False,
        autoungrabify=False,
        style={"width": "100%", "height": "100%"},
        elements=elements,
        stylesheet=DEFAULT_STYLESHEET,
    )


def info_card(kind: str, hosting: str):
    return dbc.Card(
        [
            dbc.CardHeader(
                id=f"{kind}-info-header",
                children=f"No {kind} selected",
                className="fw-bold",
            ),
            dbc.ListGroup(
                flush=True,
                children=[
                    dbc.ListGroupItem(
                        html.Div(
                            [
                                html.I(className="fa-solid fa-gears me-2"),
                                html.Strong(f"Hosted {hosting.title()}"),
                                html.Div(id=f"hosted-{hosting}", children="--"),
                            ],
                            className="mb-1",
                        ),
                        color="info",
                    ),
                    dbc.ListGroupItem(
                        html.Div(
                            [
                                html.I(className="fa-solid fa-chart-simple me-2"),
                                html.Strong(f"{kind.title()} Resources"),
                                html.Div(id=f"{kind}-resources", children="--"),
                            ],
                            className="mb-1",
                        ),
                        color="success",
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def link_info_card():
    return dbc.Card(
        [
            dbc.CardHeader(
                id="link-info-header", children="No link selected", className="fw-bold"
            ),
            dbc.ListGroup(
                flush=True,
                children=[
                    dbc.ListGroupItem(
                        html.Div(
                            [
                                html.I(className="fa-solid fa-gears me-2"),
                                html.Strong("Interactions"),
                                html.Div(id="hosted-interactions", children="--"),
                            ],
                            className="mb-1",
                        ),
                        color="info",
                    ),
                    dbc.ListGroupItem(
                        html.Div(
                            [
                                html.I(className="fa-solid fa-chart-simple me-2"),
                                html.Strong("Link Resources"),
                                html.Div(id="link-resources", children="--"),
                            ],
                            className="mb-1",
                        ),
                        color="success",
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def metrics_tabs(simulation: Simulation, kind: str):
    metrics = [
        e.name
        for e in simulation._sim_config.events  # pylint: disable=protected-access
        if e.type == kind and e.is_callback
    ]

    return dcc.Loading(
        dcc.Tabs(
            id=f"{kind}-metric-tabs",
            children=[
                dcc.Tab(label=metric, children=[dcc.Graph(id=f"graph-{kind}-{metric}")])
                for metric in metrics
            ],
        ),
        type="graph",
    )
