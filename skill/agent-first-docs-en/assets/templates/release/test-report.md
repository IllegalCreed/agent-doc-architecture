<!-- template
applies-to: docs/reports/tests/releases/*.md
must-contain: Suite | Result | Command / evidence
-->
# vX.Y.Z release-seal test report

<!-- Name the file by the record-naming rule for docs/reports: YYYYMMDD-<slug>.md, for example 20300102-v1-2-3.md (not vX.Y.Z.md). -->

> The release commit under test, the date, and the environment it ran in.

## Baseline and isolation

<!-- The commit and branch under test. The instance under test (port, configuration, database). How the parallel-execution constraint was kept. -->

## Suite acceptance

| Suite | Result | Command / evidence |
|---|---|---|
| <suite 1> | | |
| <suite 2> | | |

<!-- One row per suite the release seal must run (the suite list and the definitions come from the project's release-process document). Fill the result and a reproducible command or an evidence link on every row. A partial run must not be written up as "the full suite is green". -->

## Failures and skips, with causes

<!-- First-run failures, reruns, and skips that were already known, each with a cause. An isolated rerun is for locating a problem. It does not count as a pass. -->

## Artifact checks

<!-- The package gate, smoke and canary, and the release artifact SHA-256. -->

## Leftovers

<!-- Coverage gaps, and items still to run. -->
