"""存量项目接入：生成接入配置（init-baseline）与检测失效豁免（BASELINE-STALE）。

接入配置把「接入那一刻」的存量违规登记为豁免，之后只有新增违规会失败；豁免只减不增。
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from . import cases, plans, repo_checks, templates, vocab
from .model import Finding

DETECTED_BUNDLE_ROOT = "docs/plans/changes"
BASELINE_FILE = "scripts/doclint/baseline.json"
LIST_KEYS = ("naming_exceptions", "bundle_file_exceptions", "case_id_exceptions", "template_exceptions")
PRESERVED_KEYS = ("inherit_pairs", "fresh_docs", "strict_fresh")

# 可由接入配置豁免的 ERROR：检查代码 → 接入配置键。
# CASE-ID 只有「格式非法」可豁免；「重复」应用豁免后仍报错，按 must-fix 处理。
# BUNDLE-ID-LETTER 靠 rules_effective_since 豁免生效日之前的 bundle。
BASELINABLE = {
    "NAME": "naming_exceptions",
    "BUNDLE-FILE": "bundle_file_exceptions",
    "CASE-ID": "case_id_exceptions",
    "TEMPLATE-CONFORM": "template_exceptions",
    "LINK-BASELINE": "broken_links_total",
    "BUNDLE-ID-LETTER": "rules_effective_since",
}

# 不可豁免、接入前必须先修的 ERROR（init-baseline 报 must-fix 并退出 1，不写文件）。
MUST_FIX = frozenset({
    # 结构性：索引缺失、表头 / 列数损坏、Stable ID 重复、词表外取值——工具依赖它们解析，豁免会让后续检查失真
    "PLAN-INDEX-MISSING", "PLAN-INDEX-HEADER", "PLAN-ROW-COLUMNS", "PLAN-ID-DUP", "PLAN-STATUS", "PLAN-TYPE",
    "CASE-INDEX-MISSING", "CASE-HEADER", "CASE-ROW-COLUMNS", "CASE-LAYER", "CASE-STATUS",
    "TEMPLATE-HEADER", "TEMPLATE-CATALOG", "TEMPLATE-AMBIGUOUS",
    # 局部且改动小、没有豁免键：直接修
    "PLAN-INDEX-BANNER", "PLAN-INDEX-PREAMBLE", "PLAN-TITLE-LEN", "PLAN-NEXT-LEN",
    "BUNDLE-NAME", "BUNDLE-UNREGISTERED", "BUNDLE-META-MISSING", "BUNDLE-META-MISMATCH", "BUNDLE-RECORD",
    "CASE-NARRATIVE", "CASE-VIEW-STALE", "LINK-ENTRY", "INHERIT", "FRESH-MISSING", "ROADMAP-BANNERS",
    "TEMPLATE-LEFTOVER",
    # 只在 --release 下是 ERROR；init-baseline 按日常模式运行，这里只为分类完整
    "FRESH-STALE",
})


def case_ids(root: Path) -> list[str]:
    """主表（表头合法、列数正确的行）里的全部 Case ID，按出现顺序去重。"""
    _, _, tables = cases.read_main(root)
    ids: list[str] = []
    for _, header, rows in tables:
        if header != vocab.CASE_HEADER:
            continue
        for _, cells in rows:
            if len(cells) == len(header) and cells[0] not in ids:
                ids.append(cells[0])
    return ids


def current_violations(root: Path, config: dict) -> dict[str, list[str]]:
    """在空豁免下计算各可豁免类的当前违规；config 只取 bundle_root、frozen_dirs、bundle_file_exceptions。"""
    base = plans.bundle_root(config)
    scope = {"bundle_root": base}
    bundle_files = [
        f.path[len(base) + 1:] for f in plans.check_bundles(root, scope) if f.code == "BUNDLE-FILE"
    ]
    template_scope = {
        **scope,
        "frozen_dirs": config.get("frozen_dirs", []),
        "bundle_file_exceptions": config.get("bundle_file_exceptions", bundle_files),
    }
    return {
        "naming_exceptions": repo_checks.naming_violations(root),
        "bundle_file_exceptions": bundle_files,
        "case_id_exceptions": [cid for cid in case_ids(root) if not vocab.CASE_ID_RE.match(cid)],
        "template_exceptions": [
            f.path for f in templates.check_templates(root, template_scope) if f.code == "TEMPLATE-CONFORM"
        ],
    }


def build_baseline(
    root: Path,
    existing: dict,
    bundle_root: str | None = None,
    frozen: list[str] | None = None,
    today: str | None = None,
) -> tuple[dict, list[Finding]]:
    """返回 (接入配置, must-fix 列表)。

    首次接入（existing 无 rules_effective_since）：把当前违规全部登记。
    已接入（重跑）：豁免只减不增——列表取与现有配置的交集、断链基线取较小值，
    新增违规不登记，作为 must-fix 报出；生效日期、bundle_root、frozen_dirs 沿用现值（显式参数优先）。
    """
    root = root.resolve()
    adopted = "rules_effective_since" in existing
    config: dict = {}
    base = bundle_root or existing.get("bundle_root")
    if base is None and (root / DETECTED_BUNDLE_ROOT).is_dir():
        base = DETECTED_BUNDLE_ROOT
    if base:
        config["bundle_root"] = base
    config["rules_effective_since"] = existing.get("rules_effective_since") or today or date.today().strftime("%Y%m%d")
    config["frozen_dirs"] = list(frozen) if frozen is not None else list(existing.get("frozen_dirs", []))
    links = repo_checks.broken_links_total(root)
    config["broken_links_total"] = min(links, existing.get("broken_links_total", 0)) if adopted else links

    def ratchet(key: str, values: list[str]) -> list[str]:
        if not adopted:
            return values
        allowed = set(existing.get(key, []))
        return [v for v in values if v in allowed]

    current = current_violations(root, config)
    for key in ("naming_exceptions", "bundle_file_exceptions", "case_id_exceptions"):
        config[key] = ratchet(key, current[key])
    # 模板检查跳过已豁免的 bundle 附加文件，所以按最终的 bundle_file_exceptions 重算
    config["template_exceptions"] = ratchet("template_exceptions", current_violations(root, config)["template_exceptions"])
    for key in PRESERVED_KEYS:
        if key in existing:
            config[key] = existing[key]

    from .cli import run  # 延迟导入：cli 依赖本模块

    must_fix = [f for f in run(root, baseline=config) if f.level == "ERROR"]
    return config, must_fix


def check_baseline_stale(root: Path, baseline: dict) -> list[Finding]:
    """豁免条目对应的文件已删除或已合规时报 WARN，让豁免列表只减不增。"""
    if not any(baseline.get(key) for key in LIST_KEYS):
        return []
    root = root.resolve()
    current = current_violations(root, baseline)
    base = plans.bundle_root(baseline)
    known_ids = set(case_ids(root))
    findings: list[Finding] = []
    for key in LIST_KEYS:
        live = set(current[key])
        for entry in baseline.get(key, []):
            if entry in live:
                continue
            if key == "case_id_exceptions":
                path = f"{cases.CASES}/index.md"
                reason = "Case ID 已符合格式" if entry in known_ids else "Case ID 已不在主表"
            else:
                path = f"{base}/{entry}" if key == "bundle_file_exceptions" else entry
                reason = "已不再违规" if (root / path).exists() else "文件已不存在"
            findings.append(Finding(
                "WARN", "BASELINE-STALE", path,
                f"{key} 条目「{entry}」已失效（{reason}），从 {BASELINE_FILE} 删除（豁免只减不增）",
            ))
    return findings
