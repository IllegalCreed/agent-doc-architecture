# Vocabulary and format cheat sheet

What follows is what `doc-lint` checks. A few items ("fixed key order", "a terminal status writes `-`") are conventions the tool does not check. The vocabulary lives in `scripts/doclint/vocab.py`. This edition's labels are English. `plans.py` and `cases.py` read cells through the column-name constants in that file. There is no runtime language switch; the Chinese edition is the sibling skill `agent-first-docs`. When you change the vocabulary, change the project's documentation-model spec to match.

## Changes: IDs, metadata, status

**Stable ID** = `<letter>-YYYYMMDD-NNN`. Directory = `YYYYMMDD-<lowercase letter>NNN-<slug>/`. The two convert into each other mechanically. `NNN` starts at 001 for each (date, letter) pair. The slug is `[a-z0-9-]+` (the title goes in the H1 and in the index). Always take a number with `doc-lint next-id --type <type>`: it scans every local branch, every remote-tracking branch, and every worktree, so parallel branches do not collide. On a collision, **the later claimant moves**. The content stays the same, and the original ID is recorded. `next-id` does not fetch; a new remote branch is visible only after `git fetch`.

| Type | Letter | Use |
|---|---|---|
| feature | F | A new capability |
| bugfix | B | Fix a defect (record the reproduction, the root cause, and a regression case) |
| refactor | R | A structural change; external behavior stays the same |
| test-infrastructure | T | Test framework, fixtures, a coverage catch-up |
| docs | D | Documentation rules, governance |
| ops | O | Deployment, environments, operations |
| release | C | Seal a release, produce a package (the letter map lives in `vocab.py`; change it there, and do not change it again after it is defined) |

**Metadata block** (after the H1 of `requirements.md`; English keys, fixed order; 7 required keys):

```markdown
> Status: draft
> Stable ID: F-20260101-001
> Type: feature
> Created: 2026-01-01
> Last reviewed: 2026-01-01
> Replaces: none
> Replaced by: none
```

Optional keys go after the required keys: `Owner`, `Progress`, `Blocked by`, `Next action`, `Related plans`, `Related tests`.

| Status | Meaning | How an agent uses it |
|---|---|---|
| draft | Under discussion | Background only. Not a basis for implementation |
| approved | Approved, not implemented | May be used as a basis for implementation |
| in-progress | Being implemented | Write results back as you implement |
| implemented | Code has landed; verification is incomplete | Read the implementation record and the test record |
| verified | Implementation and verification are both confirmed (including released) | May be treated as current fact |
| superseded | Taken over by a newer change | **Must** follow `Replaced by` (doc-lint checks that it names a Stable ID registered in the main index: `BUNDLE-SUPERSEDE`). The original directory stays in place; it is not moved |
| deprecated | No longer describes current behavior, but still has historical value | Traceability only |
| obsolete | No longer valid | Not a basis for implementation |
| cancelled | Decided not to do | Not a basis for implementation. Read why it was cancelled |

## Shapes of a change

| Shape | How to tell | Required files |
|---|---|---|
| Standard | Contains `design.md` | `requirements.md`, `design.md`, `implementation.md` (when status ≥ implemented), `test-cases.md` |
| Lightweight | Does not contain `design.md` | `requirements.md`; when status ≥ implemented it must contain a `## Implementation record` section |

Optional-file allowlist (only these names are allowed): `impact-map.md`, `handoff.md`, `manual-test-cases.md`, `stages.md` plus `stage<N>[a-z]-<slug>.md`, `review-<agent>-YYYYMMDD.md`. A file outside the allowlist is an error. Scripts belong in `scripts/`, not in the change directory.

Reading order: requirements → design → impact-map → implementation → test-cases. Read `handoff`, `review`, and `manual-test-cases` only while executing, reviewing, or accepting.

## Main index (`docs/plans/index.md`)

Only: an H1, one line of explanation, one table, and topic entries. The header is fixed at six columns:

```
| Stable ID | Type | Title | Status | Next step | Plan |
```

Title ≤ 50 characters. Next step ≤ 80 characters. A terminal status (verified / superseded / deprecated / obsolete / cancelled) writes `-`. The Plan column holds only the link to the change entry. **No date banners and no multi-line preamble.** Progress belongs in the change's own documents. Version news belongs on the roadmap (at most 5 banners; archive the older ones).

## Directories, names, topics

- Directories are by **duty**: current fact (handbook, overview), changes (plans), test definitions (testing), execution evidence (reports), releases (releases), operations (deployment), attachments (assets). Each directory README has a "placement rules" table.
- In record directories (reports, releases, and the like) the filename is `YYYYMMDD-<slug>.md`. Release documents are `vX.Y.Z.md` / `vX.Y.Z-delivery.md`. The title goes in the H1.
- **A bundle is short-lived** (one deliverable change; a large multi-stage change is still one bundle plus `stages.md`). **A track is long-lived** (a topic that spans several independent changes): it records only why, the order, the boundary, and links to the related changes. **It does not hold a plan and it does not record status.**
- Case IDs are `TC-<module>-NNN` (no version segment). The case main table is the only source of fact. The by-layer and by-module views are generated by `gen-views`. Do not write them by hand.

## Case layers

The tool's vocabulary is fixed at `L1`–`L5` plus `manual` (`CASE_LAYERS` in `vocab.py`). What each layer means is defined by the **project testing spec**. When the project has no testing spec yet, put one line at the top of the case main table: "Layers, for now: L1 …" (you may omit it when there are no cases yet), and move that definition into the spec once it exists. A case belongs to exactly one primary layer.

## Case table

The main-table header is fixed at nine columns: `Case ID | Title | Feature / module | Owner Plan | Layer | Automation path | Status | Last verified | Notes`. Case statuses: `active` / `stale` / `deprecated` / `obsolete`.

## Templates

`templates/README.md` is the catalog. The `<!-- template … -->` header comment, starting at the first line of a template, declares `applies-to` (globs; separate several with `;`), `must-contain`, and `must-not-contain`. The H2 headings after the header comment are the required sections, checked in order. A heading that ends with ` (optional)` is not required. Do not put Markdown links in a template. A document kind with no applicable template: create the template, register it in the catalog, then write the document.
