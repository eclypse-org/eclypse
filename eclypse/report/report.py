"""Module for Report class, which generates the final report of the simulation.

The report can be generated in multiple formats (HTML, CSV, and JSON). Solely for HTML,
a plot type can be specified for each metric.
"""

from __future__ import annotations

import os
import sys
import warnings
from contextlib import redirect_stdout
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    AnyStr,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    get_args,
)

import datapane as dp
import networkx as nx
import pandas as pd
import plotly.express as px
from eclypse_core.graph.node_group import NodeGroup
from eclypse_core.utils.logging import (
    config_logger,
    logger,
)
from eclypse_core.utils.tools import (
    format_float,
    snake_to_title,
    to_float,
)
from eclypse_core.utils.types import (
    CallbackType,
    PlotType,
)
from pyvis.network import Network

from eclypse.utils import MAX_FLOAT

if TYPE_CHECKING:
    from eclypse_core.utils.logging import Logger

PLOT_LAYOUT_CONFIG = {
    "yaxis_title": None,
    "autosize": False,
    "margin": {"t": 2, "l": 1, "r": 1, "b": 5},
    "sliders": [
        {
            "currentvalue": {
                "prefix": "Tick:",
                "xanchor": "center",
            }
        }
    ],
}

LEGEND_COLORS = {
    NodeGroup.UNSET: ("#eeaaf3", "#df30ef"),
    NodeGroup.IOT: ("#fa7375", "#f9171b"),
    NodeGroup.NEAR_EDGE: ("#70dd39", "#3a9f07"),
    NodeGroup.FAR_EDGE: ("#ffff00", "#ffa007"),
    NodeGroup.CLOUD: ("#8bb8fa", "#2e75e7"),
}

DEFAULT_HTML_REPORT_FILENAME = "report.html"
DEFAULT_TICK_COLUMN = "n_event"
REPORT_WIDTH = dp.Width.FULL
REPORT_ACCENT_COLOR = "#656EF2"
REPORT_TEXT_ALIGNMENT = dp.TextAlignment.JUSTIFY

SIMULATION_PAGE_TITLE = "Simulation"
APPLICATION_PAGE_TITLE = "Applications"
INFRASTRUCTURE_PAGE_TITLE = "Infrastructure"

AGGREGATED_METRIC_WIDTHS = [4, 6]
LINE_WIDTHS = [2, 8]


