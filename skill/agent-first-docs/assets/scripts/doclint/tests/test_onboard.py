import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from doclint import cases, cli, onboard
from doclint.tests.fixtures import INDEX_HEAD, index_row, make_repo, meta

SCRIPTS = Path(__file__).resolve().parents[2]
CASE_HEADER = (
    "| Case ID | 标题 | 所属功能 / 模块 | Owner Plan | 层级 | 自动化路径 | 状态 | 最后验证 | 备注 |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)
REQUIREMENTS_TEMPLATE = "<!-- template\napplies-to: {bundle_root}/*/requirements.md\n-->\n# 需求\n\n## 背景\n"
TODAY = "20300102"
NO_BACKGROUND = meta("D-20260101-001", "draft", "docs").replace("## 背景", "## 其他")


def case_row(cid):
    return f"| {cid} | 甲 | BILLING | F-1 | L1 | `a.py` | active | 2026-10-01 | - |\n"


def legacy_files(bundle_dir="docs/plans/changes"):
    """一个接入中途的存量仓库：每类可豁免的违规各一处。"""
    link_prefix = "changes/" if bundle_dir.endswith("changes") else ""
    return {
        "docs/plans/index.md": INDEX_HEAD
        + index_row("D-20260101-001", "docs", "甲", "draft", "-", f"[r]({link_prefix}20260101-d001-a/requirements.md)"),
        f"{bundle_dir}/20260101-d001-a/requirements.md": meta("D-20260101-001", "draft", "docs") + "\n",
        f"{bundle_dir}/20260101-d001-a/run.sh": "echo\n",
        "docs/testing/cases/index.md": "# 全局测试用例索引\n\n## 索引\n\n" + CASE_HEADER
        + case_row("TC-BILLING-001") + case_row("LEGACY-A"),
        "docs/reports/坏名.md": "# 报告\n\n[断](missing.md)\n",
        "docs/handbook/templates/README.md": "- plan/requirements.md\n",
        "docs/handbook/templates/plan/requirements.md": REQUIREMENTS_TEMPLATE,
    }


def repo(test, files):
    tmp, root = make_repo(files)
    test.addCleanup(tmp.cleanup)
    if (root / cases.CASES / "index.md").exists():
        cases.gen_views(root)
    return root


def errors(findings):
    return [f for f in findings if f.level == "ERROR"]


class BuildBaselineTest(unittest.TestCase):
    def test_snapshot_makes_lint_clean(self):
        root = repo(self, legacy_files())
        (root / "docs/plans/changes/20260101-d001-a/requirements.md").write_text(NO_BACKGROUND, encoding="utf-8")
        self.assertTrue(errors(cli.run(root, baseline={"bundle_root": "docs/plans/changes"})))
        config, must_fix = onboard.build_baseline(root, {}, frozen=["docs/old"], today=TODAY)
        self.assertEqual(must_fix, [])
        self.assertEqual(config, {
            "bundle_root": "docs/plans/changes",
            "rules_effective_since": TODAY,
            "frozen_dirs": ["docs/old"],
            "broken_links_total": 1,
            "naming_exceptions": ["docs/reports/坏名.md"],
            "bundle_file_exceptions": ["20260101-d001-a/run.sh"],
            "case_id_exceptions": ["LEGACY-A"],
            "template_exceptions": ["docs/plans/changes/20260101-d001-a/requirements.md"],
        })
        self.assertEqual(errors(cli.run(root, baseline=config)), [])

    def test_bundle_root_given_detected_or_omitted(self):
        root = repo(self, legacy_files())
        self.assertEqual(onboard.build_baseline(root, {}, bundle_root="docs/plans", today=TODAY)[0]["bundle_root"], "docs/plans")
        flat = repo(self, legacy_files(bundle_dir="docs/plans"))
        config, must_fix = onboard.build_baseline(flat, {}, today=TODAY)
        self.assertNotIn("bundle_root", config)
        self.assertEqual(must_fix, [])
        self.assertEqual(config["bundle_file_exceptions"], ["20260101-d001-a/run.sh"])

    def test_preserves_project_keys(self):
        files = legacy_files()
        files["docs/p.md"] = "# p\n\n> 继承：[g](g.md)\n"
        files["docs/g.md"] = "# g\n\n> 项目落地：[p](p.md)\n"
        root = repo(self, files)
        existing = {
            "inherit_pairs": [["docs/p.md", "docs/g.md"]],
            "fresh_docs": ["docs/none/*.md"],
            "strict_fresh": ["docs/none/x.md"],
        }
        config, must_fix = onboard.build_baseline(root, existing, today=TODAY)
        self.assertEqual(must_fix, [])
        for key, value in existing.items():
            self.assertEqual(config[key], value)

    def test_structural_errors_are_must_fix(self):
        dup = index_row("D-20260101-001", "docs", "甲", "draft", "-", "x")
        cases_index = "# i\n\n## 索引\n\n" + CASE_HEADER + case_row("TC-BILLING-001")
        scenarios = {
            "PLAN-INDEX-MISSING": {"docs/testing/cases/index.md": cases_index},
            "PLAN-ID-DUP": {"docs/plans/index.md": INDEX_HEAD + dup + dup, "docs/testing/cases/index.md": cases_index},
            "PLAN-INDEX-HEADER": {"docs/plans/index.md": "# i\n\n| Stable ID | 标题 |\n| --- | --- |\n",
                                  "docs/testing/cases/index.md": cases_index},
            "PLAN-STATUS": {"docs/plans/index.md": INDEX_HEAD + index_row("D-20260101-001", "docs", "甲", "done", "-", "x"),
                            "docs/testing/cases/index.md": cases_index},
            "CASE-INDEX-MISSING": {"docs/plans/index.md": INDEX_HEAD},
        }
        for code, files in scenarios.items():
            with self.subTest(code=code):
                self.assertIn(code, onboard.MUST_FIX)
                _, must_fix = onboard.build_baseline(repo(self, files), {}, today=TODAY)
                self.assertEqual([f.code for f in must_fix], [code])

    def test_duplicate_case_id_is_must_fix_even_when_format_exempt(self):
        files = legacy_files()
        files["docs/testing/cases/index.md"] += case_row("LEGACY-A")
        config, must_fix = onboard.build_baseline(repo(self, files), {}, today=TODAY)
        self.assertEqual(config["case_id_exceptions"], ["LEGACY-A"])
        self.assertEqual([(f.code, "重复" in f.message) for f in must_fix], [("CASE-ID", True)])

    def test_every_error_code_is_classified(self):
        source = "".join(p.read_text(encoding="utf-8") for p in (SCRIPTS / "doclint").glob("*.py"))
        found = set(re.findall(r'Finding\(\s*(?:"ERROR"|level),\s*"([A-Z][A-Z-]+)"', source))
        self.assertTrue(found)
        self.assertEqual(found - onboard.MUST_FIX - set(onboard.BASELINABLE), set())
        self.assertEqual(onboard.MUST_FIX & set(onboard.BASELINABLE), set())

    def test_rerun_only_shrinks(self):
        files = legacy_files()
        files["docs/reports/还在.md"] = "# x\n"
        files["docs/reports/新增.md"] = "# x\n"
        root = repo(self, files)
        existing = {
            "rules_effective_since": "20260901",
            "broken_links_total": 5,
            "naming_exceptions": ["docs/reports/还在.md", "docs/reports/已删.md", "docs/reports/坏名.md"],
            "bundle_file_exceptions": ["20260101-d001-a/run.sh"],
            "case_id_exceptions": ["LEGACY-A"],
            "template_exceptions": [],
        }
        config, must_fix = onboard.build_baseline(root, existing, today=TODAY)
        self.assertEqual(config["rules_effective_since"], "20260901")
        self.assertEqual(config["broken_links_total"], 1)
        self.assertEqual(config["naming_exceptions"], ["docs/reports/坏名.md", "docs/reports/还在.md"])
        self.assertEqual([(f.code, f.path) for f in must_fix], [("NAME", "docs/reports/新增.md")])


class InitBaselineCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = make_repo(legacy_files())
        self.addCleanup(self.tmp.cleanup)
        shutil.copytree(SCRIPTS, self.root / "scripts", ignore=shutil.ignore_patterns("tests", "__pycache__", "baseline.json"))
        self.baseline = self.root / "scripts/doclint/baseline.json"

    def lint(self, *args):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts/doc-lint.py"), *args],
            capture_output=True, text=True, encoding="utf-8",
        )

    def test_end_to_end(self):
        self.assertEqual(self.lint("gen-views").returncode, 0)
        before = self.lint()
        self.assertEqual(before.returncode, 1, before.stdout)
        dry = self.lint("init-baseline", "--frozen", "docs/old")
        self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
        self.assertEqual(json.loads(dry.stdout)["naming_exceptions"], ["docs/reports/坏名.md"])
        self.assertFalse(self.baseline.exists())
        wrote = self.lint("init-baseline", "--frozen", "docs/old", "--write")
        self.assertEqual(wrote.returncode, 0, wrote.stdout + wrote.stderr)
        self.assertEqual(json.loads(self.baseline.read_text(encoding="utf-8"))["frozen_dirs"], ["docs/old"])
        after = self.lint()
        self.assertEqual(after.returncode, 0, after.stdout)
        self.assertIn("doc-lint: 0 error(s)", after.stdout)

    def test_must_fix_blocks_write(self):
        (self.root / "docs/plans/index.md").unlink()
        result = self.lint("init-baseline", "--write")
        self.assertEqual(result.returncode, 1)
        self.assertIn("must-fix PLAN-INDEX-MISSING", result.stdout)
        self.assertFalse(self.baseline.exists())


