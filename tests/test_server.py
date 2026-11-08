"""Tool-level tests through an in-memory MCP client (no network, no Commander)."""

from __future__ import annotations

import asyncio
import json
import shlex

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from keeper_mcp import commander
from keeper_mcp.server import mcp

READ_ONLY_TOOLS = {
    "keeper_search_records",
    "keeper_get_record",
    "keeper_list_folders",
    "keeper_enterprise_info",
    "keeper_list_users",
    "keeper_list_teams",
    "keeper_security_audit",
    "keeper_audit_report",
    "keeper_msp_info",
    "keeper_list_managed_companies",
    "keeper_list_roles",
    "keeper_list_nodes",
    "keeper_get_user",
    "keeper_enterprise_role_info",
    "keeper_list_shared_folders",
    "keeper_compliance_report",
    "keeper_breachwatch_report",
}
DESTRUCTIVE_TOOLS = {"keeper_transfer_user", "keeper_run_command"}


def call(name: str, args: dict | None = None) -> str:
    async def run() -> str:
        async with Client(mcp) as client:
            result = await client.call_tool(name, args or {})
            return result.content[0].text

    return asyncio.run(run())


def list_tools():
    async def run():
        async with Client(mcp) as client:
            return await client.list_tools()

    return asyncio.run(run())


def test_tool_annotations_match_risk():
    tools = {tool.name: tool for tool in list_tools()}
    for name in READ_ONLY_TOOLS:
        assert tools[name].annotations.readOnlyHint is True, name
    for name in DESTRUCTIVE_TOOLS:
        assert tools[name].annotations.destructiveHint is True, name
    for name in set(tools) - READ_ONLY_TOOLS:
        assert not tools[name].annotations.readOnlyHint, f"{name} writes but claims read-only"


def test_transfer_user_requires_confirm(fake_commander):
    with pytest.raises(ToolError, match="irreversible"):
        call("keeper_transfer_user", {"email": "a@example.com", "target_user": "b@example.com"})
    assert fake_commander.calls == []


def test_transfer_user_with_confirm_runs_forced(fake_commander):
    fake_commander.stdout = "transferred"
    out = call(
        "keeper_transfer_user",
        {"email": "a@example.com", "target_user": "b@example.com", "confirm": True},
    )
    assert out == "transferred"
    assert fake_commander.last_argv[-1] == (
        "transfer-user a@example.com --target-user b@example.com --force"
    )


@pytest.mark.parametrize(
    "command",
    ["shell", "login user@example.com", "LOGOUT", "keeper logout", "  connect host  "],
)
def test_run_command_refuses_interactive_and_logout(fake_commander, command):
    with pytest.raises(ToolError, match="Refusing to run"):
        call("keeper_run_command", {"command": command})
    assert fake_commander.calls == []


@pytest.mark.parametrize("command", ["", "'unterminated"])
def test_run_command_rejects_empty_or_unparseable(fake_commander, command):
    with pytest.raises(ToolError):
        call("keeper_run_command", {"command": command})
    assert fake_commander.calls == []


def test_run_command_strips_keeper_prefix(fake_commander):
    call("keeper_run_command", {"command": "keeper user-report --days 30"})
    assert fake_commander.last_argv[-1] == "user-report --days 30"


def test_get_record_redacts_by_default(fake_commander):
    record = {"uid": "abc", "fields": [{"type": "password", "value": ["hunter2"]}]}
    fake_commander.stdout = "Syncing...\n" + json.dumps(record) + "\n"
    out = call("keeper_get_record", {"uid": "abc"})
    assert "hunter2" not in out
    assert commander.REDACTED_PLACEHOLDER in out


def test_get_record_reveal_returns_plaintext(fake_commander):
    record = {"uid": "abc", "fields": [{"type": "password", "value": ["hunter2"]}]}
    fake_commander.stdout = json.dumps(record)
    out = call("keeper_get_record", {"uid": "abc", "reveal_secrets": True})
    assert "hunter2" in out


def test_search_records_always_redacts(fake_commander):
    fake_commander.stdout = json.dumps([{"uid": "abc", "password": "hunter2"}])
    out = call("keeper_search_records", {"query": "example"})
    assert "hunter2" not in out


def test_user_input_is_shell_quoted(fake_commander):
    hostile = "x --unmask; logout"
    call("keeper_search_records", {"query": hostile})
    command = fake_commander.last_argv[-1]
    assert shlex.split(command)[:2] == ["search", hostile]


def test_device_approve_needs_device_for_writes(fake_commander):
    with pytest.raises(ToolError, match="device is required"):
        call("keeper_device_approve", {"action": "approve"})
    assert fake_commander.calls == []


def test_mc_id_scopes_tool_to_managed_company(fake_commander):
    fake_commander.stdout = "[]"
    call("keeper_list_users", {"mc_id": 7})
    assert fake_commander.last_stdin == (
        "switch-to-mc 7\nenterprise-info --users --format json\nswitch-to-msp\n"
    )


def test_commander_errors_surface_as_tool_errors(fake_commander):
    fake_commander.returncode = 4
    with pytest.raises(ToolError, match="exit 4: not found"):
        call("keeper_get_user", {"email": "missing@example.com"})


@pytest.mark.parametrize(
    ("tool", "args"),
    [
        ("keeper_run_command", {"command": "tree\nlogout", "mc_id": 1}),
        ("keeper_lock_user", {"email": "a@example.com\nlogout", "mc_id": 1}),
        ("keeper_search_records", {"query": "x\rlogout"}),
    ],
)
def test_tools_reject_multiline_input(fake_commander, tool, args):
    with pytest.raises(ToolError, match="line breaks"):
        call(tool, args)
    assert fake_commander.calls == []
