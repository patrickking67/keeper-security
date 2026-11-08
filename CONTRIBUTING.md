# Contributing

Thanks for your interest in improving the Keeper Security agent marketplace and
MCP server. [AGENTS.md](AGENTS.md) has the full layout, commands and safety rules.

## Setup

```bash
git clone https://github.com/patrickking67/keeper-security.git
cd keeper-security
uv sync              # Python 3.13 from .python-version, runtime and dev deps
scripts/check.sh     # must pass before you open a PR
```

You also need `jq` for `scripts/validate-plugins.sh`. The `claude` CLI and
`rumdl` are optional; `scripts/check.sh` uses them when installed.

## Reporting issues

1. Check existing GitHub issues first.
2. Open a new issue with a clear title, what you expected, what happened, and
   the affected plugin, skill or file.
3. Security problems go through
   [private advisories](https://github.com/patrickking67/keeper-security/security/advisories/new),
   not public issues. See [SECURITY.md](SECURITY.md).

## Making changes

1. Branch from `main` with a prefix: `feat/`, `fix/`, `docs/` or `chore/`.
2. Keep edits focused: one plugin or concern per PR.
3. Follow the conventions:
   - SKILL.md frontmatter is single-line `name:` and `description:`.
   - Commands and agents never print secret values into transcripts.
   - Fenced code blocks always declare a language.
   - Command syntax is verified against the official Keeper docs (each plugin
     bundles the keeper-docs MCP server for this).
   - Server changes come with tests in `tests/`. Tests never run Commander or
     contact a Keeper tenant.
4. Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).
   To enforce it locally:
   `ln -s ../../scripts/validate-commit-msg.sh .git/hooks/commit-msg`
5. Add a line to `CHANGELOG.md` under `[Unreleased]`.

## Checks

`scripts/check.sh` runs lint (ruff), format check, the offline test suite,
plugin and marketplace validation, and `claude plugin validate --strict` when
the CLI is present. CI runs the same script on every push and pull request.

Never test with real production secrets; use a trial or test Keeper tenant for
manual testing, and keep its data out of the repo.

## Pull request checklist

- [ ] `scripts/check.sh` passes
- [ ] New or changed commands verified against official Keeper documentation
- [ ] No secret values, tokens, tenant IDs or real configs in code, examples or fixtures
- [ ] Gating (confirm flags, refused commands, redaction) is unchanged or stricter
- [ ] Plugin manifests (`.claude-plugin/` and `.cursor-plugin/`) stay in sync
- [ ] README, AGENTS.md or skill docs updated if behavior or structure changed
- [ ] CHANGELOG.md updated
- [ ] PR describes what changed, why, and how it was tested
