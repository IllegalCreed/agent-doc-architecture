#!/usr/bin/env python3
"""博客稿件检查：脱敏、篇幅、必备章节、数字出处；--repo 对全仓已跟踪文件与提交说明做脱敏扫描。"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CODE_FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
CJK_RE = re.compile(r"[一-鿿]")
LATIN_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-_.'][A-Za-z0-9]+)*")
IPV4_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
PORT_RE = re.compile(r"(?<![\d:]):\d{4,5}\b")
# --repo 模式只认 host:port 形态，避免把「文件:行号」误报成端口
HOST_PORT_RE = re.compile(r"(?:\blocalhost|https?://[^\s/:]+):\d{2,5}\b")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
REQUIRED_HEADINGS = ("会怎么坏", "小结")
MIN_WORDS, MAX_WORDS = 5000, 6500
DEFAULT_BANNED = Path("local/banned-terms.txt")
# 提交署名里的公开邮箱，不算敏感信息
ALLOWED_EMAILS = ("noreply@anthropic.com",)
# 加载词表的检查脚本自身不扫
REPO_SCAN_EXCLUDE = ("scripts/check-post.py",)


def strip_code(text: str) -> str:
    return CODE_FENCE_RE.sub("", text)


def count_words(text: str) -> int:
    body = strip_code(text)
    return len(CJK_RE.findall(body)) + len(LATIN_WORD_RE.findall(body))


def find_sensitive(
    text: str,
    banned: list[str],
    port_re: re.Pattern[str] = PORT_RE,
    allowed_emails: tuple[str, ...] = (),
) -> list[str]:
    hits: list[str] = []
    lower = text.lower()
    for term in banned:
        if term and term.lower() in lower:
            hits.append(f"banned term: {term}")
    hits.extend(f"ipv4: {m.group(0)}" for m in IPV4_RE.finditer(text))
    hits.extend(f"port: {m.group(0)}" for m in port_re.finditer(text))
    hits.extend(
        f"email: {m.group(0)}" for m in EMAIL_RE.finditer(text) if m.group(0).lower() not in allowed_emails
    )
    return hits


def missing_headings(text: str) -> list[str]:
    heads = [line for line in text.splitlines() if line.startswith("#")]
    return [key for key in REQUIRED_HEADINGS if not any(key in h for h in heads)]


def has_role_column(text: str) -> bool:
    return any(line.startswith("|") and "人的角色" in line for line in text.splitlines())


def _in_text(token: str, text: str) -> bool:
    """按数字边界匹配：999 不因素材库里有 1999 而算有出处。"""
    return re.search(rf"(?<!\d){re.escape(token)}(?!\d)", text) is not None


def unsourced_numbers(text: str, spec_text: str) -> list[str]:
    found: set[str] = set()
    for match in NUMBER_RE.finditer(strip_code(text)):
        token = match.group(0).rstrip(".,")
        if len(token.replace(",", "").replace(".", "")) < 3:
            continue
        if not _in_text(token, spec_text) and not _in_text(token.replace(",", ""), spec_text):
            found.add(token)
    return sorted(found)


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["git", "-C", str(root), *args]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=check)


def scan_repo(root: Path, banned: list[str]) -> list[str]:
    """扫描 git ls-files 列出的全部文本文件 + HEAD 历史的全部提交说明。"""
    hits: list[str] = []
    check = {"port_re": HOST_PORT_RE, "allowed_emails": ALLOWED_EMAILS}
    for rel in filter(None, _git(root, "ls-files", "-z").stdout.split("\0")):
        if rel in REPO_SCAN_EXCLUDE:
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue  # 二进制或工作区已删除
        hits += [f"{rel}: {h}" for h in find_sensitive(text, banned, **check)]
    if _git(root, "rev-parse", "-q", "--verify", "HEAD", check=False).returncode != 0:
        return hits  # 还没有提交
    for entry in _git(root, "log", "--format=%h%x00%B%x1e").stdout.split("\x1e"):
        sha, _, body = entry.strip().partition("\0")
        if sha:
            hits += [f"commit {sha}: {h}" for h in find_sensitive(body, banned, **check)]
    return hits


def load_banned(path: Path) -> list[str]:
    if not path.exists():
        print(f"WARN: {path} 不存在，只做内置模式检查", file=sys.stderr)
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("posts", nargs="*", type=Path)
    parser.add_argument("--spec", type=Path, default=Path("specs/2026-10-14-blog-series-design.md"))
    parser.add_argument("--banned", type=Path, default=None, help=f"默认 <root>/{DEFAULT_BANNED}")
    parser.add_argument("--repo", action="store_true", help="全仓脱敏扫描：已跟踪文件 + 提交说明")
    parser.add_argument("--root", type=Path, default=Path("."), help="--repo 模式的仓库根目录")
    args = parser.parse_args(argv)
    if not args.repo and not args.posts:
        parser.error("需要稿件路径，或使用 --repo")

    banned = load_banned(args.banned or args.root / DEFAULT_BANNED)
    hits: list[str] = []
    if args.repo:
        try:
            hits = scan_repo(args.root, banned)
        except subprocess.CalledProcessError as exc:
            print(f"FAIL repo: git 执行失败：{exc.stderr.strip()}")
            return 1
        for hit in hits:
            print(f"FAIL {hit}")
        print(f"{'FAIL' if hits else 'OK  '} repo: {len(hits)} 处命中")
        if not args.posts:
            return 1 if hits else 0
    spec_text = args.spec.read_text(encoding="utf-8")
    failed = False
    for post in args.posts:
        text = post.read_text(encoding="utf-8")
        errors = find_sensitive(text, banned)
        words = count_words(text)
        if not MIN_WORDS <= words <= MAX_WORDS:
            errors.append(f"字数 {words} 不在 [{MIN_WORDS}, {MAX_WORDS}]")
        errors += [f"缺少章节：{h}" for h in missing_headings(text)]
        if not has_role_column(text):
            errors.append("缺少含「人的角色」列的对照表")
        for token in unsourced_numbers(text, spec_text):
            print(f"WARN {post}: 数字 {token} 不在素材库，人工确认出处")
        for error in errors:
            print(f"FAIL {post}: {error}")
        if errors:
            failed = True
        else:
            print(f"OK   {post}: {words} 字")
    return 1 if failed or hits else 0


if __name__ == "__main__":
    sys.exit(main())
