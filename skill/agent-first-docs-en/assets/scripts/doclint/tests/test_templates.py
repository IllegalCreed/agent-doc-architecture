import unittest

from doclint import templates
from doclint.tests.fixtures import make_repo

NOTES = (
    "<!-- template\napplies-to: docs/releases/v*.md\nexcept: docs/releases/v*-delivery.md\n"
    "must-contain: SHA-256\nmust-not-contain: TODO\n-->\n# vX.Y.Z changelog\n\n"
    "<!-- writing notes -->\n\n## New features\n\n## Fixes and improvements\n\n## Upgrade notes\n\n## Known issues (optional)\n"
)
CATALOG = "# Template catalog\n\n- release/notes.md\n"


def codes(findings):
    return sorted(f.code for f in findings)


class TemplatesTest(unittest.TestCase):
    def repo(self, files, catalog=CATALOG):
        tree = {"docs/handbook/templates/release/notes.md": NOTES, "docs/handbook/templates/README.md": catalog}
        tree.update(files)
        tmp, root = make_repo(tree)
        self.addCleanup(tmp.cleanup)
        return root

    def test_numbering_extra_and_optional_sections(self):
        doc = "# v1.0.0 changelog\n\n## 1. New features\n\n## 2. Fixes and improvements\n\n## Notes specific to this version\n\n## 3. Upgrade notes\n\nSHA-256\n"
        root = self.repo({"docs/releases/v1.0.0.md": doc})
        self.assertEqual(templates.check_templates(root, {}), [])

    def test_missing_order_and_fenced_heading(self):
        # 正文提到 gen-views 命令的文档照样检查（只按路径跳过生成视图，不能因正文提到命令就整份漏检）
        doc = "# v\n\nSee `python3 scripts/doc-lint.py gen-views`.\n\n```\n## Fixes and improvements\n```\n\n## Upgrade notes\n\n## New features\n\nSHA-256\n"
        findings = templates.check_templates(self.repo({"docs/releases/v1.0.0.md": doc}), {})
        self.assertEqual(codes(findings), ["TEMPLATE-CONFORM"])
        self.assertIn("missing section \"Fixes and improvements\"", findings[0].message)
        self.assertIn("section \"Upgrade notes\" is out of order", findings[0].message)

    def test_tokens_ignore_comments(self):
        doc = "# v\n\n## New features\n\nTODO\n\n## Fixes and improvements\n\n## Upgrade notes\n\n<!-- SHA-256 -->\n"
        message = templates.check_templates(self.repo({"docs/releases/v1.0.0.md": doc}), {})[0].message
        self.assertIn("missing required text \"SHA-256\"", message)
        self.assertIn("contains forbidden text \"TODO\"", message)

    def test_except_readme_and_none(self):
        root = self.repo({"docs/releases/v1.0.0-delivery.md": "# d\n", "docs/releases/README.md": "# r\n"})
        got = sorted((f.level, f.code, f.path) for f in templates.check_templates(root, {}))
        self.assertEqual(got, [
            ("WARN", "TEMPLATE-NONE", "docs/releases/README.md"),
            ("WARN", "TEMPLATE-NONE", "docs/releases/v1.0.0-delivery.md"),
        ])

    def test_header_catalog_leftover_ambiguous(self):
        root = self.repo({
            "docs/handbook/templates/release/bad.md": "# 没有头注释\n",
            "docs/handbook/templates/release/dup.md": "<!-- template\napplies-to: docs/releases/v1.0.0.md\n-->\n# x\n",
            "docs/releases/v1.0.0.md": "<!-- template\n-->\n# v\n",
        }, catalog="- release/notes.md\n- release/dup.md\n")
        self.assertEqual(codes(templates.check_templates(root, {})),
                         ["TEMPLATE-AMBIGUOUS", "TEMPLATE-CATALOG", "TEMPLATE-HEADER", "TEMPLATE-LEFTOVER"])

    def test_adoption_exceptions_frozen_and_bundle_root(self):
        requirements = "<!-- template\napplies-to: {bundle_root}/*/requirements.md\n-->\n# Requirements\n\n## Background\n"
        root = self.repo({
            "docs/handbook/templates/plan/requirements.md": requirements,
            "docs/plans/changes/20300101-d001-x/requirements.md": "# x\n",
            "docs/plans/changes/20300101-d002-y/requirements.md": "# y\n",
            "docs/plans/changes/20300101-d003-z/field-contract.md": "# 白名单外存量\n",
            "docs/handbook/templates/singleton/dir-readme.md": "<!-- template\napplies-to: docs/**/README.md\n-->\n# d\n\n## Navigation\n",
            "docs/plans/legacy/README.md": "# frozen, not checked\n",
            "docs/releases/v1.0.0.md": "# v\n\n## New features\n\n## Fixes and improvements\n\n## Upgrade notes\n\nSHA-256\n",
        }, catalog="- release/notes.md\n- plan/requirements.md\n- singleton/dir-readme.md\n")
        baseline = {
            "bundle_root": "docs/plans/changes",
            "frozen_dirs": ["docs/plans/legacy"],
            "bundle_file_exceptions": ["20300101-d003-z/field-contract.md"],
            "template_exceptions": ["docs/plans/changes/20300101-d001-x/requirements.md"],
        }
        got = [(f.code, f.path) for f in templates.check_templates(root, baseline)]
        self.assertEqual(got, [("TEMPLATE-CONFORM", "docs/plans/changes/20300101-d002-y/requirements.md")])


if __name__ == "__main__":
    unittest.main()
