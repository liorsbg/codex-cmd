# codex-cmd

`codex-cmd` installs `cx`, a small local helper that turns natural language into one shell command using your existing Codex CLI login.

It is built for a fast terminal workflow:

```sh
cx git clone without history
# git clone --depth 1 <URL>
```

`cx` prints a command. It never runs the command for you.

## Quick Start

Requirements:

- macOS or another Unix-like shell environment
- Python 3.9+
- `zsh` for the in-place prompt widget
- `codex` on `PATH`
- `codex login` completed with ChatGPT/Codex subscription auth

One-line install:

```sh
/bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/liorsbg/codex-cmd/main/scripts/bootstrap.sh)"
```

The installer checks for `git`, `python3`, `zsh`, and `codex`, clones the repo into `~/.local/share/codex-cmd`, installs symlinks, and asks before updating `~/.zshrc`.

For a non-interactive install that updates `~/.zshrc` automatically:

```sh
/bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/liorsbg/codex-cmd/main/scripts/bootstrap.sh)" -- --yes
```

Manual install:

```sh
git clone https://github.com/liorsbg/codex-cmd.git ~/.local/share/codex-cmd
cd ~/.local/share/codex-cmd
scripts/install.sh
```

The installer creates these symlinks:

```text
~/.local/bin/cx -> <repo>/bin/cx
~/.config/codex-cmd/cx.zsh -> <repo>/shell/cx.zsh
```

Make sure `~/.local/bin` is on your `PATH`, then test:

```sh
cx git clone without history
```

## In-Place zsh Replacement

The best workflow is the zsh widget. It lets you type a request at the prompt and replace that prompt text with the generated shell command.

Add this line to `~/.zshrc`:

```sh
source ~/.config/codex-cmd/cx.zsh
```

Open a new terminal, then type:

```text
curl <URL> every 5 seconds for 60 seconds
```

Press `Ctrl-X Ctrl-C`. The current prompt buffer is replaced with a command. Review or edit it, then press Enter yourself if it looks right.

The widget does not submit the line automatically.

## CLI Usage

Basic form:

```sh
cx <natural language request>
```

Useful options:

```sh
cx --model gpt-5.4-mini git clone without history
cx --effort low explain disk usage sorted by size
cx --timeout 90 rsync a folder but exclude node_modules
```

Defaults:

- model: `gpt-5.3-codex-spark`
- timeout: `45` seconds
- Codex sandbox: `read-only`
- web search: disabled

`cx --raw` is accepted for the zsh widget. It still prints only the generated command.

## Examples

```sh
cx git clone without history
# git clone --depth 1 <URL>
```

```sh
cx curl '<URL>' every 5 seconds for 60 seconds
# for i in {1..13}; do curl "<URL>"; (( i < 13 )) && sleep 5; done
```

```sh
cx find the biggest files under this directory
# find . -type f -print0 | xargs -0 du -h | sort -hr | head
```

```sh
cx show only commits from last week
# git log --since="1 week ago" --oneline
```

Generated commands may vary. Treat the output like a suggestion from an assistant, not a trusted script.

## Safety Model

`cx` is intentionally conservative:

- It never executes generated commands.
- The zsh widget only replaces `BUFFER`; it does not call `accept-line`.
- Codex runs through `codex exec --json --ephemeral`.
- `cx` passes `--ignore-user-config` and `--ignore-rules` so unrelated local MCP servers, plugins, and repo guidance do not affect command generation.
- `cx` uses `--sandbox read-only` and disables web search for this command-generation task.
- Placeholders such as `<URL>`, `<repo-url>`, and `<file>` are preserved when your request does not include a concrete value.

You still need to inspect generated commands before running them, especially commands that remove files, overwrite data, change permissions, or send network requests.

## Troubleshooting

`cx: codex executable not found on PATH`

Install the Codex CLI, then confirm:

```sh
codex --version
```

`cx: reauthorization is required` or an auth-related Codex error

Refresh your Codex login:

```sh
codex login
```

The zsh keybinding does nothing

Confirm the widget is loaded:

```sh
source ~/.config/codex-cmd/cx.zsh
zsh -ic 'whence -w cx-replace-buffer; bindkey "^X^C"'
```

`cx` works in one terminal but not another

Check that `~/.local/bin` is on `PATH` in the failing terminal:

```sh
command -v cx
```

If it is missing, rerun the bootstrap installer and allow the `~/.zshrc` update, or add this block manually:

```sh
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac
source "$HOME/.config/codex-cmd/cx.zsh"
```

Output is slow

`cx` uses your Codex account and model choice. For faster responses, keep the default Spark model or try:

```sh
cx --model gpt-5.4-mini --effort low <request>
```

## FAQ

Does `cx` use my OpenAI API key?

No. It shells out to `codex exec`, which reuses your existing Codex CLI authentication. You do not need to set `OPENAI_API_KEY` for `cx`.

Does `cx` send my whole repository to Codex?

No. `cx` sends the natural-language request you type. It also runs Codex with `--ignore-user-config`, `--ignore-rules`, and `--skip-git-repo-check` for this narrow command-generation workflow.

Can it run the command automatically?

No. That is deliberate. The output is meant to be reviewed, edited, and run manually.

Can I change the keybinding?

Yes. Source `shell/cx.zsh`, then bind the widget yourself:

```sh
bindkey '^G' cx-replace-buffer
```

Can I use another shell?

The `cx` CLI works from any shell. The in-place prompt replacement is currently a `zsh` ZLE widget.

## Contributing

User-facing docs live here in the README. Contributor docs are separate so the quick start stays easy to scan:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/development.md](docs/development.md)
- [SECURITY.md](SECURITY.md)
- [LICENSE](LICENSE)
