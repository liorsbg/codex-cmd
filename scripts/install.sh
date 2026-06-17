#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
BIN_DIR="${HOME}/.local/bin"
SHELL_DIR="${HOME}/.config/codex-cmd"

mkdir -p "$BIN_DIR" "$SHELL_DIR"
ln -sfn "$ROOT_DIR/bin/cx" "$BIN_DIR/cx"
ln -sfn "$ROOT_DIR/shell/cx.zsh" "$SHELL_DIR/cx.zsh"

printf '%s\n' "Installed cx -> $BIN_DIR/cx"
printf '%s\n' "Installed cx under ~/.local/bin"
printf '%s\n' "To enable in-place zsh replacement, add this to ~/.zshrc:"
printf '%s\n' "source $SHELL_DIR/cx.zsh"
printf '%s\n' "Default keybinding: Ctrl-X Ctrl-C"
