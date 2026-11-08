"""The installed console script must speak MCP over stdio with no configuration."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

SCRIPT = Path(sys.executable).with_name("keeper-mcp")


@pytest.mark.skipif(not SCRIPT.is_file(), reason="keeper-mcp console script not installed")
def test_stdio_handshake_without_any_keeper_settings(tmp_path):
    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "check", "version": "0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    ]
    env = {k: v for k, v in os.environ.items() if not k.startswith("KEEPER_")}
    env["HOME"] = str(tmp_path)  # no ~/.keeper/config.json to find
    # Popen, not subprocess.run: the autouse fixture blocks subprocess.run so no test
    # can start Commander. This child is the MCP server itself, with no config.
    # stdin stays open until both replies arrive (the server exits on EOF); a timer
    # kills it if it hangs.
    responses: dict[int, dict] = {}
    with subprocess.Popen(
        [str(SCRIPT)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        env=env,
    ) as proc:
        watchdog = threading.Timer(60, proc.kill)
        watchdog.start()
        try:
            for message in messages:
                proc.stdin.write(json.dumps(message) + "\n")
            proc.stdin.flush()
            while len(responses) < 2:
                line = proc.stdout.readline()
                assert line, "server closed stdout before answering"
                payload = json.loads(line)  # a stray print would break MCP clients
                if "id" in payload:
                    responses[payload["id"]] = payload
        finally:
            watchdog.cancel()
            proc.stdin.close()
            proc.wait(timeout=30)

    assert responses[1]["result"]["serverInfo"]["name"] == "Keeper Security"
    names = {tool["name"] for tool in responses[2]["result"]["tools"]}
    assert "keeper_run_command" in names
    assert len(names) == 26
