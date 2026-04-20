from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

_RAY_PROBE_STATE: dict[str, str | None] = {"blocked_reason": None}


def run_remote_probe(
    repo_root: Path,
    script: str,
    timeout: int = 25,
) -> dict[str, Any]:
    blocked_reason = _RAY_PROBE_STATE["blocked_reason"]

    if blocked_reason is not None:
        pytest.skip(blocked_reason)

    env = os.environ.copy()
    env["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
    env["PYTHONPATH"] = str(repo_root)

    try:
        completed = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            check=False,
            cwd=repo_root,
            env=env,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        _RAY_PROBE_STATE["blocked_reason"] = f"Ray integration probe timed out: {exc}"
        pytest.skip(_RAY_PROBE_STATE["blocked_reason"])

    if completed.returncode != 0:
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        blocked_markers = (
            "PermissionError",
            "Operation not permitted",
            "Timed out waiting for file",
            "gcs_server_port_",
        )
        if any(marker in combined_output for marker in blocked_markers):
            _RAY_PROBE_STATE["blocked_reason"] = (
                f"Ray integration probe is not permitted here:\n{combined_output}"
            )
            pytest.skip(_RAY_PROBE_STATE["blocked_reason"])
        pytest.fail(
            "Ray integration probe failed.\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert lines, "Expected JSON output from the Ray integration probe."

    for line in reversed(lines):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    pytest.fail(
        "Ray integration probe did not emit a JSON object.\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
