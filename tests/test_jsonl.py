import unittest

from codex_cmd.jsonl import extract_final_message


class ExtractFinalMessageTests(unittest.TestCase):
    def test_extracts_agent_message_text_from_codex_jsonl(self):
        stdout = "\n".join(
            [
                '{"type":"thread.started","thread_id":"t"}',
                '{"type":"turn.started"}',
                '{"type":"item.completed","item":{"type":"agent_message","text":"git clone --depth 1 <repo-url>"}}',
                '{"type":"turn.completed","usage":{"input_tokens":1}}',
            ]
        )

        result = extract_final_message(stdout)

        self.assertEqual(result, "git clone --depth 1 <repo-url>")

    def test_uses_last_agent_message_when_multiple_messages_exist(self):
        stdout = "\n".join(
            [
                '{"type":"item.completed","item":{"type":"agent_message","text":"first"}}',
                '{"type":"item.completed","item":{"type":"agent_message","text":"second"}}',
            ]
        )

        result = extract_final_message(stdout)

        self.assertEqual(result, "second")

    def test_falls_back_to_plain_text_lines(self):
        stdout = "ignored progress\ncurl <URL>"

        result = extract_final_message(stdout)

        self.assertEqual(result, "curl <URL>")

    def test_raises_when_no_message_is_available(self):
        with self.assertRaises(ValueError):
            extract_final_message('{"type":"turn.completed"}')


if __name__ == "__main__":
    unittest.main()
