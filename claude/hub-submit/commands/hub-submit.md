---
description: Upload a Claude Code plugin or command to the Remedio AI Hub (opens a review PR)
allowed-tools: Bash(python3:*), Bash(ls:*), Bash(cat:*), Read, mcp__ai-hub__add_plugin, mcp__ai-hub__edit_plugin, mcp__ai-hub__add_skill, mcp__ai-hub__edit_skill, mcp__ai-hub__list_plugins, mcp__ai-hub__list_skills, mcp__ai-hub__get_item, mcp__ai-hub__install_plugin, mcp__ai-hub__install_skill, mcp__ai-hub__install_marketplace
---

Upload a plugin, command, or skill to the Remedio AI Hub. A public submission opens a
review PR in `gytpol/ai-hub` (nothing is published until a maintainer merges); inside a
space you own as space-admin, changes publish immediately.

There are two routes. **Prefer the `ai-hub` MCP** — it signs in with your existing Hub
SSO (no cookie to manage) and enforces the hub's authoring lints + semver. Fall back to
the bundled `upload.py` only for the one thing the MCP can't do: push **inline local
plugin/command files**.

Arguments: $ARGUMENTS

## Route A — the `ai-hub` MCP (preferred: SSO, no token)

Use this when its tools are available (they appear namespaced `mcp__ai-hub__*`). If they
aren't, the plugin isn't installed — tell the user to run
`/plugin marketplace add gytpol/ai-hub@marketplace` then `/plugin install ai-hub-mcp@remedio`
and restart Claude Code, then use Route B in the meantime. The *first* MCP call may open a
browser for SSO login — that's expected; the session is cached and refreshed silently after.

Map the request to a tool:
- **Add a plugin/skill that lives in a GitHub repo** → `add_plugin` `{repo:"owner/repo"|URL, ref?, subdir?, name?, description?, tags?, space?}`. The source is validated against GitHub and pinned to a commit.
- **Author a new skill from inline content** → `add_skill` `{name, description (write it as a "Use when…" trigger), body (the SKILL.md markdown, no frontmatter), tags?, space?}`.
- **Edit a skill** (content or metadata) → `edit_skill` `{slug, …only the fields to change}`.
- **Edit a plugin's metadata** → `edit_plugin` `{slug, description?, tags?, version?, space?}`. `version` MUST increase (semver). NOTE: this rewrites **only `plugin.json`** — it does NOT change the plugin's command/skill files. To change those, use Route B.
- **Find / install** → `list_plugins`, `list_skills`, `get_item`, `install_plugin`, `install_skill`, `install_marketplace` (the `install_*` tools return the exact `/plugin …` commands to paste — add the marketplace first, then install).

Report what the tool returns (slug, scope public/space, pending-review vs published, any
lint warnings, PR url). On failure the hub returns a structured error envelope — relay it.

## Route B — `upload.py` (inline local files; uses a session cookie)

Use this to upload **local files** the MCP can't ingest inline: wrapping a local
slash-command `.md` as a one-command plugin, or updating an authored-in-hub plugin's actual
files. (`add_plugin` only ingests GitHub repos; `edit_plugin` only touches metadata — so a
local command body, e.g. `/speak`, must go through here.)

The uploader lives next to this command at `scripts/upload.py`. It reads a hub session
token from `$REMEDIO_HUB_COOKIE` or `~/.config/remedio-hub/cookie.txt`; if it's missing or
stale the script prints how to refresh it — relay that message to the user as-is.

1. Decide what to upload from the arguments:
   - A plugin directory (one with a `.claude-plugin/plugin.json` manifest) uploads the whole dir.
   - A single command markdown file gets wrapped as a one-command plugin via the command flag.
   - If empty or ambiguous, ask which directory or command file to upload.
2. Run the uploader, pointing at wherever `upload.py` is installed:
   - Plugin directory: `python3 PATH/upload.py DIR --tags tag1,tag2`
   - Single command: `python3 PATH/upload.py --command FILE.md --tags tag1,tag2` (slug defaults to the filename stem)
   - Optional overrides: `--slug`, `--name`, `--desc`. Use `--mode update` to update an existing entry.
3. Report the PR number and URL the script prints. If it reports an auth error, relay the
   refresh instructions it gives. A `403 text/html` means the hub's edge firewall (a content/WAF
   rule, not auth) rejected the body — note that and suggest the website UI. Only report what
   the script actually returns — never invent success.
