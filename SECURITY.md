# Security Policy

`codex-cmd` is a local command generator. It is designed to produce a shell command for you to inspect, not to run commands automatically.

## What cx Does Not Collect

`cx` does not collect, store, or upload credentials.

It does not read `~/.codex/auth.json` directly. Authentication is handled by the installed Codex CLI through `codex exec`.

It does not execute generated commands. In CLI mode it prints a command to stdout. In zsh widget mode it replaces the editable prompt buffer.

## Data Sent to Codex

`cx` sends the natural-language request you provide to `codex exec`.

It uses:

- `--ignore-user-config`
- `--ignore-rules`
- `--skip-git-repo-check`
- `--sandbox read-only`
- `web_search='disabled'`

These flags are intended to keep command generation independent from local repository contents, user rules, MCP servers, plugins, and web search.

## Reporting Vulnerabilities

Please report security issues through GitHub's private vulnerability reporting flow if it is available for this repository.

If private reporting is not available, open a GitHub issue with a minimal public description and avoid including exploit details, secrets, tokens, or private logs. The maintainer can then coordinate a safer disclosure path.

## Safe Disclosure Expectations

When reporting an issue:

- Include the affected version or commit.
- Include your operating system and shell.
- Include the smallest reproduction you can share safely.
- Redact account identifiers, tokens, local paths, and private command output.

## Out of Scope

Generated shell commands are model output. A command may be wrong, unsafe, or incomplete. Users are expected to inspect generated commands before running them.

Security issues in the Codex CLI itself should be reported to the Codex/OpenAI project through its own reporting channels.
