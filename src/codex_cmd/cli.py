"""Command line interface for cx."""

import argparse
import subprocess
import sys
from typing import List, Optional, Sequence

from .jsonl import extract_final_message


DEFAULT_MODEL = "gpt-5.3-codex-spark"
DEFAULT_TIMEOUT_SECONDS = 45


def build_prompt(request: str) -> str:
    return "\n".join(
        [
            "You convert natural-language requests into macOS zsh-compatible shell commands.",
            "Do not execute shell commands or call tools.",
            "Output exactly one shell command.",
            "Do not use Markdown, backticks, commentary, or explanations.",
            "Preserve placeholders such as <URL>, <repo-url>, and <file> when the user did not provide concrete values.",
            "Prefer conservative commands that a user can inspect before running.",
            f"Request: {request}",
        ]
    )


def build_codex_args(model: str, effort: Optional[str]) -> List[str]:
    args = [
        "codex",
        "exec",
        "--json",
        "--ephemeral",
        "--skip-git-repo-check",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "-m",
        model,
        "-c",
        "web_search='disabled'",
    ]
    if effort:
        args.extend(["-c", f"model_reasoning_effort='{effort}'"])
    args.append("-")
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cx",
        description="Generate one shell command from natural language using Codex.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--effort", choices=["low", "medium", "high", "xhigh"])
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Accepted for shell-widget callers; stdout is always command-only.",
    )
    parser.add_argument("request", nargs=argparse.REMAINDER)
    args = parser.parse_args(list(argv) if argv is not None else None)

    request_parts = list(args.request)
    if request_parts and request_parts[0] == "--":
        request_parts = request_parts[1:]
    request = " ".join(request_parts).strip()
    if not request:
        print("cx: provide a natural-language command request", file=sys.stderr)
        return 2

    codex_args = build_codex_args(args.model, args.effort)
    try:
        result = subprocess.run(
            codex_args,
            input=build_prompt(request),
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
    except FileNotFoundError:
        print("cx: codex executable not found on PATH", file=sys.stderr)
        return 127
    except subprocess.TimeoutExpired:
        print(f"cx: codex timed out after {args.timeout}s", file=sys.stderr)
        return 124

    if result.returncode != 0:
        message = _stderr_tail(result.stderr) or f"codex exited with status {result.returncode}"
        print(f"cx: {message}", file=sys.stderr)
        return result.returncode

    try:
        command = extract_final_message(result.stdout)
    except ValueError as exc:
        print(f"cx: {exc}", file=sys.stderr)
        return 1

    print(command)
    return 0


def _stderr_tail(stderr: str) -> str:
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    return lines[-1] if lines else ""
