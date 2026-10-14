import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_post", ROOT / "scripts" / "check-post.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

# 夹具里的 IP / 邮箱 / host:port 在运行时拼出来，免得本文件被 --repo 全仓扫描命中
IP = ".".join(["10", "1", "2", "3"])
MAIL = "a" + "@" + "b.com"
HOST_PORT = "http://" + "box" + ":" + "8080"


class CountWordsTest(unittest.TestCase):
    def test_counts_cjk_and_latin_outside_code(self):
        text = "文档路由 Agent first\n```python\n不计入 this\n```\n"
        self.assertEqual(cp.count_words(text), 4 + 2)


class SensitiveTest(unittest.TestCase):
    def test_banned_term_case_insensitive(self):
        self.assertEqual(cp.find_sensitive("用了 ACME 框架", ["acme"]), ["banned term: acme"])

    def test_ipv4_port_email(self):
        hits = cp.find_sensitive(f"连 {IP} 和 host:12345，mail {MAIL}", [])
        self.assertIn(f"ipv4: {IP}", hits)
        self.assertIn("port: :12345", hits)
        self.assertIn(f"email: {MAIL}", hits)

    def test_time_is_not_port(self):
        self.assertEqual(cp.find_sensitive("09:30 开会", []), [])


class StructureTest(unittest.TestCase):
    def test_missing_headings(self):
        self.assertEqual(cp.missing_headings("# 标题\n## 小结\n"), ["会怎么坏"])

    def test_role_column(self):
        self.assertTrue(cp.has_role_column("| 文档 | 人的角色 |\n|---|---|\n"))
        self.assertFalse(cp.has_role_column("人的角色写在正文里"))


class NumbersTest(unittest.TestCase):
    def test_reports_numbers_absent_from_spec(self):
        spec_text = "提交 3614 次，文档 832 份"
        self.assertEqual(cp.unsourced_numbers("3614 次提交、999 份、12 个", spec_text), ["999"])

    def test_ignores_numbers_in_code(self):
        self.assertEqual(cp.unsourced_numbers("```\n12345\n```", ""), [])

    def test_matches_on_digit_boundaries(self):
        spec_text = "共 1999 份，另有 3730 次、1373 次"
        self.assertEqual(cp.unsourced_numbers("999 份、373 次", spec_text), ["373", "999"])
        self.assertEqual(cp.unsourced_numbers("1373 次、1,373 次", spec_text), [])


class CliTest(unittest.TestCase):
    def test_exit_code_fails_on_short_post(self):
        with tempfile.TemporaryDirectory() as d:
            post = Path(d) / "p.md"
            post.write_text("# 短稿\n## 会怎么坏\n## 小结\n| 人的角色 |\n", encoding="utf-8")
            spec_file = Path(d) / "spec.md"
            spec_file.write_text("", encoding="utf-8")
            code = cp.main([str(post), "--spec", str(spec_file), "--banned", str(Path(d) / "none.txt")])
            self.assertEqual(code, 1)


@unittest.skipUnless(shutil.which("git"), "需要 git")
class RepoScanTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.repo = base / "repo"
        self.repo.mkdir()
        self.banned = base / "banned.txt"
        self.banned.write_text("# 注释行\nacme\n", encoding="utf-8")
        self._git("init", "-q")

    def tearDown(self):
        self._tmp.cleanup()

    def _git(self, *args):
        ident = ["-c", "user.name=t", "-c", "user.email=" + "t" + "@" + "example.invalid"]
        opts = ["-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"]
        subprocess.run(["git", *ident, *opts, *args], cwd=self.repo, check=True, capture_output=True)

    def _write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _commit(self, message, *paths):
        self._git("add", *paths)
        self._git("commit", "-q", "-m", message)

    def _main(self):
        return cp.main(["--repo", "--root", str(self.repo), "--banned", str(self.banned)])

    def test_clean_repo_passes(self):
        self._write("doc.md", "正常内容，见 check-post.py:123，09:30 开会，v2.3.1\n")
        self._commit("init\n\nCo-Authored-By: Claude <noreply@anthropic.com>", "doc.md")
        self.assertEqual(cp.scan_repo(self.repo, ["acme"]), [])
        self.assertEqual(self._main(), 0)

    def test_hits_in_tracked_files_and_commit_messages(self):
        self._write("doc.md", f"用了 ACME 框架\n地址 {HOST_PORT}\n")
        self._write("local/secret.md", "ACME 只在本地\n")  # 未跟踪，不扫
        self._commit(f"init\n\n部署到 {IP}，联系 {MAIL}", "doc.md")
        hits = cp.scan_repo(self.repo, ["acme"])
        self.assertIn("doc.md: banned term: acme", hits)
        self.assertIn(f"doc.md: port: {HOST_PORT}", hits)
        self.assertTrue(any(h.startswith("commit ") and h.endswith(f"ipv4: {IP}") for h in hits))
        self.assertTrue(any(h.startswith("commit ") and h.endswith(f"email: {MAIL}") for h in hits))
        self.assertFalse(any("local/" in h for h in hits))
        self.assertEqual(self._main(), 1)

    def test_not_a_repo_fails_loudly(self):
        with tempfile.TemporaryDirectory() as d:
            code = cp.main(["--repo", "--root", d, "--banned", str(self.banned)])
        self.assertEqual(code, 1)

    def test_skips_checker_itself(self):
        self._write(cp.REPO_SCAN_EXCLUDE[0], "acme\n")
        self._commit("add checker", cp.REPO_SCAN_EXCLUDE[0])
        self.assertEqual(cp.scan_repo(self.repo, ["acme"]), [])


if __name__ == "__main__":
    unittest.main()
