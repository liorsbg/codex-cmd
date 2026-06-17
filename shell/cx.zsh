# Source this file from zsh to enable in-place Codex command generation.

cx-replace-buffer() {
  emulate -L zsh
  local request="$BUFFER"

  if [[ -z "${request//[[:space:]]/}" ]]; then
    zle -M "cx: type a command request first"
    return 1
  fi

  local generated
  local error_file
  error_file="$(mktemp -t cx-widget.XXXXXX)" || return 1

  generated="$(cx --raw -- "$request" 2>"$error_file")"
  local status=$?
  if (( status != 0 )); then
    local error
    error="$(tail -n 1 "$error_file" 2>/dev/null)"
    rm -f "$error_file"
    zle -M "${error:-cx failed}"
    return "$status"
  fi

  rm -f "$error_file"
  BUFFER="$generated"
  CURSOR=${#BUFFER}
}

zle -N cx-replace-buffer
bindkey '^X^C' cx-replace-buffer
