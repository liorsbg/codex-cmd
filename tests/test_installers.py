import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class BootstrapInstallerTests(unittest.TestCase):
    def test_bootstrap_has_one_line_install_contract(self):
        source = (ROOT / "scripts" / "bootstrap.sh").read_text(encoding="utf-8")

        self.assertIn("https://github.com/liorsbg/codex-cmd.git", source)
        self.assertIn("git clone --depth 1", source)
        self.assertIn("scripts/install.sh", source)
        self.assertIn("~/.local/share/codex-cmd", source)

    def test_bootstrap_checks_prerequisites_and_codex_login(self):
        source = (ROOT / "scripts" / "bootstrap.sh").read_text(encoding="utf-8")

        for command in ["git", "python3", "zsh", "codex"]:
            with self.subTest(command=command):
                self.assertIn(f"require_command {command}", source)
        self.assertIn("codex login status", source)
        self.assertIn("codex login", source)

    def test_bootstrap_updates_zshrc_only_with_confirmation_or_yes_flag(self):
        source = (ROOT / "scripts" / "bootstrap.sh").read_text(encoding="utf-8")

        self.assertIn("--yes", source)
        self.assertIn("--no-zshrc", source)
        self.assertIn("/dev/tty", source)
        self.assertIn("append_zshrc_block", source)
        self.assertIn(".config/codex-cmd/cx.zsh", source)
        self.assertIn(".local/bin", source)

    def test_readme_documents_one_line_and_manual_install_paths(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("curl -fsSL https://raw.githubusercontent.com/liorsbg/codex-cmd/main/scripts/bootstrap.sh", readme)
        self.assertIn("scripts/install.sh", readme)
        self.assertIn("--yes", readme)


if __name__ == "__main__":
    unittest.main()