class Report:
    """The Report class generates the final report of the simulation."""

    def __init__(self, sim_path: Union[Path, str]):
        """Create a new Report with default values.

        Args:
            sim_path (str): The path to the simulation.
        """
        config_logger()
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", category=UserWarning)

        self._sim_path = Path(sim_path)
        self._stats_path = self._sim_path / "stats"
        self._reports_path = self._sim_path / "reports"
        self._gml_path = self._sim_path / "gml"
        self._types = list(get_args(CallbackType))
        self.range: Tuple[int, int] = (0, int(MAX_FLOAT))
        self.step: int = 1
        self.loaded = False

        self.sim_df: Optional[pd.DataFrame] = None
        self.app_df: Optional[pd.DataFrame] = None
        self.infr_df: Optional[pd.DataFrame] = None
        self.srv_df: Optional[pd.DataFrame] = None
        self.int_df: Optional[pd.DataFrame] = None
        self.node_df: Optional[pd.DataFrame] = None
        self.link_df: Optional[pd.DataFrame] = None

    def load_stats(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
    ):
        """Load the statistics of the simulation from the configured path.

        Args:
            report_range (Tuple[int, int], optional): The range of ticks to include
                in the report. Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step between report ticks. Defaults to 1.
        """

        self.sim_df = self.read_csv("simulation")
        try:
            sim_ticks = int(
                self.sim_df[self.sim_df["callback_id"] == "ticks"]["value"].max()
            )
        except:
            self.logger.error("Simulation ticks not monitored.")
            sys.exit(-1)

        self.range = (
            max(report_range[0], 0),
            min(report_range[1], sim_ticks),
        )
        self.step = min(report_step, self.range[1] - self.range[0])

        self.app_df = self.read_csv("application")
        self.infr_df = self.read_csv("infrastructure")
        self.srv_df = self.read_csv("service")
        self.int_df = self.read_csv("interaction")
        self.node_df = self.read_csv("node")
        self.link_df = self.read_csv("link")

        self.logger.info(f"Stats of simulation {self._sim_path} loaded.")
        self.loaded = True

    def to_csv(self, path: Optional[str] = None):
        """Save the reports in CSV format.

        Args:
            path (Optional[str], optional): The path to save the CSV reports.
                Defaults to None.
        """
        if not self.loaded:
            self.load_stats()
        _path: Path = self._reports_path / "csv" if path is None else Path(path)
        _path.mkdir(parents=True, exist_ok=True)
        # for name, df in self._df.items():
        #     if name != "simulation":
        #         df.to_csv(_path / f"{name}.csv", index=False)

        _to_csv(self.app_df, _path / "application.csv")
        _to_csv(self.infr_df, _path / "infrastructure.csv")
        _to_csv(self.srv_df, _path / "service.csv")
        _to_csv(self.int_df, _path / "interaction.csv")
        _to_csv(self.node_df, _path / "node.csv")
        _to_csv(self.link_df, _path / "link.csv")

        self.logger.success(f"CSV reports saved to {_path}")

    def to_json(self, path: Optional[str] = None):
        """Save the reports in JSON format.

        Args:
            path (Optional[str], optional): The path to save the JSON reports.
                Defaults to None.
        """
        if not self.loaded:
            self.load_stats()
        _path: Path = self._reports_path / "json" if path is None else Path(path)
        _path.mkdir(parents=True, exist_ok=True)
        # for name, df in self._df.items():
        #     df.reset_index(inplace=True)
        #     df.to_json(_path / f"{name}.json", orient="records", indent=4)

        _to_json(self.app_df, _path / "application.json")
        _to_json(self.infr_df, _path / "infrastructure.json")
        _to_json(self.srv_df, _path / "service.json")
        _to_json(self.int_df, _path / "interaction.json")
        _to_json(self.node_df, _path / "node.json")
        _to_json(self.link_df, _path / "link.json")

        self.logger.success(f"JSON reports saved to {_path}")

    def to_html(
        self,
        path: Optional[str] = None,
        plot_types: Optional[Dict[str, PlotType]] = None,
        open_html: bool = False,
    ):
        """Save the reports in HTML format.

        Args:
            path (Optional[str], optional): The path to save the HTML report.
                Defaults to None.
            plot_types (Optional[Dict[str, PlotType]], optional): The plot types for each
                metric. Defaults to None.
            open_html (bool, optional): Whether to open the HTML report in the default
                browser. Defaults to False.
        """
        if not self.loaded:
            self.load_stats()
        plot_types = {} if plot_types is None else plot_types
        pages = [
            self.simulation_page(),
            self.applications_page(plot_types),
            self.infrastructure_page(plot_types),
        ]
        if self._gml_path.exists():
            pages.append(self.gml_page())
        _path: Path = self._reports_path if path is None else Path(path)
        _path.mkdir(parents=True, exist_ok=True)
        _path = _path / DEFAULT_HTML_REPORT_FILENAME
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            with redirect_stdout(devnull):
                dp.save_report(
                    blocks=pages,
                    formatting=_get_html_formatting(),
                    path=_path,
                    open=open_html,
                )

        self.logger.success(f"HTML report saved to {_path}")

    def simulation_page(self) -> dp.Page:
        """Create the simulation metrics page.

        Returns:
            dp.Page: The simulation metrics page.
        """
        with open(self._sim_path / "config.json", "r") as f:
            config = pd.read_json(f, typ="series")
            params = []
            for key, value in config.items():
                if len(str(value)) > 50:
                    params.append(
                        f"""
                        <div data-cy="block-bignumber" class="rounded-md bg-white overflow-hidden border border-gray-300 w-full">
                            <div class="px-4 py-5 sm:p-6">
                                <dl>
                                    <dt>{snake_to_title(key)}</dt>
                                    <dd>{value}</dd>
                                </dl>
                            </div>
                        </div>
                        """
                    )
                else:
                    params.append(_big_number(key, str(value)))

            ticks = [
                _big_number("Start Tick", self.range[0]),
                _big_number("End Tick", self.range[1]),
                _big_number("Step", self.step),
            ]

            return dp.Page(
                title=SIMULATION_PAGE_TITLE,
                blocks=[
                    "## Simulation Configuration",
                    dp.Group(blocks=params, columns=2),  # len(numbers)),
                    "## Report Range",
                    dp.Group(blocks=ticks, columns=len(ticks)),
                ],
            )

    def applications_page(self, plot_types: Dict[str, PlotType]) -> dp.Page:
        """Create the applications page with all the application metrics, for each
        applicationnvolved in the simulation. Also includes the service and interaction
        metrics.

        Returns:
            dp.Page: The applications page.
        """

        has_sm = self.srv_df is not None
        has_im = self.int_df is not None

        if self.app_df is not None:
            apps = self.app_df["app_id"].unique()
        elif self.srv_df is not None:
            apps = self.srv_df["app_id"].unique()
        elif self.int_df is not None:
            apps = self.int_df["app_id"].unique()
        else:
            self.logger.error("No application data found.")
            return dp.Page(title="Applications", blocks=[dp.Text("No data found.")])

        app_metrics = list(self.app_df["callback_id"].unique())
        srv_metrics = list(self.srv_df["callback_id"].unique()) if has_sm else []
        int_metrics = list(self.int_df["callback_id"].unique()) if has_im else []

        blocks = [dp.Text(f"## {APPLICATION_PAGE_TITLE} Metrics")]
        blocks.append(
            dp.Group(
                _big_number("Applications", apps.size),
                _big_number(
                    "Application Metrics", len(app_metrics) if app_metrics else "N/A"
                ),
                _big_number(
                    "Service Metrics", len(srv_metrics) if srv_metrics else "N/A"
                ),
                _big_number(
                    "Interaction Metrics", len(int_metrics) if int_metrics else "N/A"
                ),
                columns=4,
            ),
        )

        for app in apps:
            blocks.append(dp.HTML("<hr>"))
            blocks.append(dp.Text(f"### {app}"))
            app_blocks = []
            for metric in _aggregation_dict(*app_metrics, *srv_metrics, *int_metrics):
                df = self.app_df[
                    (self.app_df["app_id"] == app)
                    & (self.app_df["callback_id"].str.contains(metric))
                ]

                df_svs = (
                    self.srv_df[
                        (self.srv_df["app_id"] == app)
                        & (self.srv_df["callback_id"].str.contains(metric))
                    ]
                    if has_sm
                    else None
                )

                df_int = (
                    self.int_df[
                        (self.int_df["app_id"] == app)
                        & (self.int_df["callback_id"].str.contains(metric))
                    ]
                    if has_im
                    else None
                )
                fig_app, fig_by = None, None
                by = "service"
                if any(metric in m for m in app_metrics):
                    fig_app = _line(metric, df=df, x=DEFAULT_TICK_COLUMN, y="value")
                if metric in srv_metrics:
                    fig_by = self._plot_by_type(
                        metric, plot_types, df=df_svs, x="service_id", y="value"
                    )
                if metric in int_metrics:
                    by = "interaction"
                    x = df_int["source"] + " -- " + df_int["target"]
                    fig_by = self._plot_by_type(
                        metric, plot_types, df=df_int, x=x, y="value"
                    )

                if fig_by:
                    if fig_app:
                        app_blocks.append(
                            _aggregated_group(fig_app, fig_by, by, metric)
                        )
                    else:
                        app_blocks.append(fig_by)
                else:
                    app_blocks.insert(0, fig_app)

            numbers = dp.Group(
                _big_number(
                    "Services",
                    self.srv_df["service_id"].unique().size if has_sm else "N/A",
                ),
                _big_number(
                    "Interactions",
                    (
                        self.int_df.groupby(["source", "target"]).ngroups
                        if has_im
                        else "N/A"
                    ),
                ),
            )

            blocks.append(
                dp.Group(
                    blocks=[numbers, _select(app_blocks)], columns=2, widths=LINE_WIDTHS
                )
            )

        return dp.Page(title="Applications", blocks=blocks)

    def infrastructure_page(self, plot_types: Dict[str, PlotType]) -> dp.Page:
        """Create the infrastructure page with all the infrastructure metrics. Also
        includes the node and link metrics.

        Returns:
            dp.Page: The infrastructure page.
        """

        has_nm = self.node_df is not None
        has_lm = self.link_df is not None

        infr_metrics = list(self.infr_df["callback_id"].unique())
        node_metrics = list(self.node_df["callback_id"].unique()) if has_nm else []
        link_metrics = list(self.link_df["callback_id"].unique()) if has_lm else []

        infr_blocks = []

        for metric in _aggregation_dict(*infr_metrics, *node_metrics, *link_metrics):
            df_infr = self.infr_df[self.infr_df["callback_id"].str.contains(metric)]
            df_nds = (
                self.node_df[self.node_df["callback_id"].str.contains(metric)]
                if has_nm
                else None
            )
            df_lnk = (
                self.link_df[self.link_df["callback_id"].str.contains(metric)]
                if has_lm
                else None
            )

            fig_inf, fig_by = None, None
            by = "node"

            if any(metric in m for m in infr_metrics):
                fig_inf = _line(metric, df=df_infr, x=DEFAULT_TICK_COLUMN, y="value")
            if metric in node_metrics:
                fig_by = self._plot_by_type(
                    metric, plot_types, df=df_nds, x="node_id", y="value"
                )
            if metric in link_metrics:
                by = "link"
                x = df_lnk["source"] + " -- " + df_lnk["target"]
                fig_by = self._plot_by_type(
                    metric,
                    plot_types,
                    df=df_lnk,
                    x=x,
                    y="value",
                )

            if fig_by:
                if fig_inf:
                    infr_blocks.append(_aggregated_group(fig_inf, fig_by, by, metric))
                else:
                    infr_blocks.append(fig_by)
            else:
                infr_blocks.insert(0, fig_inf)

        blocks = [
            dp.Text(f"## {INFRASTRUCTURE_PAGE_TITLE} Metrics"),
            dp.Group(
                _big_number(
                    "Nodes", self.node_df["node_id"].unique().size if has_nm else "N/A"
                ),
                _big_number(
                    "Links",
                    (
                        self.link_df.groupby(["source", "target"]).ngroups
                        if has_lm
                        else "N/A"
                    ),
                ),
                _big_number("Infrastructure Metrics", len(infr_metrics)),
                _big_number("Node Metrics", len(node_metrics)),
                _big_number("Link Metrics", len(link_metrics)),
                columns=5,
            ),
            _select(infr_blocks),
        ]

        return dp.Page(title="Infrastructure", blocks=blocks)

    def gml_page(self) -> dp.Page:
        """Create the network page with the network graph.

        Returns:
            dp.Page: The network page.
        """
        gml_blocks = []
        for gml in self._gml_path.glob("*.gml"):
            gml_blocks.append(_gml(gml))

        blocks = [
            dp.Text("## Networks"),
            _select(gml_blocks),
        ]
        return dp.Page(title="Networks", blocks=blocks)

    def _plot_by_type(self, metric: str, plot_types: Dict[str, PlotType], **kwargs):
        """Plot the metric by the specified type. If no type is specified, use the
        default type.

        Args:
            metric (str): The metric to plot.
            default_type (PlotType, optional): The default plot type. Defaults to "bar".

        Returns:
            dp.Plot: The plot of the metric.
        """
        plot_type = plot_types.get(metric, "bar")
        kwargs["metric"] = metric

        if plot_type == "line":
            kwargs["x"] = DEFAULT_TICK_COLUMN
            return _line(**kwargs)
        if plot_type == "scatter":
            return _scatter(**kwargs)
        if plot_type == "bar":
            return _bar(**kwargs)
        raise ValueError(f"Plot type {plot_type} not supported.")

    def read_csv(self, report_type: str) -> Optional[pd.DataFrame]:
        """Read the CSV file at the specified path.

        Args:
            path (str): The path to the CSV file.

        Returns:
            pd.DataFrame: The DataFrame of the CSV file.
        """
        try:
            df = pd.read_csv(
                self._stats_path / f"{report_type}.csv", converters={"value": to_float}
            )
            if report_type != "simulation":
                df = df[
                    df["n_event"].isin(
                        list(range(self.range[0], self.range[1] + 1, self.step))
                    )
                ]
            return df
        except FileNotFoundError:
            self.logger.warning(f"File not found: {report_type}")
            return None
        except pd.errors.ParserError:
            self.logger.error(f"Error parsing file: {report_type}")
            return None

    @property
    def logger(self) -> Logger:
        """Get the logger of the Report, binding the id to "Report".

        Returns:
            Logger: The logger of the Report.
        """
        return logger.bind(id="Report")


