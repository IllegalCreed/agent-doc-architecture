import unittest

from doclint import plans
from doclint.tests.fixtures import INDEX_HEAD, index_row, make_repo, meta


def codes(findings):
    return sorted(f.code for f in findings)


class CheckIndexTest(unittest.TestCase):
    def run_index(self, body):
        tmp, root = make_repo({"docs/plans/index.md": body})
        self.addCleanup(tmp.cleanup)
        return plans.check_index(root)

    def test_wrong_header(self):
        body = (
            "| Stable ID | Type | 标题 | 状态 | 进度 | 阻塞项 | 下一步 | Plan |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        )
        self.assertEqual(codes(self.run_index(body)), ["PLAN-INDEX-HEADER"])

    def test_banner(self):
        findings = self.run_index("> 2026-10-10：已封板\n\n" + INDEX_HEAD)
        self.assertEqual([(f.code, f.path) for f in findings], [("PLAN-INDEX-BANNER", "docs/plans/index.md:1")])

    def test_preamble(self):
        fat = INDEX_HEAD.replace("# 变更计划索引\n\n", "# 变更计划索引\n\n> 说明\n\n当前推进：v9 已封板\n\n")
        self.assertEqual(codes(self.run_index(fat)), ["PLAN-INDEX-PREAMBLE"])
        thin = INDEX_HEAD.replace("# 变更计划索引\n\n", "# 变更计划索引\n\n> 说明\n\n")
        self.assertEqual(self.run_index(thin), [])

    def test_duplicate_id(self):
        row = index_row("F-20260909-005", "feature", "甲", "verified", "-", "x")
        findings = self.run_index(INDEX_HEAD + row + row)
        self.assertEqual([(f.code, f.path) for f in findings], [("PLAN-ID-DUP", "docs/plans/index.md:6")])

    def test_vocab(self):
        row = index_row("B-20260901-001", "bug", "甲", "completed", "-", "x")
        self.assertEqual(codes(self.run_index(INDEX_HEAD + row)), ["PLAN-STATUS", "PLAN-TYPE"])

    def test_length_limits(self):
        ok = index_row("B-20260901-001", "bugfix", "甲" * 50, "approved", "乙" * 80, "x")
        bad = index_row("B-20260901-002", "bugfix", "甲" * 51, "approved", "乙" * 81, "x")
        self.assertEqual(self.run_index(INDEX_HEAD + ok), [])
        self.assertEqual(codes(self.run_index(INDEX_HEAD + bad)), ["PLAN-NEXT-LEN", "PLAN-TITLE-LEN"])

    def test_missing_index(self):
        tmp, root = make_repo({"docs/plans/.keep": ""})
        self.addCleanup(tmp.cleanup)
        self.assertEqual(codes(plans.check_index(root)), ["PLAN-INDEX-MISSING"])

    def test_row_columns(self):
        short = "| B-20260901-001 | bugfix | 甲 | approved | x |\n"
        good = index_row("B-20260901-002", "bugfix", "乙", "approved", "-", "x")
        tmp, root = make_repo({"docs/plans/index.md": INDEX_HEAD + short + good})
        self.addCleanup(tmp.cleanup)
        self.assertEqual(codes(plans.check_index(root)), ["PLAN-ROW-COLUMNS"])
        self.assertEqual(plans.check_bundles(root, {}), [])


class CheckBundlesTest(unittest.TestCase):
    def run_bundles(self, files, baseline=None):
        tmp, root = make_repo(files)
        self.addCleanup(tmp.cleanup)
        return plans.check_bundles(root, baseline or {})

    def registered(self, dirname, sid, typ="docs", status="draft", extra=None):
        files = {
            "docs/plans/index.md": INDEX_HEAD
            + index_row(sid, typ, "甲", status, "-", f"[requirements]({dirname}/requirements.md)"),
            f"docs/plans/{dirname}/requirements.md": meta(sid, status, typ),
        }
        files.update(extra or {})
        return files

    def test_missing_index_skips_bundle_checks(self):
        files = {"docs/plans/archive/old.md": "# x\n", "docs/plans/20261014-d001-x/requirements.md": "# x\n"}
        self.assertEqual(self.run_bundles(files), [])

    def test_missing_bundle_root(self):
        files = {"docs/plans/index.md": INDEX_HEAD}
        self.assertEqual(self.run_bundles(files, {"bundle_root": "docs/plans/changes"}), [])

    def test_clean_bundle(self):
        self.assertEqual(self.run_bundles(self.registered("20261014-d001-x", "D-20261014-001")), [])

    def test_bad_dir_name(self):
        files = self.registered(
            "20261014-d001-x", "D-20261014-001", extra={"docs/plans/2026-bad/requirements.md": "# x\n"}
        )
        self.assertEqual(codes(self.run_bundles(files)), ["BUNDLE-NAME"])

    def test_unregistered(self):
        files = {
            "docs/plans/index.md": INDEX_HEAD,
            "docs/plans/20261014-d001-x/requirements.md": meta("D-20261014-001", "draft", "docs"),
        }
        self.assertEqual(codes(self.run_bundles(files)), ["BUNDLE-UNREGISTERED"])

    def test_missing_meta(self):
        files = self.registered("20261014-d001-x", "D-20261014-001")
        files["docs/plans/20261014-d001-x/requirements.md"] = "# x\n\n> Status: draft\n\n## 背景\n"
        findings = self.run_bundles(files)
        self.assertEqual(codes(findings), ["BUNDLE-META-MISSING"])
        self.assertIn("Stable ID", findings[0].message)

    def test_meta_mismatch(self):
        files = self.registered("20261014-d001-x", "D-20261014-001", status="approved")
        files["docs/plans/20261014-d001-x/requirements.md"] = meta("D-20261014-001", "draft", "docs")
        self.assertEqual(codes(self.run_bundles(files)), ["BUNDLE-META-MISMATCH"])

    def test_id_letter(self):
        new = self.registered("20261014-f001-x", "F-20261014-001", typ="docs")
        old = self.registered("20260901-f001-y", "F-20260901-001", typ="bugfix")
        adoption = {"rules_effective_since": "20261014"}
        self.assertEqual(codes(self.run_bundles(new, adoption)), ["BUNDLE-ID-LETTER"])
        self.assertEqual(self.run_bundles(old, adoption), [])
        self.assertEqual(codes(self.run_bundles(old)), ["BUNDLE-ID-LETTER"])  # 新项目无生效日期，全部严格

    def test_file_whitelist(self):
        base = "docs/plans/20261014-d001-x/"
        files = self.registered("20261014-d001-x", "D-20261014-001", extra={
            base + "notes.md": "x",
            base + "run.mjs": "x",
            base + "handoff.md": "x",
            base + "stage2-storage.md": "x",
            base + "review-peer-20261013.md": "x",
            base + ".DS_Store": "x",
        })
        findings = self.run_bundles(files, {"bundle_file_exceptions": ["20261014-d001-x/run.mjs"]})
        self.assertEqual([(f.code, f.path.rsplit("/", 1)[1]) for f in findings], [("BUNDLE-FILE", "notes.md")])

    def test_record_required(self):
        base = "docs/plans/20261014-d001-x/"
        standard = self.registered("20261014-d001-x", "D-20261014-001", status="implemented",
                                   extra={base + "design.md": "x"})
        light = self.registered("20261014-d001-x", "D-20261014-001", status="verified")
        light_ok = self.registered("20261014-d001-x", "D-20261014-001", status="verified")
        light_ok[base + "requirements.md"] += "\n## 实施记录\n\n- 已合并\n"
        draft = self.registered("20261014-d001-x", "D-20261014-001", status="draft",
                                extra={base + "design.md": "x"})
        self.assertEqual(codes(self.run_bundles(standard)), ["BUNDLE-RECORD"])
        self.assertEqual(codes(self.run_bundles(light)), ["BUNDLE-RECORD"])
        self.assertEqual(self.run_bundles(light_ok), [])
        self.assertEqual(self.run_bundles(draft), [])

    def test_tracks_is_not_a_bundle(self):
        files = self.registered("20261014-d001-x", "D-20261014-001",
                                extra={"docs/plans/tracks/refactor/roadmap.md": "# r\n"})
        self.assertEqual(self.run_bundles(files), [])

    def test_adoption_bundle_root(self):
        files = {
            "docs/plans/index.md": INDEX_HEAD
            + index_row("D-20261014-001", "docs", "甲", "draft", "-", "[requirements](changes/20261014-d001-x/requirements.md)"),
            "docs/plans/changes/20261014-d001-x/requirements.md": meta("D-20261014-001", "draft", "docs"),
        }
        self.assertEqual(self.run_bundles(files, {"bundle_root": "docs/plans/changes"}), [])
        self.assertEqual(codes(self.run_bundles(files)), ["BUNDLE-NAME"])  # 默认平铺时 changes/ 不是合法 bundle 名


if __name__ == "__main__":
    unittest.main()
