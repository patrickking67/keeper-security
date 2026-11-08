"""Shared fixtures. Every test runs offline: Commander is never executed."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from keeper_mcp import commander


@dataclass
class FakeCommander:
    """Stands in for subprocess.run and records every Commander invocation."""

    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    calls: list[dict] = field(default_factory=list)

    def __call__(self, argv, **kwargs):
        self.calls.append({"argv": list(argv), **kwargs})
        return subprocess.CompletedProcess(argv, self.returncode, self.stdout, self.stderr)

    @property
    def last_argv(self) -> list[str]:
        assert self.calls, "Commander was not invoked"
        return self.calls[-1]["argv"]

    @property
    def last_stdin(self) -> str | None:
        assert self.calls, "Commander was not invoked"
        return self.calls[-1].get("input")


def _refuse_real_subprocess(*args, **kwargs):
    raise AssertionError("tests must not run a real Keeper Commander process")


@pytest.fixture(autouse=True)
def _offline(monkeypatch, tmp_path: Path):
    """Block real subprocesses and point the server at a throwaway config file."""
    monkeypatch.setattr(commander.subprocess, "run", _refuse_real_subprocess)
    cfg = tmp_path / "config.json"
    cfg.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("KEEPER_CONFIG_FILE", str(cfg))
    monkeypatch.setenv("KEEPER_COMMANDER_BIN", "keeper-fake")
    monkeypatch.delenv("KEEPER_COMMAND_TIMEOUT", raising=False)
    return cfg


@pytest.fixture
def fake_commander(monkeypatch) -> FakeCommander:
    fake = FakeCommander()
    monkeypatch.setattr(commander.subprocess, "run", fake)
    return fake
