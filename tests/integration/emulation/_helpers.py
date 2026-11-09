from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def _extract_json_object(output: str) -> dict[str, Any] | None:
    """Extract the most recent JSON object from potentially noisy probe output."""
    cleaned = _ANSI_ESCAPE_RE.sub("", output)
    decoder = json.JSONDecoder()

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    for line in reversed(lines):
        candidates = [line]
        if "{" in line:
            candidates.append(line[line.find("{") :])
        for candidate in candidates:
            try:
                payload, _ = decoder.raw_decode(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                return payload

    for index in range(len(cleaned) - 1, -1, -1):
        if cleaned[index] != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    return None


def run_remote_probe(
    repo_root: Path,
    script: str,
    timeout: int = 25,
    *,
    address: str,
) -> dict[str, Any]:
    env = os.environ.copy()
    env["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
    env["PYTHONPATH"] = str(repo_root)
    env["ECLYPSE_TEST_RAY_ADDRESS"] = address
    env["ECLYPSE_TEST_RAY_NAMESPACE"] = uuid4().hex

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
        pytest.fail(f"Ray integration probe timed out: {exc}")

    if completed.returncode != 0:
        pytest.fail(
            "Ray integration probe failed.\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    payload = _extract_json_object(completed.stdout)
    if payload is None:
        payload = _extract_json_object(completed.stderr)
    if payload is not None:
        return payload

    pytest.fail(
        "Ray integration probe did not emit a JSON object.\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
