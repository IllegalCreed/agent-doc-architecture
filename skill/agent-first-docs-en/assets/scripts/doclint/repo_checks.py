"""仓库级检查：断链、命名、继承、新鲜度、取号。"""

from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

from . import vocab
from .model import Finding, last_reviewed, md_links

ENTRY_PATHS = (
    "AGENTS.md", "docs/README.md", "docs/handbook", "docs/testing",
    "docs/plans/README.md", "docs/plans/index.md", "docs/reports/README.md",
)
TOTAL_PATHS = ("docs", "AGENTS.md")
STRICT_FRESH = ("docs/overview.md", "docs/roadmap.md")
DEFAULT_FRESH_DOCS = (
    "docs/overview.md", "docs/roadmap.md", "docs/deployment/README.md",
    "docs/handbook/**/*.md", "docs/testing/guides/*.md",
)
CHECKER = Path(__file__).resolve().parents[1] / "check-doc-links.py"


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""


def link_checker():
    spec = importlib.util.spec_from_file_location("check_doc_links", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _broken(checker, root: Path, paths: tuple[str, ...]) -> list[str]:
    existing = [Path(p) for p in paths if (root / p).exists()]
    return checker.check(root, existing) if existing else []


def broken_links_total(root: Path) -> int:
    """全库（docs + AGENTS.md）断链数，即接入配置 broken_links_total 的口径。"""
    return len(_broken(link_checker(), root.resolve(), TOTAL_PATHS))


def check_links(root: Path, baseline: dict) -> list[Finding]:
    root = root.resolve()
    checker = link_checker()
    findings = [Finding("ERROR", "LINK-ENTRY", item.split(":", 1)[0], item) for item in _broken(checker, root, ENTRY_PATHS)]
    total = broken_links_total(root)
    limit = baseline.get("broken_links_total", 0)
    if total > limit:
        findings.append(Finding("ERROR", "LINK-BASELINE", "docs", f"broken links across the repo: {total}, above the baseline {limit}"))
    elif total < limit:
        findings.append(Finding("INFO", "LINK-BASELINE", "docs", f"broken links across the repo: {total}, below the baseline {limit}; lower scripts/doclint/baseline.json"))
    return findings


def naming_violations(root: Path) -> list[str]:
    bad: list[str] = []
    for base in vocab.NAMING_DIRS:
        directory = root / base
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            if path.name == "README.md":
                continue
            ok = vocab.NAMING_RE.match(path.name) or (
                base == "docs/releases" and vocab.RELEASE_NAMING_RE.match(path.name)
            )
            if not ok:
                bad.append(path.relative_to(root).as_posix())
    return bad


def check_naming(root: Path, baseline: dict) -> list[Finding]:
    exceptions = set(baseline.get("naming_exceptions", []))
    return [
        Finding("ERROR", "NAME", rel, "record files must be named YYYYMMDD-<english-slug>.md (put the title in the H1)")
        for rel in naming_violations(root) if rel not in exceptions
    ]


def _declared(root: Path, rel: str, marker: str, limit: int) -> set[str]:
    path = root / rel
    targets: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines()[:limit]:
        if marker not in line:
            continue
        for link in md_links(line):
            resolved = (path.parent / unquote(link.split("#")[0])).resolve()
            try:
                targets.add(resolved.relative_to(root.resolve()).as_posix())
            except ValueError:
                pass
    return targets


def check_inheritance(root: Path, pairs) -> list[Finding]:
    findings: list[Finding] = []
    for project, general in pairs:
        if not (root / project).exists() or not (root / general).exists():
            findings.append(Finding("ERROR", "INHERIT", project, f"inheritance pair is missing a file: {project} ↔ {general}"))
            continue
        if general not in _declared(root, project, vocab.INHERIT_MARKER, 15):
            findings.append(Finding("ERROR", "INHERIT", project, f"the first 15 lines lack a \"> {vocab.INHERIT_MARKER}\" link to {general}"))
        if project not in _declared(root, general, vocab.LANDING_MARKER, 20):
            findings.append(Finding("ERROR", "INHERIT", general, f"the first 20 lines lack a \"> {vocab.LANDING_MARKER}\" link to {project}"))
    return findings


def _glob_regex(pattern: str) -> re.Pattern:
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(out + r"\Z")


def current_fact_docs(root: Path, baseline: dict | None = None) -> list[Path]:
    patterns = (baseline or {}).get("fresh_docs", DEFAULT_FRESH_DOCS)
    regexes = [_glob_regex(p) for p in patterns]
    bases = {root / "/".join(re.split(r"[*]", p)[0].split("/")[:-1]) for p in patterns}
    candidates: set[Path] = set()
    for base in bases:
        if base.is_dir():
            candidates.update(base.rglob("*.md"))
        elif base.with_suffix(".md").is_file():
            candidates.add(base.with_suffix(".md"))
    for pattern in patterns:
        if "*" not in pattern and (root / pattern).is_file():
            candidates.add(root / pattern)
    found: list[Path] = []
    for path in sorted(candidates):
        posix = path.relative_to(root).as_posix()
        if posix.startswith("docs/handbook/") and "templates" in posix.split("/"):
            continue
        if any(r.match(posix) for r in regexes):
            found.append(path)
    return found


def latest_tag_date(root: Path) -> str | None:
    out = _git(root, "for-each-ref", "--sort=-creatordate", "--count=1", "--format=%(creatordate:short)", "refs/tags")
    return out.strip() or None


def roadmap_banner_blocks(text: str) -> int:
    blocks = 0
    previous_quote = False
    for line in text.splitlines():
        if line.startswith("## "):
            break
        if line.startswith("> 20") and not previous_quote:
            blocks += 1
        previous_quote = line.startswith(">")
    return blocks


def check_freshness(root: Path, release: bool, tag_date: str | None, baseline: dict | None = None) -> list[Finding]:
    findings: list[Finding] = []
    strict = set((baseline or {}).get("strict_fresh", STRICT_FRESH))
    if release and tag_date is None:
        findings.append(Finding("INFO", "FRESH-NOTAG", "-", "the repo has no tag, so Last reviewed cannot be compared with the latest release; tag before the release seal, or the staleness check does not run"))
    for path in current_fact_docs(root, baseline):
        rel = path.relative_to(root).as_posix()
        reviewed = last_reviewed(path.read_text(encoding="utf-8"))
        if reviewed is None:
            findings.append(Finding("ERROR", "FRESH-MISSING", rel, "the first 15 lines lack \"Last reviewed: YYYY-MM-DD\""))
        elif tag_date and reviewed < tag_date:
            level = "ERROR" if release and rel in strict else "WARN"
            findings.append(Finding(level, "FRESH-STALE", rel, f"Last reviewed {reviewed} is earlier than the latest release {tag_date}"))
    roadmap = root / "docs/roadmap.md"
    if roadmap.exists():
        blocks = roadmap_banner_blocks(roadmap.read_text(encoding="utf-8"))
        if blocks > vocab.ROADMAP_BANNER_MAX:
            findings.append(Finding(
                "ERROR", "ROADMAP-BANNERS", "docs/roadmap.md",
                f"{blocks} date banners at the top; the maximum is {vocab.ROADMAP_BANNER_MAX}",
            ))
    return findings


def occupied_numbers(root: Path, date: str, letter: str, base: str) -> set[int]:
    pattern = re.compile(rf"^{date}-{letter.lower()}(\d{{3}})-")
    numbers: set[int] = set()

    def collect(names) -> None:
        for name in names:
            match = pattern.match(name)
            if match:
                numbers.add(int(match.group(1)))

    for ref in _git(root, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes").split():
        collect(_git(root, "ls-tree", "-d", "--name-only", f"{ref}:{base}").split())
    worktrees = [
        line[len("worktree "):]
        for line in _git(root, "worktree", "list", "--porcelain").splitlines()
        if line.startswith("worktree ")
    ]
    for tree in {str(root), *worktrees}:
        directory = Path(tree) / base
        if directory.is_dir():
            collect(p.name for p in directory.iterdir())
    index = root / "docs/plans/index.md"
    if index.exists():
        found = re.findall(rf"{letter.upper()}-{date}-(\d{{3}})", index.read_text(encoding="utf-8"))
        numbers |= {int(n) for n in found}
    return numbers


def next_id(root: Path, typ: str, date: str, base: str = "docs/plans") -> tuple[str, str]:
    """base 为 bundle 根目录（plans.bundle_root）；返回 (Stable ID, bundle 目录路径模板)。"""
    letter = vocab.PLAN_TYPES[typ]
    taken = occupied_numbers(root, date, letter, base)
    number = 1
    while number in taken:
        number += 1
    return f"{letter}-{date}-{number:03d}", f"{base}/{date}-{letter.lower()}{number:03d}-<slug>"
