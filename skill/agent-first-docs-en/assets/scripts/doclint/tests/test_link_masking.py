import importlib.util
import unittest
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[2] / "check-doc-links.py"
spec = importlib.util.spec_from_file_location("check_doc_links", CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class MaskFencesTest(unittest.TestCase):
    def test_nested_four_backtick(self):
        text = "a\n````md\n```\n[x](n.md)\n```\n[y](m.md)\n````\n[z](ok.md)\n"
        out = checker.mask_fences(text)
        self.assertNotIn("n.md", out)
        self.assertNotIn("m.md", out)
        self.assertIn("[z](ok.md)", out)

    def test_indented_fence_in_list(self):
        for pad in ("  ", "   "):
            text = f"- item\n{pad}```\n{pad}[x](n.md)\n{pad}```\n[z](ok.md)\n"
            out = checker.mask_fences(text)
            self.assertNotIn("n.md", out)
            self.assertIn("ok.md", out)

    def test_four_space_not_opener(self):
        text = "    ```\n[x](n.md)\n"
        self.assertEqual(checker.mask_fences(text), text)

    def test_unclosed(self):
        out = checker.mask_fences("a\n```\n[x](n.md)\nmore\n")
        self.assertNotIn("n.md", out)
        self.assertNotIn("more", out)
        self.assertTrue(out.startswith("a\n"))

    def test_tilde(self):
        out = checker.mask_fences("~~~~\n[x](n.md)\n~~~\n[y](m.md)\n~~~~\n[z](ok.md)\n")
        self.assertNotIn("n.md", out)
        self.assertNotIn("m.md", out)
        self.assertIn("ok.md", out)

    def test_backtick_info_with_backtick_not_opener(self):
        text = "``` a`b\n[x](n.md)\n"
        self.assertEqual(checker.mask_fences(text), text)

    def test_layout_preserved(self):
        text = "a\n```py\n[x](n.md)\n```\n\n`[i](j.md)` tail\n"
        for out in (checker.mask_fences(text), checker.mask_code(text)):
            self.assertEqual(len(out), len(text))
            self.assertEqual([i for i, c in enumerate(out) if c == "\n"], [i for i, c in enumerate(text) if c == "\n"])
        self.assertNotIn("j.md", checker.mask_code(text))


if __name__ == "__main__":
    unittest.main()
