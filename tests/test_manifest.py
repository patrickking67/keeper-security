"""Keep manifest.json, pyproject.toml and the server in agreement."""

from __future__ import annotations

import asyncio
import json
import tomllib
from pathlib import Path

from fastmcp import Client

from keeper_mcp import __version__
from keeper_mcp.server import mcp

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def server_tool_names() -> set[str]:
    async def run():
        async with Client(mcp) as client:
            return {tool.name for tool in await client.list_tools()}

    return asyncio.run(run())


def test_versions_agree():
    assert MANIFEST["version"] == PYPROJECT["project"]["version"] == __version__


def test_manifest_lists_exactly_the_server_tools():
    listed = [tool["name"] for tool in MANIFEST["tools"]]
    assert len(listed) == len(set(listed)), "duplicate tool in manifest.json"
    assert set(listed) == server_tool_names()


def test_manifest_entry_point_and_assets_exist():
    assert (ROOT / MANIFEST["server"]["entry_point"]).is_file()
    assert (ROOT / MANIFEST["icon"]).is_file()
    for icon in MANIFEST.get("icons", []):
        assert (ROOT / icon["src"]).is_file()


def test_manifest_env_only_references_declared_user_config():
    declared = set(MANIFEST.get("user_config", {}))
    for value in MANIFEST["server"]["mcp_config"].get("env", {}).values():
        if value.startswith("${user_config."):
            assert value[len("${user_config.") : -1] in declared