class StaleTest(unittest.TestCase):
    def test_stale_entries(self):
        root = repo(self, legacy_files())
        config, _ = onboard.build_baseline(root, {}, today=TODAY)
        self.assertEqual(onboard.check_baseline_stale(root, config), [])
        (root / "docs/reports/坏名.md").unlink()
        (root / "docs/plans/changes/20260101-d001-a/run.sh").unlink()
        index = root / "docs/testing/cases/index.md"
        index.write_text(index.read_text(encoding="utf-8").replace("LEGACY-A", "TC-BILLING-002"), encoding="utf-8")
        got = sorted((f.level, f.code, f.path) for f in onboard.check_baseline_stale(root, config))
        self.assertEqual(got, [
            ("WARN", "BASELINE-STALE", "docs/plans/changes/20260101-d001-a/run.sh"),
            ("WARN", "BASELINE-STALE", "docs/reports/坏名.md"),
            ("WARN", "BASELINE-STALE", "docs/testing/cases/index.md"),
        ])

    def test_now_conforming_template(self):
        root = repo(self, legacy_files())
        (root / "docs/plans/changes/20260101-d001-a/requirements.md").write_text(NO_BACKGROUND, encoding="utf-8")
        config, _ = onboard.build_baseline(root, {}, today=TODAY)
        self.assertEqual(onboard.check_baseline_stale(root, config), [])
        (root / "docs/plans/changes/20260101-d001-a/requirements.md").write_text(
            meta("D-20260101-001", "draft", "docs"), encoding="utf-8")
        stale = onboard.check_baseline_stale(root, config)
        self.assertEqual([(f.code, f.path) for f in stale],
                         [("BASELINE-STALE", "docs/plans/changes/20260101-d001-a/requirements.md")])
        self.assertIn("template_exceptions", stale[0].message)

    def test_wired_into_run(self):
        root = repo(self, legacy_files())
        config, _ = onboard.build_baseline(root, {}, today=TODAY)
        config["naming_exceptions"].append("docs/reports/不存在.md")
        got = [(f.level, f.code, f.path) for f in cli.run(root, baseline=config) if f.code == "BASELINE-STALE"]
        self.assertEqual(got, [("WARN", "BASELINE-STALE", "docs/reports/不存在.md")])


if __name__ == "__main__":
    unittest.main()
