"""模板一致性检查：一种文档一个模板，模板头注释声明适用范围与必含字段，模板 H2 即必备章节。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import cases, plans, repo_checks
from .model import Finding

TEMPLATES = "docs/handbook/templates"
HEADER_RE = re.compile(r"\A<!-- template\n(.*?)\n-->\n", re.DOTALL)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
NUMBERING_RE = re.compile(r"^(?:\d+(?:\.\d+)*[.、)]?\s*|[一二三四五六七八九十]+、\s*|§\d+\s*)")
OPTIONAL = "（可选）"
SEPARATOR = "；"
STEADY_SKIP = ("docs/handbook/templates", "docs/reports/archive", "docs/assets")
GENERATED = tuple(f"{cases.CASES}/{name}" for name in cases.VIEWS)


@dataclass
class Template:
    path: str
    patterns: list[str]
    applies: list[re.Pattern]
    excepts: list[re.Pattern]
    sections: list[str]
    must: list[str]
    must_not: list[str]


def glob_re(pattern: str) -> re.Pattern:
    """`*` 不跨目录、`**/` 跨目录、`**` 结尾匹配全部、支持 `[...]` 字符类。"""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        elif pattern[i] == "[":
            end = pattern.index("]", i)
            out, i = out + pattern[i:end + 1], end + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + r"\Z")


def split_field(value: str) -> list[str]:
    return [item.strip() for item in value.split(SEPARATOR) if item.strip()]


def strip_noise(text: str) -> str:
    """去掉 HTML 注释与围栏代码块（复用链接检查器的逐行围栏解析，不另写正则）。"""
    return COMMENT_RE.sub("", repo_checks.link_checker().mask_fences(text))


def headings(text: str) -> list[str]:
    return [NUMBERING_RE.sub("", line[3:].strip()).strip() for line in strip_noise(text).splitlines() if line.startswith("## ")]


def load_templates(root: Path, baseline: dict) -> list[Template]:
    base = plans.bundle_root(baseline)
    directory = root / TEMPLATES
    loaded: list[Template] = []
    if not directory.is_dir():
        return loaded
    for path in sorted(directory.rglob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        match = HEADER_RE.match(text)
        if not match:
            continue
        fields: dict[str, str] = {}
        for line in match.group(1).splitlines():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().replace("{bundle_root}", base)
        patterns = split_field(fields.get("applies-to", ""))
        loaded.append(Template(
            path=path.relative_to(root).as_posix(),
            patterns=patterns,
            applies=[glob_re(p) for p in patterns],
            excepts=[glob_re(p) for p in split_field(fields.get("except", ""))],
            sections=[h for h in headings(text[match.end():]) if not h.endswith(OPTIONAL)],
            must=split_field(fields.get("must-contain", "")),
            must_not=split_field(fields.get("must-not-contain", "")),
        ))
    return loaded


def matches(rel: str, template: Template) -> bool:
    readme = rel.rsplit("/", 1)[-1] == "README.md"
    for pattern, rx in zip(template.patterns, template.applies):
        if readme and not pattern.endswith("README.md"):
            continue
        if rx.match(rel) and not any(e.match(rel) for e in template.excepts):
            return True
    return False


def candidates(root: Path, templates: list[Template]) -> list[Path]:
    files: set[Path] = set()
    for template in templates:
        for pattern in template.patterns:
            static = re.split(r"[*?\[]", pattern, maxsplit=1)[0]
            if static == pattern:
                if (root / pattern).is_file():
                    files.add(root / pattern)
                continue
            base = root / static.rsplit("/", 1)[0]
            if base.is_dir():
                files.update(base.rglob("*.md"))
    return sorted(files)


def conformance(text: str, template: Template) -> list[str]:
    found = headings(text)
    body = strip_noise(text)
    problems: list[str] = []
    position = -1
    for section in template.sections:
        if section not in found:
            problems.append(f"缺章节「{section}」")
            continue
        index = next((i for i, h in enumerate(found) if h == section and i > position), None)
        if index is None:
            problems.append(f"章节「{section}」顺序错误")
        else:
            position = index
    problems += [f"缺必含字段「{token}」" for token in template.must if token not in body]
    problems += [f"含禁止字段「{token}」" for token in template.must_not if token in body]
    return problems


def check_templates(root: Path, baseline: dict) -> list[Finding]:
    directory = root / TEMPLATES
    findings: list[Finding] = []
    if not directory.is_dir():
        return findings
    catalog_path = directory / "README.md"
    catalog = catalog_path.read_text(encoding="utf-8") if catalog_path.exists() else ""
    for path in sorted(directory.rglob("*.md")):
        if path.name == "README.md":
            continue
        rel = path.relative_to(root).as_posix()
        if not HEADER_RE.match(path.read_text(encoding="utf-8")):
            findings.append(Finding("ERROR", "TEMPLATE-HEADER", rel, "模板必须以 `<!-- template` 头注释开始（applies-to 必填）"))
        if path.relative_to(directory).as_posix() not in catalog:
            findings.append(Finding("ERROR", "TEMPLATE-CATALOG", rel, f"未登记 {TEMPLATES}/README.md"))
    templates = load_templates(root, baseline)
    skipped = [glob_re(d.rstrip("/") + "/**") for d in (*STEADY_SKIP, *baseline.get("frozen_dirs", []))]
    base = plans.bundle_root(baseline)
    bundle_extras = {f"{base}/{item}" for item in baseline.get("bundle_file_exceptions", [])}
    exceptions = set(baseline.get("template_exceptions", []))
    for path in candidates(root, templates):
        rel = path.relative_to(root).as_posix()
        if rel in bundle_extras or rel in GENERATED or any(s.match(rel) for s in skipped):
            continue
        text = path.read_text(encoding="utf-8")
        if text.startswith("<!-- template"):
            findings.append(Finding("ERROR", "TEMPLATE-LEFTOVER", rel, "复制模板后未删除首行头注释"))
        matched = [t for t in templates if matches(rel, t)]
        if not matched:
            findings.append(Finding("WARN", "TEMPLATE-NONE", rel, f"没有适用模板；先在 {TEMPLATES}/ 建模板并登记目录"))
            continue
        if len(matched) > 1:
            findings.append(Finding("ERROR", "TEMPLATE-AMBIGUOUS", rel, "同时匹配 " + "、".join(t.path for t in matched)))
            continue
        if rel in exceptions:
            continue
        problems = conformance(text, matched[0])
        if problems:
            findings.append(Finding("ERROR", "TEMPLATE-CONFORM", rel, f"不符合 {matched[0].path}：" + "；".join(problems)))
    return findings
