# Development Guide

This guide is for contributors who want to understand how `codex-cmd` works internally.

## Architecture

`codex-cmd` has three small parts:

- `bin/cx`: repo-local executable wrapper. It adds `src/` to `sys.path` when run from a clone or symlink.
- `src/codex_cmd/cli.py`: argument parsing, prompt construction, Codex invocation, and error handling.
- `src/codex_cmd/jsonl.py`: extraction of the final assistant message from `codex exec --json` output.
- `shell/cx.zsh`: zsh ZLE widget that replaces the active prompt buffer.

The Python CLI is intentionally small. It delegates model access and authentication to the installed Codex CLI.

## Command Flow

For normal CLI use:

1. User runs `cx <request>`.
2. `cx` builds a narrow prompt asking for exactly one shell command.
3. `cx` runs `codex exec --json --ephemeral --ignore-user-config --ignore-rules --skip-git-repo-check --sandbox read-only`.
4. `cx` parses JSONL stdout and extracts the final `agent_message`.
5. `cx` prints only the generated command to stdout.

For zsh widget use:

1. User types a natural-language request at the prompt.
2. User presses `Ctrl-X Ctrl-C`.
3. `cx-replace-buffer` calls `cx --raw -- "$BUFFER"`.
4. On success, the widget assigns the generated text to `BUFFER` and moves `CURSOR` to the end.
5. The widget does not call `accept-line`; the user must press Enter manually.

## Codex Invocation

The Codex subprocess arguments are built in `build_codex_args()`.

Current defaults:

- `--json`
- `--ephemeral`
- `--skip-git-repo-check`
- `--ignore-user-config`
- `--ignore-rules`
- `--sandbox read-only`
- `-c web_search='disabled'`
- `-m gpt-5.3-codex-spark`

These flags keep this workflow narrow and predictable. `cx` should not depend on the caller's repository, local MCP servers, plugins, or user rules.

## Prompt Contract

The prompt is built in `build_prompt()`.

The important contract:

- output exactly one shell command
- no Markdown
- no explanation
- do not execute commands or call tools
- preserve placeholders when concrete values are missing
- prefer conservative command forms

Tests should verify the contract text when it changes.

## JSONL Parsing

`extract_final_message()` accepts Codex JSONL stdout and returns the last message-like text it can find. It currently recognizes:

- `agent_message.text`
- `agent_message.message`
- `final_message.content`
- `final_response.content`
- plain non-JSON fallback lines

If Codex changes JSONL shape, add a failing parser test first.

## Release Checklist

Before publishing changes:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
zsh -n shell/cx.zsh
sh -n scripts/install.sh
```

For public releases, also run a privacy-oriented scan over tracked files:

```sh
git grep -n -I -E '(/Users/|auth\.json|OPENAI_API_KEY|CODEX_API_KEY|token|secret|password|credential|ghp_|github_pat_|sk-[A-Za-z0-9])' HEAD
```

Review matches manually. Some words, such as `input_tokens` in tests, may be benign.

## Public History Hygiene

Public commits should use public-safe author metadata. Avoid publishing local hostnames or private email addresses in commit metadata.

Recommended author email:

```text
liorsbg@users.noreply.github.com
```
