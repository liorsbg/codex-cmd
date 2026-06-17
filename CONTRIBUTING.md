# Contributing

Thanks for taking the time to improve `codex-cmd`.

The project goal is narrow: make it fast and safe to turn a short natural-language request into one inspectable shell command.

## Development Setup

Clone the repo:

```sh
git clone https://github.com/liorsbg/codex-cmd.git
cd codex-cmd
```

Use the source tree directly:

```sh
PYTHONPATH=src bin/cx git clone without history
```

Optional local install:

```sh
scripts/install.sh
```

The installer creates symlinks. It does not edit your shell startup files.

## Test Commands

Run the unit tests:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Check shell script syntax:

```sh
zsh -n shell/cx.zsh
sh -n scripts/install.sh
```

Run a real smoke test if you have Codex CLI auth configured:

```sh
PYTHONPATH=src bin/cx git clone without history
```

## Code Style

- Keep the dependency footprint at zero unless there is a strong reason to add one.
- Prefer focused standard-library Python over framework code.
- Keep generated output command-only on stdout.
- Send user-facing failures to stderr with a `cx:` prefix.
- Do not add behavior that executes generated commands automatically.

## Documentation Style

- Keep the README user-first.
- Put internals and contributor detail in `docs/development.md`.
- Keep examples copy-pasteable.
- Avoid promising exact generated commands; model output may vary.
- Be explicit about safety boundaries.

## Pull Request Checklist

Before opening a PR:

- [ ] The change keeps `cx` command-only and non-executing.
- [ ] `PYTHONPATH=src python3 -m unittest discover -s tests -v` passes.
- [ ] `zsh -n shell/cx.zsh` passes if shell code changed.
- [ ] `sh -n scripts/install.sh` passes if installer code changed.
- [ ] README changes stay user-first.
- [ ] New files do not include local paths, tokens, credentials, or private account data.

## Release Notes

For user-visible changes, include:

- what changed
- how users opt into it
- any compatibility or safety implications
- the verification command used
