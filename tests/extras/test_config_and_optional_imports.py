from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from eclypse.simulation.config import (
    SimulationConfig,
    _require_module,
)
from eclypse.utils.defaults import (
    PARQUET_REPORT_DIR,
    TENSORBOARD_REPORT_DIR,
)
from eclypse.workflow.event import (
    EclypseEvent,
    EventRole,
)


def _require_installed(module_name: str):
    if importlib.util.find_spec(module_name) is None:
        pytest.skip(f"Optional dependency {module_name!r} is not installed.")


class ExtraMetricEvent(EclypseEvent):
    def __init__(self, name: str, report: str):
        super().__init__(
            name=name,
            event_type="simulation",
            role=EventRole.METRIC,
            report=report,
        )

    def __call__(self, *_args, **_kwargs):
        return {"value": 1}


@pytest.mark.extras
def test_config_import_targets_are_available_for_installed_extras():
    _require_installed("pandas")
    _require_installed("polars")
    _require_installed("ray")
    _require_installed("tensorboardX")

    _require_module("pandas")
    _require_module("polars")
    _require_module("ray", extras_name="remote")
    _require_module("tensorboardX", extras_name="tboard")


@pytest.mark.extras
def test_simulation_config_accepts_optional_backend_extras(tmp_path: Path):
    _require_installed("pandas")
    _require_installed("polars")

    pandas_config = SimulationConfig(
        path=tmp_path / "pandas-config",
        report_backend="pandas",
    )
    polars_config = SimulationConfig(
        path=tmp_path / "polars-config",
        report_backend="polars",
    )
    lazy_config = SimulationConfig(
        path=tmp_path / "polars-lazy-config",
        report_backend="polars_lazy",
    )

    assert pandas_config.report_backend == "pandas"
    assert polars_config.report_backend == "polars"
    assert lazy_config.report_backend == "polars_lazy"


@pytest.mark.extras
def test_simulation_config_resolves_optional_reporters_and_remote(tmp_path: Path):
    _require_installed("ray")
    _require_installed("polars")
    _require_installed("tensorboardX")

    config = SimulationConfig(
        path=tmp_path / "extra-reporters",
        report_backend="pandas",
        remote=True,
        events=[
            ExtraMetricEvent("tensorboard_metric", TENSORBOARD_REPORT_DIR),
            ExtraMetricEvent("parquet_metric", PARQUET_REPORT_DIR),
        ],
    )

    assert config.remote is not None
    assert config.reporters is not None
    assert TENSORBOARD_REPORT_DIR in config.reporters
    assert PARQUET_REPORT_DIR in config.reporters
