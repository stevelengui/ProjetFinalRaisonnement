# Stage 6.3 — WP1-WP6 Implementation Guide

**Branch:** `stage-6.3-corrections`
**Frozen reference:** manuscript of 18 November 2026, tag `v6.2-verification` (unmodified)
**Status:** Work in progress. This README will be updated as each WP is completed.

## Work packages

| WP | Title | Priority | Gate | Status |
|---|---|---|---|---|
| WP1 | Numerical and resource accounting | P0 | G1 | in progress |
| WP2 | Real quantized inference and Python-C equivalence | P0 | G2 | not started |
| WP3 | Canonical E0-E7 evidence reconciliation | P0 | G3 | not started |
| WP4 | Complete RISC-V artifact and memory validation | P0 | G2 | not started |
| WP5 | Honest latency, energy and simulation evidence | P0 | G4 | not started |
| WP6 | Operational meta-policy evidence | P1 | G3/G4 | not started |

## Acceptance gates

| Gate | PASS condition | FAIL condition | UNVERIFIED condition |
|---|---|---|---|
| G1 | Tensor/operation/memory accounting reconciled and reproducible | Conflicting definitions, arithmetic mismatch | Missing trained weights or stack evidence |
| G2 | Real input-dependent C inference; genuine parity; complete RISC-V build; runtime status explicit | Hard-coded PASS, synthetic logits, incomplete ELF | No reference weights or execution environment |
| G3 | E0-E7 results and metrics trace to raw records; E4/E6/E7 resolved | Cherry-picking, mismatched DCR, hidden failed checks | Missing oracle, seeds or case-level data |
| G4 | Each claim matches measured/simulated/estimated evidence | Unsupported cycle-accurate or physical claims | Missing simulation calibration |

## Constraints

1. The manuscript of 18 November 2026 and tag `v6.2-verification` are kept unchanged.
2. All corrections are done on branch `stage-6.3-corrections` with traceable commits.
3. Experimental protocols are respected; no unjustified changes to configurations or metrics.
4. Positive, negative, and unverified results are documented.
5. A versioned ZIP package will be produced with sources, scripts, results, logs, and the G1-G4 compliance matrix.

## Document index

- `BASELINE.md` — frozen inputs, canonical repositories, environment
- `reports/WP1_reconciliation.md` — WP1 deliverable
- `reports/WP2_validation.md` — WP2 deliverable
- `reports/WP3_experiment_audit.md` — WP3 deliverable
- `reports/WP4_riscv.md` — WP4 deliverable
- `reports/WP5_evidence_classification.csv` — WP5 deliverable
- `reports/WP6_meta_policy.md` — WP6 deliverable
- `reports/G1_G4_acceptance_matrix.csv` — final acceptance matrix
