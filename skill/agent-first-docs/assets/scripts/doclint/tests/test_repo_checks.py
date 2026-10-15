import subprocess
import unittest

from doclint import repo_checks
from doclint.tests.fixtures import make_repo


class LinksTest(unittest.TestCase):
    def test_entry_and_baseline(self):
        tmp, root = make_repo({
            "docs/README.md": "[坏](missing.md)\n",
            "docs/reports/a.md": "[坏](nope.md)\n",
            "docs/reports/b.md": "```markdown\n[示例](nope.md)\n```\n\n行内 `[示例](nope.md)` 不算\n",
        })
        self.addCleanup(tmp.cleanup)
        over = repo_checks.check_links(root, {"broken_links_total": 1})
        self.assertEqual([(f.level, f.code) for f in over], [("ERROR", "LINK-ENTRY"), ("ERROR", "LINK-BASELINE")])
        under = repo_checks.check_links(root, {"broken_links_total": 3})
        self.assertEqual([(f.level, f.code) for f in under], [("ERROR", "LINK-ENTRY"), ("INFO", "LINK-BASELINE")])


class NamingTest(unittest.TestCase):
    def test_naming(self):
        tmp, root = make_repo({
            "docs/reports/坏名.md": "x",
            "docs/reports/20261014-ok.md": "x",
            "docs/reports/README.md": "x",
            "docs/releases/v1.2.3-delivery.md": "x",
            "docs/testing/guides/x.md": "x",
            "docs/testing/infrastructure/Bad.md": "x",
        })
        self.addCleanup(tmp.cleanup)
        bad = ["docs/reports/坏名.md", "docs/testing/infrastructure/Bad.md"]
        self.assertEqual([f.path for f in repo_checks.check_naming(root, {})], bad)
        self.assertEqual(repo_checks.check_naming(root, {"naming_exceptions": bad}), [])


class InheritanceTest(unittest.TestCase):
    def test_pairs(self):
        tmp, root = make_repo({"docs/p.md": "# 项目\n\n> 继承：[通用](g.md)\n", "docs/g.md": "# 通用\n"})
        self.addCleanup(tmp.cleanup)
        pairs = (("docs/p.md", "docs/g.md"),)
        self.assertEqual([(f.code, f.path) for f in repo_checks.check_inheritance(root, pairs)], [("INHERIT", "docs/g.md")])
        (root / "docs/g.md").write_text("# 通用\n\n> 项目落地：[项目](p.md)\n", encoding="utf-8")
        self.assertEqual(repo_checks.check_inheritance(root, pairs), [])


    def test_greenfield_no_pairs(self):
        tmp, root = make_repo({"docs/x.md": "x"})
        self.addCleanup(tmp.cleanup)
        self.assertEqual(repo_checks.check_inheritance(root, []), [])


class FreshnessTest(unittest.TestCase):
    def test_fresh_override(self):
        tmp, root = make_repo({
            "docs/overview.md": "# 概览\n",
            "docs/handbook/a.md": "# a\n\n> Last reviewed: 2026-09-01\n",
            "docs/extra/b.md": "# b\n\n> Last reviewed: 2026-09-01\n",
            "docs/extra/sub/c.md": "# c\n",
        })
        self.addCleanup(tmp.cleanup)
        cfg = {"fresh_docs": ["docs/extra/*.md"]}
        found = repo_checks.check_freshness(root, False, "2026-10-10", cfg)
        self.assertEqual([(f.level, f.code, f.path) for f in found], [("WARN", "FRESH-STALE", "docs/extra/b.md")])
        cfg = {"fresh_docs": ["docs/extra/**/*.md"], "strict_fresh": ["docs/extra/b.md"]}
        found = repo_checks.check_freshness(root, True, "2026-10-10", cfg)
        self.assertEqual(sorted((f.level, f.code, f.path) for f in found), [
            ("ERROR", "FRESH-MISSING", "docs/extra/sub/c.md"),
            ("ERROR", "FRESH-STALE", "docs/extra/b.md"),
        ])

    def test_freshness(self):
        banners = "".join(f"> 2026-10-0{i}：动态\n\n" for i in range(1, 7))
        tmp, root = make_repo({
            "docs/overview.md": "# 概览\n",
            "docs/roadmap.md": f"# 路线图\n\n> Last reviewed: 2026-09-01\n\n{banners}## 阶段\n\n> 2026-01-01：正文引用不算\n",
            "docs/handbook/a.md": "# a\n\n> Last reviewed: 2026-10-12\n",
            "docs/handbook/templates/t.md": "# 模板\n",
        })
        self.addCleanup(tmp.cleanup)
        normal = repo_checks.check_freshness(root, False, "2026-10-10")
        self.assertEqual(sorted((f.level, f.code, f.path) for f in normal), [
            ("ERROR", "FRESH-MISSING", "docs/overview.md"),
            ("ERROR", "ROADMAP-BANNERS", "docs/roadmap.md"),
            ("WARN", "FRESH-STALE", "docs/roadmap.md"),
        ])
        release = repo_checks.check_freshness(root, True, "2026-10-10")
        self.assertIn(("ERROR", "FRESH-STALE", "docs/roadmap.md"), [(f.level, f.code, f.path) for f in release])


class NextIdTest(unittest.TestCase):
    def test_scans_branches_and_worktree(self):
        tmp, root = make_repo({"docs/plans/20261014-d001-a/requirements.md": "x"})
        self.addCleanup(tmp.cleanup)

        def git(*args):
            subprocess.run(
                ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t",
                 "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args],
                check=True, capture_output=True,
            )

        git("init", "-q")
        git("checkout", "-q", "-b", "main")
        git("commit", "-q", "--allow-empty", "-m", "init")
        git("checkout", "-q", "-b", "b1")
        git("add", "docs")
        git("commit", "-q", "-m", "b1")
        git("checkout", "-q", "main")
        self.assertFalse((root / "docs/plans/20261014-d001-a").exists())
        (root / "docs/plans/20261014-d002-b").mkdir(parents=True)
        self.assertEqual(repo_checks.next_id(root, "docs", "20261014")[0], "D-20261014-003")
        self.assertEqual(repo_checks.next_id(root, "bugfix", "20261014")[0], "B-20261014-001")
        self.assertEqual(repo_checks.next_id(root, "docs", "20261014")[1], "docs/plans/20261014-d003-<slug>")


if __name__ == "__main__":
    unittest.main()
