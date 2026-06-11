"""Thin non-interactive subprocess wrapper around the Keeper Commander CLI."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = "~/.keeper/config.json"
DEFAULT_TIMEOUT_SECONDS = 120.0

REDACTED_PLACEHOLDER = (
    "***REDACTED*** (call keeper_get_record with reveal_secrets=true to retrieve this value)"
)

_TRUNCATE_AT = 2000

_EXIT_CODE_MEANINGS = {
    1: "general error",
    2: "authentication error",
    3: "syntax error",
    4: "not found",
}

# Keeper record field types whose values must never reach the client unmasked.
_SENSITIVE_FIELD_TYPES = {
    "password",
    "secret",
    "pincode",
    "onetimecode",
    "onetimepassword",
    "otp",
    "keypair",
    "hiddenfield",
    "note",
    "securednote",
    "passkey",
}

# Dict keys that hold secret material directly (legacy records, key material).
_SENSITIVE_KEYS = {
    "password",
    "passphrase",
    "pin",
    "secret",
    "private_key",
    "privatekey",
}

# Serialize Commander invocations: Commander rewrites the config file with
# rotated session tokens, so concurrent processes would race on it.
_lock = threading.Lock()


class CommanderError(RuntimeError):
    """Raised when a Keeper Commander invocation cannot run or exits non-zero."""


def config_path() -> Path:
    raw = os.environ.get("KEEPER_CONFIG_FILE", "").strip() or DEFAULT_CONFIG_PATH
    return Path(raw).expanduser()


def commander_bin() -> str:
    explicit = os.environ.get("KEEPER_COMMANDER_BIN", "").strip()
    if explicit:
        return explicit
    # keepercommander is a dependency of this project, so the venv that runs
    # the server usually carries the `keeper` script next to its python.
    bundled = Path(sys.executable).with_name("keeper")
    if bundled.is_file():
        return str(bundled)
    return "keeper"


def command_timeout() -> float:
    raw = os.environ.get("KEEPER_COMMAND_TIMEOUT", "").strip()
    if not raw:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError as exc:
        raise CommanderError(
            f"KEEPER_COMMAND_TIMEOUT must be a number of seconds, got {raw!r}."
        ) from exc
    if value <= 0:
        raise CommanderError("KEEPER_COMMAND_TIMEOUT must be greater than zero.")
    return value


def _truncate(text: str) -> str:
    text = text.strip()
    if len(text) <= _TRUNCATE_AT:
        return text
    return f"{text[:_TRUNCATE_AT]}... [truncated, {len(text)} chars total]"


def run_commands(commands: list[str]) -> str:
    """Run one or more Commander commands non-interactively; return captured stdout.

    A single command uses the documented one-shot form
    (``keeper --config=<file> "<command>"``); multiple commands are chained via
    ``--batch-mode -`` with the commands piped on stdin. The child never inherits
    this server's stdin or stdout, so the MCP protocol stream stays clean.
    """
    if not commands or not all(c.strip() for c in commands):
        raise CommanderError("No Commander command provided.")
    cfg = config_path()
    if not cfg.is_file():
        raise CommanderError(
            f"Keeper Commander config not found at {cfg}. This server needs a persistent-login "
            "config file. One-time bootstrap: run 'keeper shell --config-file', log in, then run "
            "'this-device register', 'this-device persistent-login on', "
            "'this-device ip-auto-approve on', 'this-device timeout 30d', and exit with 'quit' "
            "(never 'logout'). See README.md 'Authentication bootstrap'. "
            "Set KEEPER_CONFIG_FILE if the config lives elsewhere."
        )
    binary = commander_bin()
    timeout = command_timeout()
    pretty = " && ".join(commands)
    if len(commands) == 1:
        argv = [binary, f"--config={cfg}", commands[0]]
        stdin_text = None
    else:
        argv = [binary, f"--config={cfg}", "--batch-mode", "-"]
        stdin_text = "\n".join(commands) + "\n"
    env = {**os.environ, "NO_COLOR": "1"}
    with _lock:
        try:
            proc = subprocess.run(
                argv,
                input=stdin_text,
                stdin=subprocess.DEVNULL if stdin_text is None else None,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                env=env,
            )
        except FileNotFoundError as exc:
            raise CommanderError(
                f"Keeper Commander binary {binary!r} was not found. It is installed with this "
                "project's virtualenv (dependency 'keepercommander'); otherwise run "
                "'pip install keepercommander' or point KEEPER_COMMANDER_BIN at the executable."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise CommanderError(
                f"Commander command timed out after {timeout:.0f}s: {pretty}. "
                "Raise KEEPER_COMMAND_TIMEOUT if this command legitimately needs longer."
            ) from exc
    if proc.returncode != 0:
        meaning = _EXIT_CODE_MEANINGS.get(proc.returncode, "unknown")
        message = (
            f"Commander command failed (exit {proc.returncode}: {meaning}): {pretty}\n"
            f"stderr: {_truncate(proc.stderr) or '(empty)'}\n"
            f"stdout: {_truncate(proc.stdout) or '(empty)'}"
        )
        if proc.returncode == 2:
            message += (
                "\nThe persistent-login session has likely expired or been revoked. Re-run the "
                "authentication bootstrap in README.md ('keeper shell --config-file' -> login -> "
                "'this-device persistent-login on')."
            )
        raise CommanderError(message)
    return proc.stdout


def run_command(command: str, mc_id: int | None = None) -> str:
    """Run a single Commander command, optionally inside a managed-company context.

    With ``mc_id`` the command is wrapped in a batch chain:
    ``switch-to-mc <id>`` -> command -> ``switch-to-msp``.
    """
    if mc_id is None:
        return run_commands([command])
    return run_commands([f"switch-to-mc {int(mc_id)}", command, "switch-to-msp"])


def extract_json(text: str) -> Any | None:
    """Find and parse the JSON object/array payload in Commander stdout.

    Commander prints login/sync status lines around ``--format json`` payloads,
    and some of that noise itself parses as JSON (e.g. ``Decrypted [23]
    record(s)``), so neither ``json.loads`` on the whole output nor "first
    parseable value" works. The payload always starts at the beginning of its
    own line, so prefer the longest object/array anchored at a line start and
    fall back to the longest match found anywhere.
    """
    decoder = json.JSONDecoder()

    def best_candidate(line_anchored: bool) -> Any | None:
        best_value: Any | None = None
        best_span = -1
        idx = 0
        while True:
            starts = [i for i in (text.find("{", idx), text.find("[", idx)) if i != -1]
            if not starts:
                return best_value
            idx = min(starts)
            if line_anchored and idx != 0 and text[idx - 1] != "\n":
                idx += 1
                continue
            try:
                value, end = decoder.raw_decode(text, idx)
            except ValueError:
                idx += 1
                continue
            if isinstance(value, (dict, list)):
                if end - idx > best_span:
                    best_value, best_span = value, end - idx
                idx = end  # nothing inside this value can be longer
            else:
                idx += 1

    for line_anchored in (True, False):
        found = best_candidate(line_anchored)
        if found is not None:
            return found
    return None


def scrub_secrets(value: Any) -> Any:
    """Recursively replace secret values in parsed record JSON with a placeholder.

    Masks the ``value`` of typed fields whose type is sensitive (password,
    secret, pinCode, oneTimeCode, keyPair, hidden/secured note, passkey) and
    any dict entry whose key itself names secret material.
    """
    if isinstance(value, dict):
        field_type = value.get("type")
        type_is_sensitive = (
            isinstance(field_type, str) and field_type.lower() in _SENSITIVE_FIELD_TYPES
        )
        scrubbed: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = key.lower().replace("-", "_")
            if key == "value" and type_is_sensitive and item not in (None, "", []):
                scrubbed[key] = REDACTED_PLACEHOLDER
            elif normalized_key in _SENSITIVE_KEYS and isinstance(item, str) and item:
                scrubbed[key] = REDACTED_PLACEHOLDER
            else:
                scrubbed[key] = scrub_secrets(item)
        return scrubbed
    if isinstance(value, list):
        return [scrub_secrets(item) for item in value]
    return value
