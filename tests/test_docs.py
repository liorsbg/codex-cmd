import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PublicDocsTests(unittest.TestCase):
    def test_readme_is_user_first_and_links_to_contributor_docs(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        required_sections = [
            "# codex-cmd",
            "## Quick Start",
            "## In-Place zsh Replacement",
            "## CLI Usage",
            "## Examples",
            "## Safety Model",
            "## Troubleshooting",
            "## FAQ",
            "## Contributing",
        ]
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, readme)

        self.assertLess(readme.index("## Quick Start"), readme.index("## Contributing"))
        self.assertIn("[CONTRIBUTING.md](CONTRIBUTING.md)", readme)
        self.assertIn("[docs/development.md](docs/development.md)", readme)
        self.assertIn("[SECURITY.md](SECURITY.md)", readme)

    def test_contributor_and_security_docs_exist_with_expected_sections(self):
        expected = {
            "CONTRIBUTING.md": [
                "# Contributing",
                "## Development Setup",
                "## Test Commands",
                "## Pull Request Checklist",
            ],
            "docs/development.md": [
                "# Development Guide",
                "## Architecture",
                "## Command Flow",
                "## Release Checklist",
            ],
            "SECURITY.md": [
                "# Security Policy",
                "## What cx Does Not Collect",
                "## Reporting Vulnerabilities",
            ],
            "LICENSE": [
                "MIT License",
            ],
        }

        for relative_path, sections in expected.items():
            with self.subTest(path=relative_path):
                content = (ROOT / relative_path).read_text(encoding="utf-8")
                for section in sections:
                    self.assertIn(section, content)

    def test_markdown_links_point_to_repo_files_or_safe_external_targets(self):
        markdown_files = [
            ROOT / "README.md",
            ROOT / "CONTRIBUTING.md",
            ROOT / "SECURITY.md",
            ROOT / "docs" / "development.md",
        ]
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

        for path in markdown_files:
            content = path.read_text(encoding="utf-8")
            for target in link_pattern.findall(content):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                if target.startswith("#"):
                    continue
                local_target = target.split("#", 1)[0]
                resolved = (path.parent / local_target).resolve()
                with self.subTest(path=path.name, target=target):
                    self.assertTrue(resolved.exists(), f"{target} does not exist")


if __name__ == "__main__":
    unittest.main()