def _big_number(heading: str, value: Union[float, AnyStr]) -> dp.BigNumber:
    """Create a BigNumber block with the specified heading and value.

    Args:
        heading (str): The heading of the BigNumber.
        value (Union[float, AnyStr]): The value of the BigNumber.

    Returns:
        dp.BigNumber: The BigNumber block.
    """
    return dp.BigNumber(
        heading=snake_to_title(heading),
        value=format_float(value) if isinstance(value, float) else value,
        prev_value=0,
    )


def _aggregated_group(
    fig_agg: dp.Plot, fig_by: dp.Plot, by: str, metric: str
) -> dp.Group:
    """Create a Group block with two plots:
    - the aggregated metric plot (application/infrastructure)
    - the metric plot (service/interaction/node/link)

    Args:
        fig_agg (dp.Plot): The aggregated metric plot.
        fig_by (dp.Plot): The metric plot.
        by (str): The type of the metric.
        metric (str): The metric name.

    Returns:
        dp.Group: The Group block.
    """
    return dp.Group(
        dp.Group("#### Overall", fig_agg),
        dp.Group(f"#### By {by}", fig_by),
        columns=2,
        widths=AGGREGATED_METRIC_WIDTHS,
        label=snake_to_title(metric),
    )


def _bar(
    metric: str,
    df: pd.DataFrame,
    x: str,
    y: str,
    animation_frame: str = DEFAULT_TICK_COLUMN,
) -> dp.Plot:
    """Create a bar plot of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to plot.
        x (str): The x-axis column.
        y (str): The y-axis column.
        animation_frame (str, optional): The animation frame column. Defaults to DEFAULT_TICK_COLUMN.

    Returns:
        dp.Plot: The bar plot.
    """
    fig = px.bar(df, x=x, y=y, animation_frame=animation_frame)
    fig.update_layout(PLOT_LAYOUT_CONFIG, xaxis_title=None)
    return dp.Plot(fig, label=snake_to_title(metric))


