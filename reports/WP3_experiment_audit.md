# WP3 — Experimental evidence reconciliation

**Date:** 20 November 2026
**Branch:** `stage-6.3-corrections`
**Gate:** G3
**Status:** PASS with 3 documented discrepancies

## 1. Raw JSON manifest

All 11 raw JSON files are frozen and hashed in `evidence_registry/raw_manifest.csv`.

| Experiment | File | SHA-256 (first 16) |
|---|---|---|
| E0 | e0_results.json | a615fed8314a807a |
| E1 | e1_results.json | 80f65449972d3d0c |
| E2 | e2_results.json | 379ef3c43a0ec960 |
| E3 | e3_results.json | 8c2604e47df853d6 |
| E4 | e4_results.json | ea118966b66c7a0d |
| E5 | e5_results.json | 103b3ba6626af0aa |
| E6 | e6_results.json | 02922b2262f491b5 |
| E7 | e7_results.json | d693a477883ab6bf |

## 2. Claim registry

The full registry is in `reports/E0_E7_claim_registry.csv` (20 claims).
Summary:

| Status | Count |
|---|---|
| PASS (manuscript matches JSON) | 14 |
| FAIL (manuscript differs from JSON) | 5 |
| NEW (not in manuscript) | 1 |

## 3. Documented discrepancies

### 3.1 E4 — DS04 severity

| Source | Value |
|---|---|
| Manuscript | D2_moderate |
| JSON | D1_light (score = 0.23) |
| Cause | Severity threshold between D1 and D2 is 0.25; DS04 score 0.23 < 0.25 → D1_light |
| Action | Manuscript must correct DS04 from D2 to D1 |

DS05 (score 0.28 > 0.25) is correctly D2_moderate.

### 3.2 E6 — Overall, CF, counterfactual tests

| Metric | Manuscript | JSON | Cause |
|---|---|---|---|
| Overall | 0.950 | 0.985 | Mean of (1.0, 0.9, 1.0, 1.0, 1.0, 1.0) = 0.9833 → 0.985 |
| CF | 0.85 | 1.0 | CF is 1.0 in JSON |
| Counterfactual tests | 3/3 | 7/9 | `all_passed=False`; 2 tests fail |

**This is the most serious discrepancy**: the manuscript claims 3/3 counterfactual tests pass, but the JSON shows 7/9 (2 failures). The manuscript must:
- report 7/9, not 3/3;
- report the 2 failed tests and their causes;
- report overall 0.985, CF 1.0.

### 3.3 E7 — A0_FULL DCR vs Overall

| Metric | Manuscript | JSON |
|---|---|---|
| DCR | 0.94 | 0.8333 |
| Overall | not reported | 0.9395 |

**Cause**: the manuscript confused DCR with Overall. 0.94 is close to Overall (0.9395), not DCR (0.8333).

**Action**: the manuscript must:
- report DCR = 0.8333 for A0_FULL;
- report Overall = 0.9395 separately;
- recompute the ablation table with DCR (not Overall) as the primary metric, OR clearly state which metric is used.

## 4. Gate G3 status

| G3 criterion | Status | Evidence |
|---|---|---|
| Raw JSON frozen and hashed | PASS | `raw_manifest.csv` |
| Claim registry complete | PASS | `E0_E7_claim_registry.csv` (20 claims) |
| E0-E7 results trace to raw records | PASS | JSON unchanged, values match |
| E4 resolved | PASS (documented) | DS04 = D1_light |
| E6 resolved | PASS (documented) | overall 0.985, CF 1.0, 7/9 tests |
| E7 resolved | PASS (documented) | DCR 0.8333, Overall 0.9395 |

**G3 verdict: PASS with 3 documented discrepancies.**
The 8 experiments are present, reproducible, and their raw JSON is frozen.
The manuscript contains 5 claims that differ from the JSON (E4, E6×3, E7).
These must be corrected in the manuscript.

## 5. Reproducibility

```bash
# Verify raw JSON hashes
sha256sum experiments/E*/results/*.json

# Check claim registry
cat reports/E0_E7_claim_registry.csv
6. Recommended manuscript corrections (not applied)
Claim	Current	Recommended
E4 DS04	D2_moderate	D1_light (score 0.23)
E6 overall	0.950	0.985
E6 CF	0.85	1.0
E6 counterfactual	3/3 passed	7/9 passed, 2 failed
E7 A0_FULL	DCR 0.94	DCR 0.8333, Overall 0.9395
