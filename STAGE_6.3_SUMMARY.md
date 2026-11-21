# STAGE 6.3 — Executive Summary

**Date:** 20 November 2026
**Branch:** `stage-6.3-corrections`
**Frozen reference:** manuscript of 18 November 2026 (unmodified)

## What was done

Six work packages (WP1-WP6) were completed per the supervisor's Stage 6.3 guide.
The frozen manuscript and tag v6.2-verification were not modified.

| WP | Deliverable | Verdict |
|---|---|---|
| WP1 | Numerical reconciliation | G1 = PARTIAL PASS |
| WP2 | Real C inference + Python-C equivalence | G2 = PASS with divergence |
| WP3 | E0-E7 reconciliation | G3 = PASS with 3 discrepancies |
| WP4 | RISC-V build + QEMU execution | G2 = PASS (no physical validation) |
| WP5 | Hardware metric classification | G4 = PASS with honest labels |
| WP6 | Meta-controller operational tests | G3/G4 = PASS |

## Key results

- **Parameters**: 7,651 verified (18 arrays); manuscript 9,317 explained (3 layer errors).
- **Operations**: 373,128 MACs verified.
- **C vs Python C-faithful**: exact match (`0 -1 -1 -1 0`).
- **C vs PyTorch**: 100% divergence (documented: BatchNorm, router, fusion, LSTM-LIF).
- **RISC-V**: cross-compiled and executed in QEMU; logits match host (`0 -1 -1 -1 0`).
- **E4/E6/E7**: 5 discrepancies documented (manuscript must be corrected).
- **Hardware**: latency/energy/TOPS-W labeled ANA (estimates), not measurements.
- **Meta-controller**: 5 deterministic tests pass.

## Reproducible commands

```bash
python3 scripts/param_ledger.py --header llm_nas/model_weights.h --out evidence_registry/derived/param_ledger.csv
python3 tests/compare_c_python.py
python3 tests/negative_controls.py
python3 tests/wp6_operational/run_wp6_tests.py
What the manuscript must change (after Stage 6.4)
Correct layer counts (LSTM 5,664, SNN-LIF 0, Dense 300).

Correct E4 DS04 (D1_light).

Correct E6 (overall 0.985, CF 1.0, 7/9 tests).

Correct E7 (DCR 0.8333, Overall 0.9395).

Label latency/energy/TOPS-W as ANA (estimates).

Disclose C-PyTorch divergence.

Unresolved items (see OPEN_ITEMS.md)
Memory Table I vs VI-A (29.0 vs 31.0 KiB) — UNVERIFIED.

Real quantization scales — UNKNOWN.

Physical validation — NOT PERFORMED.

Baseline comparison for meta-controller — PARTIAL.