def _line(metric: str, df: pd.DataFrame, x: str, y: str) -> dp.Plot:
    """Create a line plot of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to plot.
        x (str): The x-axis column.
        y (str): The y-axis column.

    Returns:
        dp.Plot: The line plot.
    """
    fig = px.line(df, x=x, y=y, markers=True)
    fig.update_layout(PLOT_LAYOUT_CONFIG)
    fig.update_layout(xaxis_title="Tick")
    return dp.Plot(fig, label=snake_to_title(metric))


def _scatter(metric: str, df: pd.DataFrame, x: str, y: str) -> dp.Plot:
    """Create a scatter plot of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to plot.
        x (str): The x-axis column.
        y (str): The y-axis column.

    Returns:
        dp.Plot: The scatter plot.
    """
    fig = px.scatter(df, x=x, y=y)
    fig.update_layout(PLOT_LAYOUT_CONFIG)
    return dp.Plot(fig, label=snake_to_title(metric))


def _select(blocks: List[dp.Block]) -> dp.Block:
    """Create a Select block with the specified blocks. If there is only one block,
    return the block.

    Args:
        blocks (List[dp.Block]): The blocks to select from.

    Returns:
        dp.Block: The Select block or the single block.
    """
    if len(blocks) > 1:
        return dp.Select(blocks=blocks)
    b = blocks[0]
    return dp.Group(f"#### {b._attributes['label']}", b)


