import io
import unittest
from contextlib import redirect_stdout

from doclint import cases, cli
from doclint.tests.fixtures import make_repo

HEADER = (
    "| Case ID | Title | Feature / module | Owner Plan | Layer | Automation path | Status | Last verified | Notes |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


def case_row(cid, title="甲", module="BILLING / 文件", layer="L1", status="active"):
    return f"| {cid} | {title} | {module} | [F](x) | {layer} | `a.py` | {status} | 2026-10-01 | - |\n"


def index_md(rows, pre=""):
    return f"# Global test-case index\n\n{pre}## How to use\n\nNotes\n\n## Index\n\n### Group\n\n{HEADER}{rows}"


def codes(findings):
    return sorted(f.code for f in findings)


class CasesTest(unittest.TestCase):
    def repo(self, index, views=True):
        tmp, root = make_repo({"docs/testing/cases/index.md": index})
        self.addCleanup(tmp.cleanup)
        if views:
            cases.gen_views(root)
        return root

    def test_clean(self):
        root = self.repo(index_md(case_row("TC-BILLING-001") + case_row("TC-STOCK-V2-002", module="STOCK", layer="L4")))
        self.assertEqual(cases.check_cases(root), [])

    def test_missing_index(self):
        tmp, root = make_repo({"docs/testing/cases/.keep": ""})
        self.addCleanup(tmp.cleanup)
        cases.gen_views(root)
        self.assertEqual(codes(cases.check_cases(root)), ["CASE-INDEX-MISSING"])
        self.assertEqual(cases.main_rows(root), [])

    def test_gen_views_without_index(self):
        tmp, root = make_repo({"docs/README.md": "# d\n"})
        self.addCleanup(tmp.cleanup)
        self.assertFalse(cases.gen_views(root))
        self.assertFalse((root / "docs/testing").exists())
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["--root", str(root), "gen-views"])
        self.assertEqual(code, 1)
        self.assertIn("docs/testing/cases/index.md", out.getvalue())

    def test_short_row(self):
        short = "| TC-BILLING-009 | 甲 | BILLING | [F](x) | L1 |\n"
        root = self.repo(index_md(short + case_row("TC-BILLING-001")))
        self.assertEqual(codes(cases.check_cases(root)), ["CASE-ROW-COLUMNS"])
        for name in ("by-layer.md", "by-module.md"):
            text = (root / "docs/testing/cases" / name).read_text(encoding="utf-8")
            self.assertIn("TC-BILLING-001", text)
            self.assertNotIn("TC-BILLING-009", text)

    def test_row_errors(self):
        rows = (
            case_row("TC-BILLING-001") + case_row("TC-BILLING-001") + case_row("TC-BAD-1")
            + case_row("TC-BILLING-003", layer="L9") + case_row("TC-BILLING-004", status="pending")
        )
        root = self.repo(index_md(rows))
        self.assertEqual(codes(cases.check_cases(root)), ["CASE-ID", "CASE-ID", "CASE-LAYER", "CASE-STATUS"])

    def test_adoption_case_id_exceptions(self):
        root = self.repo(index_md(case_row("LEGACY-A")))
        self.assertEqual(codes(cases.check_cases(root)), ["CASE-ID"])
        self.assertEqual(cases.check_cases(root, {"case_id_exceptions": ["LEGACY-A"]}), [])

    def test_header(self):
        bad = index_md(case_row("TC-BILLING-001")).replace("| Notes |", "| Obsolete / replacement reason |")
        root = self.repo(bad)
        self.assertEqual(codes(cases.check_cases(root)), ["CASE-HEADER"])

    def test_narrative(self):
        root = self.repo(index_md(case_row("TC-BILLING-001"), pre="## 批次\n\n| TC-BILLING-009 | x |\n\n"))
        self.assertEqual(codes(cases.check_cases(root)), ["CASE-NARRATIVE"])

    def test_views_stale_then_generated(self):
        rows = (
            case_row("TC-BILLING-001", module="BILLING / 文件", layer="L2")
            + case_row("TC-STOCK-001", module="STOCK", layer="L1")
            + case_row("TC-BILLING-002", module="BILLING", layer="L1")
        )
        root = self.repo(index_md(rows), views=False)
        (root / "docs/testing/cases/by-layer.md").write_text("旧\n", encoding="utf-8")
        self.assertEqual(codes(cases.check_cases(root)), ["CASE-VIEW-STALE", "CASE-VIEW-STALE"])
        cases.gen_views(root)
        self.assertEqual(cases.check_cases(root), [])
        layer = (root / "docs/testing/cases/by-layer.md").read_text(encoding="utf-8")
        self.assertLess(layer.index("## L1"), layer.index("## L2"))
        self.assertLess(layer.index("TC-STOCK-001"), layer.index("TC-BILLING-002"))
        module = (root / "docs/testing/cases/by-module.md").read_text(encoding="utf-8")
        self.assertEqual([l for l in module.splitlines() if l.startswith("## ")], ["## BILLING", "## STOCK"])
        self.assertIn("TC-BILLING-002", module.split("## STOCK")[0])


if __name__ == "__main__":
    unittest.main()
