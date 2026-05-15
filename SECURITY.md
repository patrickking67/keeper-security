# Security Policy

Because this plugin bridges Claude with Keeper Security's CLI tooling and vault, security reports are taken seriously and triaged quickly.

## Supported versions

| Version | Supported          |
|---------|--------------------|
| 1.1.x   | :white_check_mark: |
| 0.1.x   | :x:                |

Older pre-1.1 versions will not receive backported fixes — please upgrade.

## Reporting a vulnerability

**Do not open a public GitHub issue for security reports.**

Email: **patrickking673@gmail.com**
Subject: `[keeper-plugin SECURITY] <short description>`

Please include:

- A clear description of the issue
- Steps to reproduce (a minimal proof-of-concept is ideal)
- Affected version(s) / commit SHA
- Any known mitigations or workarounds

You'll get an acknowledgement within 72 hours. Confirmed issues will be fixed and disclosed via a GitHub Security Advisory once a patched release is available.

For vulnerabilities in **Keeper Security's own products** (KSM CLI, Commander, Keeper Vault, Keeper Automator), report directly to Keeper at <https://www.keepersecurity.com/security.html>. This repo only ships skill prompts, MCP configuration, and documentation — it does not redistribute or modify Keeper's binaries.

## Scope

In scope:

- Skill prompts in `skills/*/SKILL.md` and their `references/` files
- MCP server configuration in `.mcp.json`
- Plugin manifest in `.claude-plugin/plugin.json`
- Any code in this repository

Out of scope:

- Vulnerabilities in Keeper's CLI tools, vault, or hosted services — report to Keeper directly
- Vulnerabilities in Claude Code, Cowork, or the Anthropic API — report to Anthropic
- Vulnerabilities in the GitBook-hosted Keeper docs MCP server — report to Keeper / GitBook

## Handling secrets

This plugin is designed so that **no secret material ever lives in this repository or in skill prompts**. If you find a place where a skill encourages echoing, logging, or writing a real secret to disk in plaintext beyond what the user explicitly asked for, that's a bug — please report it.

When demonstrating the plugin, never paste real vault records, KSM client tokens, or one-time access codes into issues, pull requests, or commit messages. Use the placeholders the existing skills already provide.
