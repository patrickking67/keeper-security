"""Keeper MCP server: FastMCP tools wrapping the Keeper Commander CLI."""

from __future__ import annotations

import json
import shlex
from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from keeper_mcp import commander
from keeper_mcp import __version__

mcp = FastMCP(
    name="Keeper Security",
    version=__version__,
    instructions=(
        "Tools for the Keeper Security vault and MSP/enterprise admin console, backed by the "
        "Keeper Commander CLI in non-interactive mode. Requires a persistent-login config file "
        "(see the repo README for the one-time bootstrap). Tools that accept mc_id run inside "
        "that managed company (switch-to-mc / switch-to-msp); get mc_id values from "
        "keeper_msp_info. Secret field values are redacted unless explicitly revealed."
    ),
)

_NO_OUTPUT = "(command completed with no output)"

McId = Annotated[
    int | None,
    Field(
        description=(
            "Optional managed-company ID (the ID column from keeper_msp_info). When set, the "
            "command runs inside that managed company via switch-to-mc/switch-to-msp. "
            "Requires MSP admin privileges."
        )
    ),
]


def _run_text(command: str, mc_id: int | None = None) -> str:
    try:
        output = commander.run_command(command, mc_id=mc_id)
    except commander.CommanderError as exc:
        raise ToolError(str(exc)) from exc
    return output.strip() or _NO_OUTPUT


