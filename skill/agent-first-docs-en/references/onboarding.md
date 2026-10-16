# Onboarding: a project that already has docs

An existing project cannot "migrate everything to the new format, then turn the checks on". The migration never finishes, the checks stay red, and someone turns them off. The approach is: **freeze what exists, register a baseline, be strict about new writing, and migrate a document when you next touch it.**

## Principles

- **Do not delete old documents and do not rewrite them** (decision 3). Move them as-is. Text you move out goes into a migration record.
- The rules are mandatory only for **new documents**. Isolate the existing tree with frozen directories and with exemptions in the onboarding config. Exemptions may only shrink.
- Dates and project paths go only in the **onboarding config** (`baseline.json`), not in the checker. The code stays project-agnostic.
- Do not rewrite everything at once. Each time you touch an old document (you are about to edit it, or you are about to cite it), migrate it to the new shape as you go.

## Steps

1. **Inventory.** List the existing docs tree, how many documents of each kind, and the indexes and naming habits already in use. Read only. Change nothing.
2. **Install the tools.** `assets/scripts/` → `scripts/`; `assets/templates/` → `docs/handbook/templates/`. Do not touch any old document yet.
3. **Create `docs/README.md` and the two indexes.** `docs/README.md` is the same as in the steady state: directories by duty, and a README for each top-level directory from `singleton/dir-readme.md`. Spec documents carry `Last reviewed`. `docs/plans/index.md` and `docs/testing/cases/index.md` are both required (without them the tool cannot parse the rest). Copy `singleton/plans-index.md` and `singleton/cases-index.md`, delete the header comments, register the existing plans and cases (do not rename them and do not change their content; see "Existing plans have no ID, or they are a single file" below), then run `python3 scripts/doc-lint.py gen-views`.
4. **Generate the onboarding config.** `python3 scripts/doc-lint.py init-baseline` (print only, first). It lists `must-fix` items: a broken link in an entry document, a wrong index header, a duplicate ID, a status outside the vocabulary, an unregistered bundle, and the other problems that **cannot be exempted**. Fix them one by one until they stop appearing. When you need them, pass `--bundle-root` (the existing bundles are not laid out flat under `docs/plans/`) and `--frozen <directory>` (a read-only historical archive, exempt from template checks as a whole).
5. **Write it.** `init-baseline --write` creates `scripts/doclint/baseline.json`. Run `doc-lint` again. It should be 0 ERROR. In the config, `rules_effective_since` (the day of the first run) exempts only older bundles from the "ID letter matches the type" check. The four exemption lists (naming, extra files inside a bundle, Case ID format, template mismatch) and `broken_links_total` record the existing violations as known. The per-key notes are in `assets/examples/baseline.md`.
6. **Tighten (the ratchet).** Each time you fix an existing violation, that exemption goes stale and `doc-lint` reports `WARN BASELINE-STALE <path>`. Delete that entry from the config (edit the JSON by hand, or rerun `init-baseline --write`; they are equivalent). **A rerun only deletes entries. It never adds one.** A new violation is always reported as `must-fix`, the file is not written, and you fix it in place. When you truly need to start over, delete `baseline.json` first. That is an explicit decision that needs review.
7. **Migrate when you touch it.** When you edit an old document, migrate it to the new shape from the template. Put the original text in a migration record, and **check the facts once before the move and once after**.
8. **Wire the route.** Add routing rows to the entry file (read the documentation spec before changing docs; run doc-lint before committing), and add `--release` to the release-seal checklist.

## Existing plans have no ID, or they are a single file

- The tool scans **bundle directories** only. An old plan that is a flat single file is not checked, but a link to it from the main index is valid. So: **leave it where it is, and only register it in the index.** Migrate it into a bundle when you next touch it.
- An old plan with no Stable ID: infer one from the filename date plus the type letter (for example `F-20260101-001`, incrementing for the same day and the same type). **Write it only in the index. Do not edit the old file.**
- Map status conservatively. An old file that says `done` but has no verification record becomes `implemented` (not `verified`), and "Next step" says "change to verified after a person accepts". Acceptance is a person's adjudication.
- An existing document with no applicable template (an old report, for example) gets `TEMPLATE-NONE` as a **WARN**. There is no exemption key for it. That is expected. It goes away when a template exists or when the document is migrated.

## One-shot migration scripts

- A migration script is **one-shot**, not a tool you run again. Write it, run it, commit the result. Do not leave the script in the permanent `scripts/` location (citing it from the migration record is enough).
- A migration script has a dry run, and you run `doc-lint` once before the commit and once after, to confirm the violation count only goes down.
- When the change is large, one migration is one commit that can be reverted on its own.

## Merge conflicts

- Other people are editing documents during the migration. The main index and the roadmap almost always conflict. **Merge by hand.** Do not let a tool pick one side. Rebuild the index row from the change's own metadata.
- A numbering collision: the later claimant moves. The content stays the same, and the original ID is recorded.

## When onboarding is done

- `doc-lint` is 0 ERROR across the repo (existing violations inside an exemption are reported as WARN).
- Every new document comes from a template and carries a stable ID. `next-id` works.
- The routing table has the two rows "change docs" and "seal a release".
- The baseline is still shrinking. Reaching zero is not the goal. **Not growing** is.
