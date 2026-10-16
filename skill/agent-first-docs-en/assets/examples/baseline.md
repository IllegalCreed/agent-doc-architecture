# Onboarding config: `baseline.json`

`scripts/doclint/baseline.json` is the **onboarding config** for a project that adopts these rules partway through. It registers the violations that already exist at the moment of onboarding as exemptions, so `doc-lint` is immediately 0 ERROR, and after that only a **new** violation fails. JSON cannot hold comments, so the per-key notes live in this file. [baseline.json](baseline.json) is an example for a fictional project.

A new project does not need this file (if you need to register `inherit_pairs`, you may create a file that contains only that key; strict checking is unaffected). When the file is absent, `doc-lint` checks strictly: no exemptions, a broken-link baseline of 0, and bundles laid out flat under `docs/plans/`.

## Generating it

```bash
python3 scripts/doc-lint.py init-baseline                      # print the JSON that would be written
python3 scripts/doc-lint.py init-baseline --write              # write scripts/doclint/baseline.json
python3 scripts/doc-lint.py init-baseline --bundle-root docs/plans/changes --frozen docs/plans/legacy --write
```

- Fix the "cannot be exempted" problems below first. When `init-baseline` finds them it prints each one as `must-fix …`, exits 1, and **does not write the file**.
- After writing, run `python3 scripts/doc-lint.py`. It should be 0 ERROR.

### Cannot be exempted (must-fix)

The tool depends on these to parse everything else, or the fix is small and there is no matching exemption key, so they must be fixed before onboarding. The full list is `MUST_FIX` in `scripts/doclint/onboard.py`. The main ones:

- Structural: missing `docs/plans/index.md` (PLAN-INDEX-MISSING) or `docs/testing/cases/index.md` (CASE-INDEX-MISSING); a wrong index or case-table header, or a row with the wrong number of columns; a duplicate Stable ID or Case ID; a status, type, or layer outside the vocabulary; a template with no header comment, or one not registered in the catalog.
- Local: a broken link in an entry document (LINK-ENTRY), a date banner in the index, an unregistered bundle or missing metadata, a stale generated view (run `gen-views`), a spec document missing `Last reviewed`, and similar.

The two indexes can be created straight from the templates. Copy `docs/handbook/templates/singleton/plans-index.md` and `singleton/cases-index.md`, delete the opening header comment, then run `python3 scripts/doc-lint.py gen-views`.

## Exemptions only shrink (the ratchet)

- The four exemption lists (`naming_exceptions`, `bundle_file_exceptions`, `case_id_exceptions`, `template_exceptions`) and `broken_links_total` are a ratchet that **can only get smaller**.
- When the file an exemption names is deleted, renamed, or already conforms, `doc-lint` reports `WARN BASELINE-STALE <path>` and tells you to delete that entry from the config. When the broken-link count is below the baseline it reports `INFO LINK-BASELINE` and tells you to lower `broken_links_total`.
- You can delete a stale entry by editing the JSON, or by rerunning `init-baseline --write`. They are equivalent. **A rerun only deletes entries. It never adds one.** When a config already exists, each list is the intersection with the current config, and the broken-link baseline is the smaller of the two values. A new violation is not registered. It is reported as `must-fix` (exit 1, file not written).
- Do not use `init-baseline` to "add an exemption" for a new violation. Fix the new violation in place. When you truly need to onboard again from scratch (for example after a large migration), delete `baseline.json` first and then run. That is an explicit decision that needs review.

## Per-key notes

| Key | Who maintains it | Meaning | Default |
|---|---|---|---|
| `bundle_root` | `init-baseline` (`--bundle-root` wins, otherwise the current value, otherwise `docs/plans/changes` when that directory exists) | Root directory of change bundles. Plan links in `docs/plans/index.md` resolve against it, and `{bundle_root}` in a template header comment is replaced with it | `docs/plans` (bundles laid out flat) |
| `rules_effective_since` | `init-baseline` (the first run takes today's `YYYYMMDD`; a rerun keeps it) | The day the rules take effect. A bundle whose directory date is earlier than this is not checked for "the Stable ID's first letter matches Type" (BUNDLE-ID-LETTER) | Absent: everything is checked strictly |
| `frozen_dirs` | `init-baseline --frozen` (if omitted, the current value is kept) | Frozen directories: the whole directory skips the template-conformance check. For a read-only historical archive | `[]` |
| `broken_links_total` | `init-baseline`; may only be lowered | The cap on broken links across the repo (`docs/` and `AGENTS.md`). Above the cap is ERROR. Broken links in entry documents (`AGENTS.md`, `docs/README.md`, `docs/handbook/`, `docs/testing/`, and the like) are not covered by this baseline and are always ERROR | `0` |
| `naming_exceptions` | `init-baseline`; may only shrink | Existing record files (`docs/reports/`, `docs/testing/infrastructure/`, `docs/releases/`) whose names do not match `YYYYMMDD-<slug>.md`. Paths relative to the repo | `[]` |
| `bundle_file_exceptions` | `init-baseline`; may only shrink | Existing files inside a bundle that are outside the file allowlist, written as `<bundle directory>/<filename>` relative to `bundle_root`. These files also skip the template check | `[]` |
| `case_id_exceptions` | `init-baseline`; may only shrink | Existing Case IDs whose format is not `TC-<module>-NNN` (the ID is stable and must not be renamed). Only the format is exempted. A duplicate is still an error | `[]` |
| `template_exceptions` | `init-baseline`; may only shrink | Existing documents that do not match the template that applies (required sections, required text). Paths relative to the repo | `[]` |
| `inherit_pairs` | By hand; `init-baseline` keeps them as they are | Pairs of paths `[project layer, shared layer]`. The project layer's first 15 lines must contain a `> Inherits:` link to the shared layer. The shared layer's first 20 lines must contain a `> Project landing:` link back to the project layer | `[]` |
| `fresh_docs` | By hand; `init-baseline` keeps them as they are | Current-fact documents that need `Last reviewed: YYYY-MM-DD` (globs; `*` does not cross a directory, `**/` does). Older than the latest tag is WARN | `docs/overview.md`, `docs/roadmap.md`, `docs/deployment/README.md`, `docs/handbook/**/*.md`, `docs/testing/guides/*.md` |
| `strict_fresh` | By hand; `init-baseline` keeps them as they are | The subset of `fresh_docs` whose staleness is ERROR under `--release` (release seal) | `docs/overview.md`, `docs/roadmap.md` |

The two paths in the example's `inherit_pairs` are only a demonstration. When you onboard, fill in where this project actually puts the shared-layer and project-layer documents. If there is no layering, omit the key.
