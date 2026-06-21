#!/usr/bin/env sh
set -eu

REPO_URL="${CX_REPO_URL:-https://github.com/liorsbg/codex-cmd.git}"
INSTALL_DIR="${CX_INSTALL_DIR:-$HOME/.local/share/codex-cmd}"
ZSHRC="${CX_ZSHRC:-${ZDOTDIR:-$HOME}/.zshrc}"
YES=0
ZSHRC_MODE="ask"

usage() {
  cat <<'EOF'
Usage: bootstrap.sh [options]

Install or update codex-cmd from GitHub.

Default install dir: ~/.local/share/codex-cmd

Options:
  --yes              Do not prompt; update ~/.zshrc automatically.
  --zshrc            Update ~/.zshrc automatically.
  --no-zshrc         Do not update ~/.zshrc.
  --install-dir DIR  Install repository clone at DIR.
  -h, --help         Show this help.

Environment:
  CX_REPO_URL        Git repository URL to clone.
  CX_INSTALL_DIR     Install repository directory.
  CX_ZSHRC           zsh startup file to update.
EOF
}

say() {
  printf '%s\n' "$*"
}

fail() {
  printf 'cx bootstrap: %s\n' "$*" >&2
  exit 1
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

require_command() {
  if ! command_exists "$1"; then
    fail "required command not found: $1"
  fi
}

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --yes)
        YES=1
        ZSHRC_MODE="yes"
        ;;
      --zshrc)
        ZSHRC_MODE="yes"
        ;;
      --no-zshrc)
        ZSHRC_MODE="no"
        ;;
      --install-dir)
        [ "$#" -ge 2 ] || fail "--install-dir requires a value"
        INSTALL_DIR="$2"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        fail "unknown option: $1"
        ;;
    esac
    shift
  done
}

check_prerequisites() {
  require_command git
  require_command python3
  require_command zsh
  require_command codex

  python3 --version >/dev/null 2>&1 || fail "python3 is installed but not runnable"
  zsh --version >/dev/null 2>&1 || fail "zsh is installed but not runnable"
  codex --version >/dev/null 2>&1 || fail "codex is installed but not runnable"

  if ! codex login status >/dev/null 2>&1; then
    say "Codex CLI is installed, but login status could not be confirmed."
    say "Run this if cx later reports an auth error: codex login"
  fi
}

clone_or_update_repo() {
  if [ -d "$INSTALL_DIR/.git" ]; then
    remote_url="$(git -C "$INSTALL_DIR" remote get-url origin 2>/dev/null || true)"
    if [ "$remote_url" != "$REPO_URL" ]; then
      fail "$INSTALL_DIR already exists with a different origin: $remote_url"
    fi
    if ! git -C "$INSTALL_DIR" diff --quiet || ! git -C "$INSTALL_DIR" diff --cached --quiet; then
      fail "$INSTALL_DIR has local changes; commit, stash, or remove them before updating"
    fi
    say "Updating $INSTALL_DIR"
    git -C "$INSTALL_DIR" fetch --depth 1 origin main
    git -C "$INSTALL_DIR" checkout -B main FETCH_HEAD
    return
  fi

  if [ -e "$INSTALL_DIR" ]; then
    fail "$INSTALL_DIR already exists and is not a git repository"
  fi

  say "Cloning $REPO_URL into $INSTALL_DIR"
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
}

install_links() {
  sh "$INSTALL_DIR/scripts/install.sh"
}

zshrc_has_codex_cmd() {
  [ -f "$ZSHRC" ] && grep -q 'codex-cmd' "$ZSHRC"
}

append_zshrc_block() {
  mkdir -p "$(dirname "$ZSHRC")"
  touch "$ZSHRC"

  if zshrc_has_codex_cmd; then
    say "$ZSHRC already appears to load codex-cmd"
    return
  fi

  cat >>"$ZSHRC" <<'EOF'

# codex-cmd
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac
source "$HOME/.config/codex-cmd/cx.zsh"
EOF

  say "Updated $ZSHRC"
}

prompt_yes_no() {
  prompt="$1"

  if [ "$YES" -eq 1 ]; then
    return 0
  fi

  if [ ! -r /dev/tty ]; then
    return 1
  fi

  printf '%s [y/N] ' "$prompt" >/dev/tty
  read answer </dev/tty || return 1
  case "$answer" in
    y|Y|yes|YES)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

maybe_update_zshrc() {
  case "$ZSHRC_MODE" in
    yes)
      append_zshrc_block
      ;;
    no)
      say "Skipped zsh startup update."
      say "To enable the widget later, add: source \$HOME/.config/codex-cmd/cx.zsh"
      ;;
    ask)
      if prompt_yes_no "Update $ZSHRC to add ~/.local/bin to PATH and enable the zsh widget?"; then
        append_zshrc_block
      else
        say "Skipped zsh startup update."
        say "To enable the widget later, add: source \$HOME/.config/codex-cmd/cx.zsh"
      fi
      ;;
    *)
      fail "internal error: invalid zshrc mode: $ZSHRC_MODE"
      ;;
  esac
}

print_next_steps() {
  say ""
  say "Installed codex-cmd."
  say "Open a new terminal, then run:"
  say "  cx git clone without history"
  say ""
  say "For in-place zsh replacement, type a request and press Ctrl-X Ctrl-C."
}

main() {
  parse_args "$@"
  check_prerequisites
  clone_or_update_repo
  install_links
  maybe_update_zshrc
  print_next_steps
}

main "$@"
