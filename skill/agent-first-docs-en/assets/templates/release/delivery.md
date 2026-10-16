<!-- template
applies-to: docs/releases/v*-delivery.md
must-contain: SHA-256; Rollback; tag
-->
# vX.Y.Z artifact delivery note

> One sentence: whether a production migration is still pending, and the deployment window.

## Delivery result

<!-- Required: the annotated tag (a short description), the release commit hash, the build command and the build time, the package filename (for example vX.Y.Z-YYYYMMDD-HHMMSS-dist.zip), the size in bytes, and the package SHA-256. When several packages exist for the same day, say which one is void and must not be used. -->

## Artifacts and verification

| Artifact | Path inside the package | Verification |
|---|---|---|

<!-- One row per deployment unit: frontend, server, client, and other artifacts (build parameters, version identifier, size in bytes, SHA-256; a new build or a reuse of the previous version), and the production database migration (migration numbers and their order, or "None"). -->

## Release scope

<!-- The changes on the main line, with their Stable IDs. -->

## Deploy order and smoke tests

<!-- Ordering constraints (for example, migrate before deploying). The smoke checklist (covering the main roles). -->

## Rollback and acceptance boundary

<!-- Rollback steps; risk of leftover data structures; the acceptance boundary. The words SHA-256, Rollback, and tag must appear in the body of the filled document, not only inside these comments. -->

## Records

<!-- Links: the changelog, the release-seal plan, the test report. -->
