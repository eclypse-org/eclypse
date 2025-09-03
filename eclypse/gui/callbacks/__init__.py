from __future__ import annotations

from typing import TYPE_CHECKING

from .buttons import register_button_callbacks
from .info_box import register_info_box_callbacks
from .network import register_network_callbacks
from .plots import register_plots_callbacks

if TYPE_CHECKING:
    from dash import Dash
    from eclypse.simulation import Simulation


def register_callbacks(app: Dash, sim: Simulation):
    """Register all callbacks for the GUI."""
    register_button_callbacks(app, sim)
    register_info_box_callbacks(app, sim)
    register_network_callbacks(app, sim)
    register_plots_callbacks(app, sim)
