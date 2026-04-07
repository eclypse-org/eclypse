from __future__ import annotations

import importlib.util
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    cast,
)

import pytest

from eclypse.remote.utils.ray_interface import RayInterface
from eclypse.report.reporters import (
    ParquetReporter,
    TensorBoardReporter,
)
from eclypse.utils.defaults import PARQUET_REPORT_DIR

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.workflow.event.event import EclypseEvent


def _require_installed(module_name: str):
    if importlib.util.find_spec(module_name) is None:
        pytest.skip(f"Optional dependency {module_name!r} is not installed.")


@pytest.mark.extras
@pytest.mark.asyncio
async def test_optional_reporters_initialise_with_real_dependencies(tmp_path: Path):
    _require_installed("polars")
    _require_installed("tensorboardX")

    parquet_reporter = ParquetReporter(tmp_path)
    await parquet_reporter.init()
    await parquet_reporter.write(
        "service",
        [
            {
                "timestamp": "2026-01-01T00:00:00",
                "event_id": "step",
                "n_event": 1,
                "callback_id": "latency",
                "application_id": "shop",
                "service_id": "gateway",
                "value": 2.5,
            }
        ],
    )

    tensorboard_reporter = TensorBoardReporter(tmp_path)
    await tensorboard_reporter.init()

    callback = cast(
        "EclypseEvent",
        SimpleNamespace(
            is_metric=True,
            data=(("shop", "gateway", 3.0),),
            type="service",
            name="latency",
        ),
    )
    rows = list(tensorboard_reporter.report("step", 1, callback))
    await tensorboard_reporter.write("service", rows)

    assert parquet_reporter.report_path == tmp_path / PARQUET_REPORT_DIR
    assert (tmp_path / PARQUET_REPORT_DIR / "service" / "part-000000.parquet").exists()
    assert tensorboard_reporter.writer is not None

    await parquet_reporter.close()
    await tensorboard_reporter.close()


@pytest.mark.extras
def test_ray_interface_smoke_round_trip():
    _require_installed("ray")

    interface = RayInterface()
    interface._backend = None
    backend = interface.backend

    try:
        backend.shutdown()
        backend.init(address="local", include_dashboard=False, ignore_reinit_error=True)
    except Exception as exc:  # pragma: no cover - environment-dependent skip path
        pytest.skip(f"Ray local runtime is not available here: {exc}")

    try:
        reference = interface.put({"value": 3})
        assert interface.get(reference) == {"value": 3}
    finally:
        backend.shutdown()