def _run_json(command: str, mc_id: int | None = None, scrub: bool = False) -> str:
    """Run a command requested with --format json; pretty-print the JSON payload.

    Falls back to raw text when the Commander version prints a table instead.
    """
    try:
        output = commander.run_command(command, mc_id=mc_id)
    except commander.CommanderError as exc:
        raise ToolError(str(exc)) from exc
    data = commander.extract_json(output)
    if data is None:
        return output.strip() or _NO_OUTPUT
    if scrub:
        data = commander.scrub_secrets(data)
    return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool(
    description=(
        "Search the Keeper vault for records matching a pattern (title, login, URL, notes; "
        "regular expressions supported). Returns record metadata as JSON: UID, title, type, "
        "and similar. Password/secret values are never included; pass a UID to "
        "keeper_get_record for full details."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_search_records(
    query: Annotated[
        str,
        Field(description="Search pattern matched against record titles, logins, URLs and notes."),
    ],
) -> str:
    return _run_json(f"search {shlex.quote(query)} --format json", scrub=True)


@mcp.tool(
    description=(
        "Fetch a single vault record by UID as JSON. By default every secret field "
        "(password, TOTP/one-time code, pin, key pair, hidden/secured note, passkey) is "
        "masked. WARNING: reveal_secrets=true returns the live plaintext credentials into "
        "the conversation - set it only when the user explicitly asked for the secret value."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_get_record(
    uid: Annotated[
        str,
        Field(description="Record UID, e.g. from keeper_search_records."),
    ],
    reveal_secrets: Annotated[
        bool,
        Field(
            description=(
                "If true, include plaintext password/secret field values (live credentials) "
                "instead of masking them. Use only on explicit user request."
            )
        ),
    ] = False,
) -> str:
    return _run_json(f"get {shlex.quote(uid)} --format json", scrub=not reveal_secrets)


@mcp.tool(
    description=(
        "List the vault folder tree ('tree') and shared folders with their default "
        "permissions ('list-sf'). Returns Commander's table/text output; these commands "
        "have no JSON mode."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_list_folders() -> str:
    try:
        output = commander.run_commands(["tree", "list-sf"])
    except commander.CommanderError as exc:
        raise ToolError(str(exc)) from exc
    return output.strip() or _NO_OUTPUT


@mcp.tool(
    description=(
        "Enterprise overview via 'enterprise-info': node structure, seat/license usage and "
        "general tenant info. For an MSP account this shows the MSP tenant itself unless "
        "mc_id selects a managed company. Use keeper_list_users / keeper_list_teams for "
        "user- and team-level listings."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_enterprise_info(
    verbose: Annotated[
        bool,
        Field(description="Include verbose detail (-v)."),
    ] = False,
    mc_id: McId = None,
) -> str:
    command = "enterprise-info --format json"
    if verbose:
        command += " -v"
    return _run_json(command, mc_id=mc_id)


@mcp.tool(
    description=(
        "List enterprise users (email, name, status, node, 2FA, team/role membership) as "
        "JSON via 'enterprise-info --users --format json'."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_list_users(mc_id: McId = None) -> str:
    return _run_json("enterprise-info --users --format json", mc_id=mc_id)


@mcp.tool(
    description=(
        "Lock an enterprise user's account so they cannot sign in or access their vault. "
        "Reversible with keeper_unlock_user. Requires admin rights over the user's node."
    ),
    annotations={"destructiveHint": False, "idempotentHint": True},
)
def keeper_lock_user(
    email: Annotated[
        str,
        Field(description="Email address (or user ID) of the enterprise user to lock."),
    ],
    mc_id: McId = None,
) -> str:
    return _run_text(f"enterprise-user {shlex.quote(email)} --lock", mc_id=mc_id)


@mcp.tool(
    description="Unlock a previously locked enterprise user account, restoring vault access.",
    annotations={"destructiveHint": False, "idempotentHint": True},
)
def keeper_unlock_user(
    email: Annotated[
        str,
        Field(description="Email address (or user ID) of the enterprise user to unlock."),
    ],
    mc_id: McId = None,
) -> str:
    return _run_text(f"enterprise-user {shlex.quote(email)} --unlock", mc_id=mc_id)


@mcp.tool(
    description=(
        "List enterprise teams (name, UID, node, edit/share/view restrictions, membership) "
        "as JSON via 'enterprise-info --teams --format json'."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_list_teams(mc_id: McId = None) -> str:
    return _run_json("enterprise-info --teams --format json", mc_id=mc_id)


@mcp.tool(
    description=(
        "Password-health summary per user via 'security-audit-report': counts of "
        "weak/medium/strong/reused/unique passwords, overall security score and 2FA "
        "channel. Returns JSON."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_security_audit(
    node: Annotated[
        str | None,
        Field(description="Optional node name or ID to limit the report to that subtree."),
    ] = None,
    mc_id: McId = None,
) -> str:
    command = "security-audit-report --format json"
    if node:
        command += f" --node {shlex.quote(node)}"
    return _run_json(command, mc_id=mc_id)


@mcp.tool(
    description=(
        "Query enterprise audit/event logs via 'audit-report' (requires the ARAM add-on). "
        "report_type 'raw' returns individual events; span/hour/day/week/month aggregate "
        "occurrences over time. Filter by created window, event type, username or record "
        "UID to keep output small."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_audit_report(
    report_type: Annotated[
        Literal["raw", "span", "hour", "day", "week", "month"],
        Field(description="raw = individual events; the others aggregate event occurrences."),
    ] = "raw",
    created: Annotated[
        str | None,
        Field(
            description=(
                "Event-time filter: today, yesterday, last_7_days, last_30_days, "
                "month_to_date, last_month, year_to_date, last_year, or "
                "'between 2026-01-01 and 2026-02-01'. null disables the filter."
            )
        ),
    ] = "last_30_days",
    limit: Annotated[
        int,
        Field(description="Maximum rows to return; -1 returns everything (can be huge).", ge=-1),
    ] = 100,
    event_type: Annotated[
        str | None,
        Field(description="Optional event type filter, e.g. record_add, record_update, login."),
    ] = None,
    username: Annotated[
        str | None,
        Field(description="Only events initiated by this username/email."),
    ] = None,
    record_uid: Annotated[
        str | None,
        Field(description="Only events about this record UID."),
    ] = None,
    mc_id: McId = None,
) -> str:
    parts = [
        "audit-report",
        f"--report-type {report_type}",
        "--format json",
        f"--limit {int(limit)}",
    ]
    if created:
        parts.append(f"--created {shlex.quote(created)}")
    if event_type:
        parts.append(f"--event-type {shlex.quote(event_type)}")
    if username:
        parts.append(f"--username {shlex.quote(username)}")
    if record_uid:
        parts.append(f"--record-uid {shlex.quote(record_uid)}")
    return _run_json(" ".join(parts), mc_id=mc_id)


@mcp.tool(
    description=(
        "MSP overview via 'msp-info': license plans/allocations plus the managed-company "
        "table (#, ID, name, plan, allocated/active seats). Output is table text - "
        "msp-info has no JSON mode. Requires an MSP admin account."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_msp_info() -> str:
    return _run_text("msp-info")


@mcp.tool(
    description=(
        "List this MSP's managed companies (same 'msp-info' table: #, ID, name, plan, "
        "allocated/active seats). The ID column is the mc_id value accepted by other "
        "tools. Output is table text."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_list_managed_companies() -> str:
    return _run_text("msp-info")


@mcp.tool(
    description=(
        "Manage pending cloud-SSO device approval requests via 'device-approve'. "
        "action='list' (read-only) returns pending requests as JSON; 'approve' grants the "
        "device access to the user's vault; 'deny' rejects it. device is the user's email "
        "or a device ID and is required for approve/deny."
    ),
    annotations={"destructiveHint": False},
)
def keeper_device_approve(
    action: Annotated[
        Literal["list", "approve", "deny"],
        Field(description="list pending requests, or approve/deny a specific one."),
    ] = "list",
    device: Annotated[
        str | None,
        Field(description="User email or device ID to approve/deny. Required unless action='list'."),
    ] = None,
    mc_id: McId = None,
) -> str:
    if action == "list":
        return _run_json("device-approve --format json", mc_id=mc_id)
    if not device:
        raise ToolError("device is required when action is 'approve' or 'deny'.")
    flag = "--approve" if action == "approve" else "--deny"
    return _run_text(f"device-approve {shlex.quote(device)} {flag}", mc_id=mc_id)


@mcp.tool(
    description=(
        "List enterprise roles (name, node, cascade/visible scope and membership) as JSON "
        "via 'enterprise-info --roles'. Use keeper_enterprise_role_info for one role's "
        "enforcements and assignments."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_list_roles(mc_id: McId = None) -> str:
    return _run_json("enterprise-info --roles --format json", mc_id=mc_id)


@mcp.tool(
    description=(
        "List the enterprise node tree (organizational units: node names, IDs and parent "
        "structure) as JSON via 'enterprise-info --nodes'. Node names/IDs feed the node "
        "parameter on other tools."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_list_nodes(mc_id: McId = None) -> str:
    return _run_json("enterprise-info --nodes --format json", mc_id=mc_id)


@mcp.tool(
    description=(
        "Show one enterprise user's detail (status, node, team and role membership, email "
        "aliases, 2FA) via 'enterprise-user <email> -v'. Output is table text; "
        "enterprise-user has no JSON mode. Use keeper_list_users for the full JSON roster."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_get_user(
    email: Annotated[
        str,
        Field(description="Email address (or user ID) of the enterprise user to display."),
    ],
    mc_id: McId = None,
) -> str:
    return _run_text(f"enterprise-user {shlex.quote(email)} -v", mc_id=mc_id)


@mcp.tool(
    description=(
        "Show one enterprise role's detail (enforcement policies, assigned users and teams, "
        "managed nodes and admin privileges) via 'enterprise-role <role> -v'. Output is "
        "table text. Use keeper_list_roles for the full role list."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_enterprise_role_info(
    role: Annotated[
        str,
        Field(description="Role name (or role ID) to display, e.g. from keeper_list_roles."),
    ],
    mc_id: McId = None,
) -> str:
    return _run_text(f"enterprise-role {shlex.quote(role)} -v", mc_id=mc_id)


@mcp.tool(
    description=(
        "List all shared folders (name, UID and default manage/edit/share permissions) as "
        "JSON via 'list-sf'. For the full vault folder tree use keeper_list_folders."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_list_shared_folders() -> str:
    return _run_json("list-sf --format json")


@mcp.tool(
    description=(
        "Run the enterprise compliance report ('compliance report'): record access across "
        "users and teams with owner, shared-folder and permission detail. Requires the "
        "Compliance Reporting add-on. Returns JSON; secret values are never included. "
        "Filter by node/username/record to keep the report small (it can be large and slow)."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_compliance_report(
    node: Annotated[
        str | None,
        Field(description="Optional node name or ID to scope the report to that subtree."),
    ] = None,
    username: Annotated[
        str | None,
        Field(description="Optional user email to limit the report to that user's records."),
    ] = None,
    record: Annotated[
        str | None,
        Field(description="Optional record UID or title to limit the report to that record."),
    ] = None,
    mc_id: McId = None,
) -> str:
    parts = ["compliance report", "--format json"]
    if node:
        parts.append(f"--node {shlex.quote(node)}")
    if username:
        parts.append(f"--username {shlex.quote(username)}")
    if record:
        parts.append(f"--record {shlex.quote(record)}")
    return _run_json(" ".join(parts), mc_id=mc_id)


@mcp.tool(
    description=(
        "Run the BreachWatch report ('breachwatch report') across enterprise vaults: users "
        "with breached, weak or reused credentials from dark-web monitoring. Requires an "
        "admin account with BreachWatch enabled. Returns JSON; no password values are "
        "included."
    ),
    annotations={"readOnlyHint": True},
)
def keeper_breachwatch_report(mc_id: McId = None) -> str:
    return _run_json("breachwatch report --format json", mc_id=mc_id)


@mcp.tool(
    description=(
        "Invite a new enterprise user by email ('enterprise-user --add'): sends an "
        "invitation so the user sets their own master password. Optionally place them under "
        "a specific node. Creates and stores no password."
    ),
    annotations={"destructiveHint": False, "idempotentHint": False},
)
def keeper_create_user(
    email: Annotated[
        str,
        Field(description="Email address of the user to invite to the enterprise."),
    ],
    node: Annotated[
        str | None,
        Field(
            description="Optional node name or ID to place the user under; defaults to the root node."
        ),
    ] = None,
    mc_id: McId = None,
) -> str:
    command = f"enterprise-user --add {shlex.quote(email)}"
    if node:
        command += f" --node {shlex.quote(node)}"
    return _run_text(command, mc_id=mc_id)


@mcp.tool(
    description=(
        "Add an enterprise user to a team via 'enterprise-user <email> --add-team <team>', "
        "granting that team's shared-folder access. Reversible with "
        "keeper_remove_user_from_team."
    ),
    annotations={"destructiveHint": False, "idempotentHint": True},
)
def keeper_add_user_to_team(
    email: Annotated[
        str,
        Field(description="Email address (or user ID) of the enterprise user."),
    ],
    team: Annotated[
        str,
        Field(description="Team name or team UID to add the user to."),
    ],
    mc_id: McId = None,
) -> str:
    return _run_text(
        f"enterprise-user {shlex.quote(email)} --add-team {shlex.quote(team)}", mc_id=mc_id
    )


@mcp.tool(
    description=(
        "Remove an enterprise user from a team via 'enterprise-user <email> --remove-team "
        "<team>', revoking that team's shared-folder access for the user. Reversible with "
        "keeper_add_user_to_team."
    ),
    annotations={"destructiveHint": False, "idempotentHint": True},
)
def keeper_remove_user_from_team(
    email: Annotated[
        str,
        Field(description="Email address (or user ID) of the enterprise user."),
    ],
    team: Annotated[
        str,
        Field(description="Team name or team UID to remove the user from."),
    ],
    mc_id: McId = None,
) -> str:
    return _run_text(
        f"enterprise-user {shlex.quote(email)} --remove-team {shlex.quote(team)}", mc_id=mc_id
    )


@mcp.tool(
    description=(
        "Add an enterprise user to a role via 'enterprise-user <email> --add-role <role>', "
        "applying that role's enforcement policies and privileges to the user."
    ),
    annotations={"destructiveHint": False, "idempotentHint": True},
)
def keeper_add_user_to_role(
    email: Annotated[
        str,
        Field(description="Email address (or user ID) of the enterprise user."),
    ],
    role: Annotated[
        str,
        Field(description="Role name or role ID to add the user to."),
    ],
    mc_id: McId = None,
) -> str:
    return _run_text(
        f"enterprise-user {shlex.quote(email)} --add-role {shlex.quote(role)}", mc_id=mc_id
    )


@mcp.tool(
    description=(
        "Transfer a departing user's entire vault to another user via 'transfer-user "
        "--target-user' (offboarding/account takeover). IRREVERSIBLE: it moves all of the "
        "source user's records to the target; lock the source first with keeper_lock_user. "
        "Requires confirm=true and runs with --force because MCP is non-interactive."
    ),
    annotations={"destructiveHint": True, "idempotentHint": False},
)
def keeper_transfer_user(
    email: Annotated[
        str,
        Field(description="Source user email whose vault records will be transferred away."),
    ],
    target_user: Annotated[
        str,
        Field(description="Target user email that will receive the transferred records."),
    ],
    confirm: Annotated[
        bool,
        Field(
            description=(
                "Must be true to run this irreversible transfer. Guards against accidental "
                "account takeover; set only after the user explicitly approves."
            )
        ),
    ] = False,
    mc_id: McId = None,
) -> str:
    if not confirm:
        raise ToolError(
            "keeper_transfer_user is irreversible: it moves the source user's entire vault "
            "to the target. Re-call with confirm=true only after the user explicitly approves."
        )
    return _run_text(
        f"transfer-user {shlex.quote(email)} --target-user {shlex.quote(target_user)} --force",
        mc_id=mc_id,
    )


_REFUSED_COMMANDS = {
    "shell": "starts an interactive shell, which cannot run over MCP",
    "login": (
        "requires interactive device approval/MFA; use the persistent-login bootstrap "
        "from README.md instead"
    ),
    "logout": "permanently invalidates the persistent-login session this server depends on",
    "connect": "opens an interactive connection session, which cannot run over MCP",
}


@mcp.tool(
    description=(
        "Escape hatch: run any non-interactive Keeper Commander command and return its raw "
        "output - the catch-all for the full command set beyond the curated tools. Safe "
        "read commands include enterprise-info/ei, enterprise-role, enterprise-team, "
        "enterprise-node, compliance-report, security-audit-report, breachwatch, list-sf, "
        "share-report, user-report and msp-billing-report (add --format=json where "
        "supported); prefer the dedicated keeper_* tool when one exists. record-add/"
        "record-update must use password=$GEN, never plaintext. Mutating/destructive "
        "commands (rm, msp-remove, msp-update, enterprise-user --delete) execute exactly as "
        "given - confirm with the user first. Interactive commands (shell, login, connect) "
        "and logout are refused."
    ),
    annotations={"destructiveHint": True},
)
def keeper_run_command(
    command: Annotated[
        str,
        Field(
            description=(
                "Full Commander command line, e.g. \"user-report --days 30 --format json\". "
                "Do not prefix with 'keeper'."
            )
        ),
    ],
    mc_id: McId = None,
) -> str:
    cleaned = command.strip()
    if cleaned.lower().startswith("keeper "):
        cleaned = cleaned[len("keeper ") :].strip()
    if not cleaned:
        raise ToolError("command must not be empty.")
    try:
        first_token = shlex.split(cleaned)[0].lower()
    except (ValueError, IndexError) as exc:
        raise ToolError(f"Could not parse command: {exc}") from exc
    refusal = _REFUSED_COMMANDS.get(first_token)
    if refusal:
        raise ToolError(
            f"Refusing to run '{first_token}': it {refusal}. This server only supports "
            "non-interactive Commander commands."
        )
    return _run_text(cleaned, mc_id=mc_id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
