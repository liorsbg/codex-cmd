import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ShellWidgetTests(unittest.TestCase):
    def test_widget_replaces_buffer_without_accepting_line(self):
        source = (ROOT / "shell" / "cx.zsh").read_text()

        self.assertIn("cx-replace-buffer()", source)
        self.assertIn('local request="$BUFFER"', source)
        self.assertIn('BUFFER="$generated"', source)
        self.assertIn("CURSOR=${#BUFFER}", source)
        self.assertNotIn("accept-line", source)

    def test_widget_registers_default_keybinding(self):
        source = (ROOT / "shell" / "cx.zsh").read_text()

        self.assertIn("zle -N cx-replace-buffer", source)
        self.assertIn("bindkey '^X^C' cx-replace-buffer", source)

    def test_install_script_uses_symlink_not_copy(self):
        source = (ROOT / "scripts" / "install.sh").read_text()

        self.assertIn("ln -sfn", source)
        self.assertIn("~/.local/bin", source)
        self.assertIn("source ", source)


if __name__ == "__main__":
    unittest.main()
