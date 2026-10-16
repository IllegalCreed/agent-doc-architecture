# Document template catalog

> This directory lives in the project at `docs/handbook/templates/` (doc-lint reads templates from there by default). Paths in the table are relative to `docs/`.

> There is one template per document kind. To create a document: copy the matching template, delete the opening `<!-- template … -->` header comment, and fill the sections from the comments inside them. **Do not imitate the structure of the previous document of the same kind.** That document's drift gets copied and then stacked.

## How to use them

- A template's H2 headings are the required sections. Do not change the wording or the order (a "1." numbering prefix is allowed). A section with nothing to say writes "None". A section ending in ` (optional)` is deleted when you do not use it; when you use it, drop ` (optional)`. You may add sections the template does not have.
- The header comment's `applies-to` declares the paths this template governs. `must-contain` and `must-not-contain` declare required and forbidden text (text inside an HTML comment does not count). doc-lint reads the template and checks against it. There is no separate rule list.
- A document kind with no applicable template: create the template in this directory, register it in the table below, then write the document.
- Changing a template does not reach back into documents that already exist. Documents that predate onboarding and do not conform are registered in `template_exceptions` of the onboarding config. That list may only shrink.

## Catalog

| Kind | Template | Applies to | Who writes / who reads |
|---|---|---|---|
| Requirements | [plan/requirements.md](plan/requirements.md) | bundle `requirements.md` (standard and lightweight share it) | The agent writes; a person approves |
| Design | [plan/design.md](plan/design.md) | bundle `design.md` | The agent |
| Implementation record | [plan/implementation.md](plan/implementation.md) | bundle `implementation.md` | The agent |
| Test cases | [plan/test-cases.md](plan/test-cases.md) | bundle `test-cases.md` | The agent |
| Handoff | [plan/handoff.md](plan/handoff.md) | bundle `handoff.md` | The handing-off side writes; the executing or reviewing agent reads |
| Impact map | [plan/impact-map.md](plan/impact-map.md) | bundle `impact-map.md` | The agent |
| Manual cases | [plan/manual-test-cases.md](plan/manual-test-cases.md) | bundle `manual-test-cases.md` | The agent writes; a person runs them |
| Stage plan | [plan/stages.md](plan/stages.md) | bundle `stages.md` | The agent |
| Stage booklet | [plan/stage.md](plan/stage.md) | bundle `stage<N>-<slug>.md` | The agent |
| Review | [plan/review.md](plan/review.md) | bundle `review-<agent>-YYYYMMDD.md` | The reviewing agent |
| Long-lived topic | [plan/track-readme.md](plan/track-readme.md) | `plans/tracks/<topic>/README.md` | The agent |
| Changelog | [release/notes.md](release/notes.md) | `releases/vX.Y.Z.md` | The agent writes; the end user reads |
| Delivery note | [release/delivery.md](release/delivery.md) | `releases/vX.Y.Z-delivery.md` | The agent writes; operations reads |
| Release-seal test report | [release/test-report.md](release/test-report.md) | `reports/tests/releases/` | The agent |
| Focused test report | [testing/test-report.md](testing/test-report.md) | `reports/tests/` (except release-seal reports) | The agent |
| Manual regression | [testing/regression.md](testing/regression.md) | `testing/cases/regressions/` | The agent writes; a person runs it |
| Rule catalog | [testing/catalog.md](testing/catalog.md) | `testing/cases/catalogs/` | The agent |
| Incident report | [report/incident.md](report/incident.md) | `reports/incidents/YYYY-MM/` | The agent |
| Audit report | [report/audit.md](report/audit.md) | `reports/audits/`, `reports/security/` | The agent |
| Migration evidence pack | [report/migration-readme.md](report/migration-readme.md) | `reports/migrations/<topic>/README.md` | The agent |
| Migration execution record | [report/migration-record.md](report/migration-record.md) | `reports/migrations/<topic>/*.md` | The agent / operations |
| Operations record | [report/operations.md](report/operations.md) | `reports/operations/YYYY-MM/` | The agent / operations |
| Analysis report | [report/analysis.md](report/analysis.md) | `reports/analysis/`, `reports/refactoring/` | The agent |
| Spec document | [handbook/handbook.md](handbook/handbook.md) | `handbook/`, `testing/guides/` | The agent |
| Deployment runbook | [handbook/runbook.md](handbook/runbook.md) | `deployment/` | The agent writes; operations reads |
| Project overview | [singleton/overview.md](singleton/overview.md) | `overview.md` | The agent |
| Roadmap | [singleton/roadmap.md](singleton/roadmap.md) | `roadmap.md` | The agent |
| Change index | [singleton/plans-index.md](singleton/plans-index.md) | `plans/index.md` | The agent |
| Case index | [singleton/cases-index.md](singleton/cases-index.md) | `testing/cases/index.md` | The agent |
| User manual | [singleton/operation-manual.md](singleton/operation-manual.md) | `operation-manual.md` | The agent writes; the end user reads |
| Directory README | [singleton/dir-readme.md](singleton/dir-readme.md) | `README.md` at each directory level | The agent |
