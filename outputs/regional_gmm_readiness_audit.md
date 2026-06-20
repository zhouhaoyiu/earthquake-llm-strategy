# Regional GMM Readiness Audit

Date: 2026-06-18

This audit checks whether the current balanced held-station data support a fully specified regional GMM comparison.

## Findings

- InstanceGM joins back to metadata for 5000/5000 train records and 1000/1000 test records.
- InstanceGM has Vs30 for 5000/5000 train records and 1000/1000 test records.
- InstanceGM has focal-mechanism strings for 141/5000 train records and 36/1000 test records.
- K-NET has source-distance values for 5000/5000 train records, but no Vs30 or focal-mechanism fields in the current local package.

## Interpretation

The current package supports bias-corrected classical references and Japanese GMM screening, but it does not support a fully specified regional GMM claim. InstanceGM has site terms but sparse mechanism coverage. K-NET has the target and distance coverage needed for screening, but lacks Vs30, rupture distance, and focal-mechanism or tectonic-class metadata in the approved local data.

CSV: `outputs/regional_gmm_readiness_audit.csv`
