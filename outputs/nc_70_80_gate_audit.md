# NC 70-80 Gate Audit

Date: 2026-06-21

## Current position

The current package is stronger than a benchmark-only paper. It now contains held-event and held-station tests, AQ2009GM full-manifest streaming validation, a CWA official PGA/PGV one-year layer, ESM external checks, ESM regional GMM screening, cross-region transfer, conformal uncertainty, strong-tail auditing, residual persistence, residual mechanism classes and an official-format PDF.

Current defensible probability estimate after adding the CWA official PGA/PGV layer: **65-70%**.

Do not present **70-80%** as current. That would overstate the evidence.

## What moved the paper up

| Layer | Status | Probability effect |
|---|---|---|
| Public event-station benchmark | Done | Makes the work reusable instead of a single-model report |
| Held-event and held-station splits | Done | Blocks the strongest leakage objection |
| AQ2009GM full-manifest streaming validation | Done | Adds an independent SeisBench strong-motion check |
| CWA official PGA/PGV one-year validation | Done | Adds a Taiwan official metadata-target check |
| ESM external strong-motion check | Done | Adds a European target domain |
| ESM regional GMM screening | Done | Tests the added-information claim against stronger regional references |
| Cross-region transfer boundary | Done | Turns poor transfer into a result |
| Conformal uncertainty | Done | Adds calibrated risk framing |
| Strong-tail audit | Done | Addresses high-consequence errors |
| Residual persistence and mechanism audits | Done | Shows unresolved errors have structure |
| Official-format PDF with embedded figures | Done | Makes desk review easier |

## Blocking gates for 70-80

| Gate | Why it matters | Current status |
|---|---|---|
| Complete references | Missing references signal an unfinished submission | Filled with verified DOI-backed entries; final literature-manager export still recommended |
| Author, affiliation, contribution and acknowledgement metadata | Submission systems require complete metadata | Filled from user-confirmed memory: Zhou Haoyu first author, Ma Qiang supervisor and corresponding author, no funding, no competing interests |
| Manual ESM P-pick validation | Would remove the theoretical-onset weakness | Not done |
| Fully specified regional GMM comparison | Would address the strongest seismology reviewer objection | Screening layer done; full comparison still waits for curated rupture/site/mechanism fields |
| Stronger physical residual mechanism | Would make the boundary feel like a geophysical result | Residual classes now separate path-attenuation, strong-motion-tail and early-amplitude boundaries |
| Clean public release package | Editors and reviewers need reproducibility without local paths | Local package exists; final archive DOI missing |

## Automatic work still worth doing

1. Prepare source-data and code-availability wording for an archival release.
2. Keep residual mechanism as Extended Data, not a new main claim.
3. Run placeholder and PDF checks after every manuscript regeneration.

## Work that should not be automated

1. Suggested reviewers.
2. Manual ESM P-pick labels.
3. Claims of operational EEW readiness.

## Bottom line

The fastest honest route is now to keep the package submission-complete and add one major independent evidence layer that cannot be generated from the current tables, such as manual ESM P picks or curated rupture/site/mechanism fields. With the current evidence, the realistic target is **65-70%**, not **70-80%**.
