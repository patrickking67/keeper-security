"""Unit tests for the Commander subprocess wrapper."""

from __future__ import annotations

import subprocess

import pytest

from keeper_mcp import commander


def test_missing_config_raises_bootstrap_hint(monkeypatch, tmp_path, fake_commander):
    monkeypatch.setenv("KEEPER_CONFIG_FILE", str(tmp_path / "absent.json"))
    with pytest.raises(commander.CommanderError, match="persistent-login"):
        commander.run_command("tree")
    assert fake_commander.calls == []


def test_empty_command_rejected(fake_commander):
    with pytest.raises(commander.CommanderError, match="No Commander command"):
        commander.run_commands(["  "])
    assert fake_commander.calls == []


def test_single_command_uses_one_shot_form(_offline, fake_commander):
    fake_commander.stdout = "ok\n"
    assert commander.run_command("tree") == "ok\n"
    assert fake_commander.last_argv == ["keeper-fake", f"--config={_offline}", "tree"]
    call = fake_commander.calls[-1]
    assert call["stdin"] is subprocess.DEVNULL
    assert call["capture_output"] is True
    assert call["env"]["NO_COLOR"] == "1"


def test_mc_id_wraps_command_in_batch_chain(fake_commander):
    commander.run_command("enterprise-info --users", mc_id=42)
    assert fake_commander.last_argv[-2:] == ["--batch-mode", "-"]
    assert fake_commander.last_stdin == (
        "switch-to-mc 42\nenterprise-info --users\nswitch-to-msp\n"
    )


def test_mc_id_is_coerced_to_int(fake_commander):
    commander.run_command("tree", mc_id=True)  # bool is an int subclass
    assert fake_commander.last_stdin.startswith("switch-to-mc 1\n")


def test_nonzero_exit_reports_meaning_and_auth_hint(fake_commander):
    fake_commander.returncode = 2
    fake_commander.stderr = "session expired"
    with pytest.raises(commander.CommanderError) as info:
        commander.run_command("tree")
    message = str(info.value)
    assert "exit 2: authentication error" in message
    assert "session expired" in message
    assert "persistent-login" in message


def test_long_output_is_truncated_in_errors(fake_commander):
    fake_commander.returncode = 1
    fake_commander.stdout = "x" * 5000
    with pytest.raises(commander.CommanderError, match=r"truncated, 5000 chars total"):
        commander.run_command("tree")


def test_binary_not_found(monkeypatch):
    def missing(*args, **kwargs):
        raise FileNotFoundError("keeper-fake")

    monkeypatch.setattr(commander.subprocess, "run", missing)
    with pytest.raises(commander.CommanderError, match="was not found"):
        commander.run_command("tree")


def test_timeout(monkeypatch):
    def slow(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"])

    monkeypatch.setenv("KEEPER_COMMAND_TIMEOUT", "5")
    monkeypatch.setattr(commander.subprocess, "run", slow)
    with pytest.raises(commander.CommanderError, match="timed out after 5s"):
        commander.run_command("tree")


@pytest.mark.parametrize("raw", ["abc", "0", "-3"])
def test_invalid_timeout_rejected(monkeypatch, raw):
    monkeypatch.setenv("KEEPER_COMMAND_TIMEOUT", raw)
    with pytest.raises(commander.CommanderError, match="KEEPER_COMMAND_TIMEOUT"):
        commander.command_timeout()


def test_default_timeout():
    assert commander.command_timeout() == commander.DEFAULT_TIMEOUT_SECONDS


def test_extract_json_skips_status_noise():
    text = 'Logging in...\nDecrypted [23] record(s)\n[{"uid": "abc", "title": "Example"}]\nDone\n'
    assert commander.extract_json(text) == [{"uid": "abc", "title": "Example"}]


def test_extract_json_prefers_line_anchored_payload():
    text = 'note {"inline": 1}\n{"payload": {"a": 1, "b": 2}}\n'
    assert commander.extract_json(text) == {"payload": {"a": 1, "b": 2}}


def test_extract_json_returns_none_for_tables():
    assert commander.extract_json("Name   Value\n----   -----\nfoo    bar\n") is None


def test_scrub_secrets_masks_sensitive_fields():
    record = {
        "title": "Example",
        "fields": [
            {"type": "login", "value": ["user@example.com"]},
            {"type": "password", "value": ["hunter2"]},
            {"type": "oneTimeCode", "value": ["otpauth://totp/x"]},
            {"type": "pinCode", "value": []},
        ],
        "custom": [{"type": "secret", "label": "api", "value": ["s3cr3t"]}],
        "password": "legacy-pass",
        "Private-Key": "-----BEGIN-----",
    }
    scrubbed = commander.scrub_secrets(record)
    placeholder = commander.REDACTED_PLACEHOLDER
    assert scrubbed["fields"][0]["value"] == ["user@example.com"]
    assert scrubbed["fields"][1]["value"] == placeholder
    assert scrubbed["fields"][2]["value"] == placeholder
    assert scrubbed["fields"][3]["value"] == []  # empty values stay empty
    assert scrubbed["custom"][0]["value"] == placeholder
    assert scrubbed["custom"][0]["label"] == "api"
    assert scrubbed["password"] == placeholder
    assert scrubbed["Private-Key"] == placeholder
    assert "hunter2" not in repr(scrubbed)
    # The input is not mutated.
    assert record["fields"][1]["value"] == ["hunter2"]


@pytest.mark.parametrize("separator", ["\n", "\r", "\r\n", "\x00", " "])
def test_line_breaks_cannot_smuggle_batch_commands(fake_commander, separator):
    with pytest.raises(commander.CommanderError, match="line breaks"):
        commander.run_command(f"tree{separator}logout", mc_id=1)
    with pytest.raises(commander.CommanderError, match="line breaks"):
        commander.run_command(f"tree{separator}logout")
    assert fake_commander.calls == []
