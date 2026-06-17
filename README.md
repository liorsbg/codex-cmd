# codex-cmd

`codex-cmd` installs `cx`, a local command that turns natural language into one shell command using your existing Codex CLI login.

## Usage

```sh
cx git clone without history
cx curl '<URL>' every 5 seconds for 60 seconds
```

`cx` prints the generated command. It never runs it.

## In-Place zsh Replacement

Source the widget:

```sh
source ~/.config/codex-cmd/cx.zsh
```

Then type a request at your prompt and press `Ctrl-X Ctrl-C`. The current prompt buffer is replaced with the generated command. Press Enter only after reviewing it.

## Install

```sh
scripts/install.sh
```

Add the printed `source .../cx.zsh` line to `~/.zshrc` when you want the widget loaded in new shells.

## Requirements

- `codex` on `PATH`
- `codex login` completed with ChatGPT/Codex subscription auth
- Python 3.9+
- `zsh` for the in-place prompt widget

## Smoke Test

```sh
bin/cx git clone without history
```