def _extract_fn_and_aggregation(aggregated_metric: str) -> Tuple[str, Optional[str]]:
    last_underscore_index = aggregated_metric.rfind("_")
    if last_underscore_index != -1:
        metric = aggregated_metric[:last_underscore_index]
        aggr_fn = aggregated_metric[last_underscore_index + 1 :]
        if aggr_fn in ["sum", "mean", "max", "min", "aggregated"]:
            return metric, aggr_fn

    return aggregated_metric, None


def _aggregation_dict(*args: str) -> Dict[str, Optional[str]]:
    d = {}
    for arg in args:
        metric, aggr_fn = _extract_fn_and_aggregation(arg)
        if metric not in d:
            d[metric] = aggr_fn

    return d


def _gml(path: Path) -> dp.HTML:
    g = nx.read_gml(path)
    nt = Network(height="1000px", width="100%")
    nt.from_nx(g, show_edge_weights=True)
    for n in nt.nodes:

        n["title"] = "\n".join(
            [
                f"{k}: {(format_float(v) if isinstance(v, float) else v)}"
                for k, v in g.nodes[n["id"]].items()
                if k != "size"
            ]
        )
    # nt.force_atlas_2based()
    nt.toggle_physics(False)
    nt.set_options(
        """
        {
            "interaction": {
                "zoomSpeed": 0.2
            }
        }
        """
    )
    label = path.stem.split("-")[-1]
    legend = dp.HTML(
        "\n".join(
            [
                _legend_button(group, color, border)
                for group, (color, border) in LEGEND_COLORS.items()
            ]
        )
    )
    return dp.Group(legend, dp.HTML(nt.generate_html()), label=label)


def _legend_button(label: NodeGroup, color: str, border: str) -> str:
    btn = f"<button style='background-color: {color}; color: black; font-size: 15px;"
    btn += f" border-radius: 10px; border: 2px solid {border}; padding: 10px 20px;"
    btn += f" margin-right: 5px;' disabled>{label}</button>"
    return btn


def _to_csv(df: pd.DataFrame, path: str):
    if df is not None:
        df.to_csv(path, index=False)


def _to_json(df: pd.DataFrame, path: str):
    if df is not None:
        df.reset_index().to_json(path, orient="records", indent=4)


def _get_html_formatting() -> dp.Formatting:
    """Get the formatting configuration for HTML reports.

    Returns:
        dp.Formatting: The formatting configuration.
    """
    return dp.Formatting(
        width=REPORT_WIDTH,
        accent_color=REPORT_ACCENT_COLOR,
        text_alignment=REPORT_TEXT_ALIGNMENT,
    )
