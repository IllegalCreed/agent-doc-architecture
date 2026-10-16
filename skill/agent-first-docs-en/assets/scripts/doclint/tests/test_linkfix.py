import unittest

from doclint import linkfix


class RebaseTest(unittest.TestCase):
    def test_rebase(self):
        text = "见 [需求](../../plans/changes/x/requirements.md#背景)、[外链](https://a.b/c)、[锚](#本节)、[同级](by-layer.md)"
        out = linkfix.rebase_links(text, "docs/testing/cases", "docs/plans/changes/y")
        self.assertIn("[需求](../x/requirements.md#背景)", out)
        self.assertIn("[外链](https://a.b/c)", out)
        self.assertIn("[锚](#本节)", out)
        self.assertIn("[同级](../../../testing/cases/by-layer.md)", out)


class AppendUnderTest(unittest.TestCase):
    def test_existing_section_keeps_following_sections(self):
        text = "# t\n\n## 实施记录\n\n- 旧\n\n## 验证\n\n- v\n"
        out = linkfix.append_under(text, "## 实施记录", "### 新\n\n- n\n")
        self.assertLess(out.index("- 旧"), out.index("### 新"))
        self.assertLess(out.index("### 新"), out.index("## 验证"))

    def test_missing_section_and_none(self):
        self.assertTrue(linkfix.append_under("# t\n", "## 实施记录", "x\n").endswith("## 实施记录\n\nx\n"))
        self.assertTrue(linkfix.append_under("# t\n", None, "x\n").endswith("# t\n\nx\n"))


if __name__ == "__main__":
    unittest.main()
