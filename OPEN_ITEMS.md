# OPEN_ITEMS.md — Stage 6.3

**Date:** 20 November 2026
**Branch:** `stage-6.3-corrections`

This file lists the limitations and unresolved issues that must be addressed
in a future stage (6.4 or manuscript revision).

## 1. Numerical reconciliation (WP1)

| Item | Status | Action |
|---|---|---|
| Manuscript 9,317 vs code 7,651 | documented | manuscript must correct layer counts (LSTM 5,664, SNN-LIF 0, Dense 300) |
| Memory Table I 29.0 vs VI-A 31.0 KiB | UNVERIFIED | need ELF section report or explicit convention |
| Stored vs executed parameters | documented | 1,358 parameters (fusion + router) are stored but unused |

## 2. Implementation equivalence (WP2)

| Item | Status | Action |
|---|---|---|
| C vs PyTorch numerical equivalence | FAIL (documented) | C omits BatchNorm, uses heuristic router/fusion, LSTM-LIF |
| Real quantization scales | UNKNOWN | declared values (1, 2, 3) are placeholders; real scales not in repo |
| C logits near-uniform (0 -1 -1 -1 0) | documented | model does not discriminate classes; consistent with placeholder scales |

## 3. Experimental evidence (WP3)

| Item | Status | Action |
|---|---|---|
| E4 DS04 (D1_light, score 0.23) | documented | manuscript says D2_moderate — must correct |
| E6 overall (0.985 vs 0.950) | documented | manuscript must correct |
| E6 CF (1.0 vs 0.85) | documented | manuscript must correct |
| E6 counterfactual (7/9 vs 3/3) | documented | manuscript must correct, disclose 2 failures |
| E7 A0_FULL DCR (0.8333 vs 0.94) | documented | manuscript confuses DCR with Overall (0.9395) |

## 4. RISC-V validation (WP4)

| Item | Status | Action |
|---|---|---|
| Physical validation on K210/HiFive1 | NOT PERFORMED | no hardware board available |
| QEMU execution (SIM, not cycle-accurate) | PASS | QEMU latency (40.75 ms) cannot confirm manuscript 8.2 ms |

## 5. Hardware performance (WP5)

| Item | Status | Action |
|---|---|---|
| Latency 8.2 ms | ANA (estimate) | manuscript must label as ANA, not measured |
| Energy 2.8 mJ | ANA (estimate) | manuscript must label as ANA, not measured |
| TOPS/W 4.7 | ANA (estimate) | manuscript must label as ANA; QEMU gives 5447.9 (calc error) |
| Flash 19.47 KiB | ANA (estimate) | need ELF size to confirm |

## 6. Meta-reasoning (WP6)

| Item | Status | Action |
|---|---|---|
| Controller executable | PASS | 5 test cases run |
| Baseline comparison (fixed workflow, no-EVI) | PARTIAL | may need additional ablation |

## 7. Summary

- **G1**: PARTIAL PASS (parameters and operations PASS; memory UNVERIFIED)
- **G2**: PASS with divergence (C real and reproducible; PyTorch equivalence FAIL)
- **G3**: PASS with 3 discrepancies (E4, E6, E7 documented)
- **G4**: PASS with honest classification (ANA/SIM/DER labeled)

**The manuscript must be revised (after Stage 6.4 audit) to:**
1. Correct layer counts (LSTM 5,664, SNN-LIF 0, Dense 300).
2. Correct E4 DS04 (D1_light).
3. Correct E6 (overall 0.985, CF 1.0, 7/9 tests).
4. Correct E7 (DCR 0.8333, Overall 0.9395).
5. Label latency, energy, TOPS/W as ANA (estimates), not measurements.
6. Disclose that the C inference is not numerically equivalent to PyTorch.
