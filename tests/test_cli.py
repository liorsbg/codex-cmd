import io
import pathlib
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from codex_cmd.cli import build_codex_args, build_prompt, main


ROOT = pathlib.Path(__file__).resolve().parents[1]


class BuildPromptTests(unittest.TestCase):
    def test_prompt_contains_request_and_output_contract(self):
        prompt = build_prompt("git clone without history")

        self.assertIn("git clone without history", prompt)
        self.assertIn("Output exactly one shell command", prompt)
        self.assertIn("Do not execute", prompt)


class BuildCodexArgsTests(unittest.TestCase):
    def test_uses_fast_subscription_backed_defaults(self):
        args = build_codex_args(model="gpt-5.3-codex-spark", effort=None)

        self.assertEqual(args[0:2], ["codex", "exec"])
        self.assertIn("--json", args)
        self.assertIn("--ephemeral", args)
        self.assertIn("--ignore-user-config", args)
        self.assertIn("--ignore-rules", args)
        self.assertIn("--skip-git-repo-check", args)
        self.assertIn("--sandbox", args)
        self.assertIn("read-only", args)
        self.assertIn("-m", args)
        self.assertIn("gpt-5.3-codex-spark", args)
        self.assertIn("web_search='disabled'", args)
        self.assertEqual(args[-1], "-")

    def test_adds_reasoning_effort_when_requested(self):
        args = build_codex_args(model="gpt-5.4-mini", effort="low")

        self.assertIn("model_reasoning_effort='low'", args)


class MainTests(unittest.TestCase):
    def test_prints_final_command_only(self):
        completed = subprocess.CompletedProcess(
            args=["codex"],
            returncode=0,
            stdout='{"type":"item.completed","item":{"type":"agent_message","text":"git clone --depth 1 <repo-url>"}}\n',
            stderr="OpenAI Codex progress\n",
        )
        stdout = io.StringIO()

        with patch("subprocess.run", return_value=completed) as run:
            with redirect_stdout(stdout):
                status = main(["git", "clone", "without", "history"])

        self.assertEqual(status, 0)
        self.assertEqual(stdout.getvalue(), "git clone --depth 1 <repo-url>\n")
        run.assert_called_once()
        _, kwargs = run.call_args
        self.assertIn("git clone without history", kwargs["input"])
        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])
        self.assertEqual(kwargs["timeout"], 45)

    def test_returns_nonzero_when_codex_fails(self):
        completed = subprocess.CompletedProcess(
            args=["codex"],
            returncode=1,
            stdout="",
            stderr="reauthorization is required\n",
        )
        stderr = io.StringIO()

        with patch("subprocess.run", return_value=completed):
            with redirect_stderr(stderr):
                status = main(["git clone without history"])

        self.assertEqual(status, 1)
        self.assertIn("reauthorization is required", stderr.getvalue())

    def test_requires_a_request(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            status = main([])

        self.assertEqual(status, 2)
        self.assertIn("provide a natural-language command request", stderr.getvalue())


class PackagingTests(unittest.TestCase):
    def test_pyproject_exposes_cx_console_script(self):
        with open("pyproject.toml", encoding="utf-8") as handle:
            pyproject = handle.read()

        self.assertIn('cx = "codex_cmd.cli:main"', pyproject)

    def test_bin_wrapper_adds_repo_src_to_python_path(self):
        wrapper = (ROOT / "bin" / "cx").read_text()

        self.assertIn("Path(__file__).resolve()", wrapper)
        self.assertIn("sys.path.insert", wrapper)


if __name__ == "__main__":
    unittest.main()
