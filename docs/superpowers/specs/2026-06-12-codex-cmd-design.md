# Codex Cmd Design

## Goal

Build a fast local command, installed as `cx`, that turns natural language into shell commands using the user's existing Codex subscription and saved Codex CLI authentication. The primary workflow is an in-place `zsh` prompt replacement: type a natural-language request, press a keybinding, inspect or edit the generated command, then press Enter manually.

## User Experience

The default terminal flow is:

1. Type a request at a `zsh` prompt, for example `git clone without history`.
2. Press the configured `zsh` keybinding.
3. The current input buffer is replaced with a generated command, for example `git clone --depth 1 <repository-url>`.
4. The user edits or runs the command manually.

The fallback flow is:

```sh
cx git clone without history
```

This prints only the generated shell command to stdout. It does not execute the command.

## Architecture

`cx` is a small Python CLI that shells out to `codex exec` in non-interactive JSONL mode. It sends a narrow prompt over stdin, parses the final Codex agent message from JSONL output, and prints only the command. It uses `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, `--skip-git-repo-check`, `--sandbox read-only`, and `web_search='disabled'` so command generation is isolated from local repo state, MCP servers, plugins, and persistent rollout files.

The `zsh` integration is a separate sourced file. It defines a ZLE widget that reads `BUFFER`, calls `cx --raw -- "$BUFFER"`, and replaces `BUFFER` with stdout on success. This has to live inside the parent shell because a normal executable cannot mutate the active shell input buffer.

## Model Defaults

The default model is `gpt-5.3-codex-spark` because a local smoke test showed it is available in this Codex account and faster than `gpt-5.4-mini` for this use case. The implementation keeps `--model` configurable so the user can switch to `gpt-5.4-mini` or another Codex model without changing code.

The default prompt does not request tools, web search, file reads, or command execution. It asks Codex to output exactly one shell command, without Markdown fences or explanations.

## Safety

`cx` never executes generated commands. The `zsh` widget replaces the prompt buffer but leaves the cursor at the end so the user must explicitly press Enter.

The prompt should prefer conservative command forms and preserve placeholders like `<URL>` and `<repository-url>` when the input lacks a concrete value. For dangerous requests, the generated output should still be a command string rather than an action taken by the tool; user review remains the safety gate.

## Files

- `bin/cx`: executable entrypoint for development and symlink installs.
- `src/codex_cmd/cli.py`: argument parsing, prompt construction, Codex subprocess invocation, and stdout/stderr behavior.
- `src/codex_cmd/jsonl.py`: JSONL final-message extraction from `codex exec --json`.
- `shell/cx.zsh`: ZLE widget and default keybinding.
- `tests/`: unit tests for parsing, command construction, CLI behavior, and shell integration text.
- `scripts/install.sh`: local installer that symlinks `cx` and prints the shell source line.

## Testing

Unit tests use Python's standard `unittest` module and mock subprocess execution so the suite is fast and does not consume Codex credits. Manual smoke testing runs `bin/cx "git clone without history"` against the real Codex CLI, then sources `shell/cx.zsh` in an interactive `zsh` session for prompt-buffer validation.

## Install Policy

The first implementation will install source files under the repo and provide an installer script. Updating `~/.zshrc` automatically should remain opt-in because it edits user shell startup state outside the repo.
