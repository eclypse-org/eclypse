from __future__ import annotations

import subprocess

import pytest

from tests.integration.emulation import _helpers


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_probe_uses_shared_address_and_a_fresh_namespace(monkeypatch, tmp_path, stream):
    environments = []

    def run(args, **kwargs):
        environments.append(kwargs["env"])
        assert kwargs["cwd"] == tmp_path
        assert kwargs["timeout"] == 25
        output = {"stdout": "", "stderr": ""}
        output[stream] = 'log line\n{"ok": true}\n'
        return subprocess.CompletedProcess(args, 0, **output)

    monkeypatch.setattr(_helpers.subprocess, "run", run)
    for _ in range(2):
        assert _helpers.run_remote_probe(tmp_path, "pass", address="shared:1234") == {
            "ok": True
        }
    assert all(env["ECLYPSE_TEST_RAY_ADDRESS"] == "shared:1234" for env in environments)
    assert len({env["ECLYPSE_TEST_RAY_NAMESPACE"] for env in environments}) == 2


@pytest.mark.parametrize("failure", ["timeout", "permission", "missing_json"])
def test_probe_failures_do_not_skip_later_probes(monkeypatch, tmp_path, failure):
    def run(args, **_kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired(args, 25)
        if failure == "permission":
            return subprocess.CompletedProcess(args, 1, "", "PermissionError")
        return subprocess.CompletedProcess(args, 0, "no result", "")

    monkeypatch.setattr(_helpers.subprocess, "run", run)
    with pytest.raises(pytest.fail.Exception):
        _helpers.run_remote_probe(tmp_path, "pass", address="shared:1234")

    monkeypatch.setattr(
        _helpers.subprocess,
        "run",
        lambda args, **_: subprocess.CompletedProcess(args, 0, '{"ok": true}', ""),
    )
    assert _helpers.run_remote_probe(tmp_path, "pass", address="shared:1234") == {
        "ok": True
    }
