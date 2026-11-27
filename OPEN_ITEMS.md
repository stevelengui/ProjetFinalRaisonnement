# OPEN_ITEMS.md — Stage 6.3 (updated)

**Date:** 26 November 2026
**Branch:** `stage-6.3-corrections`
**Base tag:** `v6.3-corrections` (commit 4a95a52)
**Status:** Updated with B10 precision (8 blockers clarified)

This file lists the limitations and unresolved issues that must be addressed
in a future stage (6.4 or manuscript revision).

## 0. Top blockers (P0)

| Blocker | Status | Action |
|---|---|---|
| Real quantization scales UNKNOWN | P0 | Declared values (1, 2, 3) are placeholders. Without true scales, no C ↔ trained Python equivalence can be proven. Regenerate from model.py or document as a limitation. |
| C ↔ PyTorch divergence (100%) | P0 | C omits BatchNorm, uses heuristic router/fusion, LSTM-LIF. Either correct the C or reduce the "numerical equivalence" claim. |
| E4 DS04 (D1_light, score 0.23) | P0 | Manuscript says D2_moderate. The "severe domain shift" claim is overstated. |
| E6 counterfactual (7/9, not 3/3) | P0 | The "counterfactual fidelity" claim is partial. Disclose 2 failures. |
| E7 A0_FULL DCR (0.8333, not 0.94) | P0 | Manuscript confuses DCR with Overall (0.9395). The "meta efficiency" claim is overstated. |
| Latency 8.2 ms (ANA, not measured) | P0 | QEMU gives 40.75 ms (5x slower). Label as ANA estimate. |
| TOPS/W 4.7 (ANA, not measured) | P0 | QEMU gives 5447.9 (calculation error). Label as ANA estimate. |

## 1. WP1 — Numerical reconciliation (G1 = PARTIAL PASS)

**PASS**: parameters (7,651 = 18 arrays), operations (373,128 MACs).
**UNVERIFIED**: memory Table I (29.0 KiB) vs VI-A (31.0 KiB); real quantization scales.
**DOCUMENTED**: 1,358 parameters (fusion + router) stored but not executed.

| Item | Status | Action |
|---|---|---|
| Manuscript 9,317 vs code 7,651 | documented | correct layer counts (LSTM 5,664, SNN-LIF 0, Dense 300) |
| Memory Table I vs VI-A | UNVERIFIED | need ELF section report or explicit convention |
| Stored vs executed parameters | documented | 1,358 parameters (fusion + router) stored but not executed |

## 2. WP2 — Implementation equivalence (G2 = PASS with divergence)

**BLOCKER P0**: C ↔ PyTorch divergence (100%). Four technical debts:

| Technical debt | Detail |
|---|---|
| BatchNorm omitted | bn1_*, bn2_* exist in arrays/ but not in model_weights.h and not used in model.c |
| Router heuristic | feature_router returns 89/51/70 based on energy, ignores router_fc1/router_fc2 weights |
| Fusion heuristic | dynamic_fusion_rv32x uses custom3_fusion, ignores fusion_weight/fusion_bias (888 params stored but unused) |
| LSTM-LIF | quantized_lstm_layer_rv32x uses custom2_lif instead of sigmoid/tanh |

**C logits near-uniform** (`0 -1 -1 -1 0`): model does not discriminate classes; consistent with placeholder scales.

## 3. WP3 — Experimental evidence (G3 = PASS with 3 discrepancies)

| Item | Status | Action |
|---|---|---|
| E4 DS04 | manuscript overestimates severity | DS04 = D1_light (score 0.23), not D2. |
| E6 counterfactual | manuscript overestimates fidelity | 7/9 tests pass (not 3/3). Disclose 2 failures. |
| E7 A0_FULL DCR | manuscript overestimates meta efficiency | DCR = 0.8333 (not 0.94); Overall = 0.9395. |

## 4. WP4 — RISC-V validation (G2 = PASS, no physical validation)

| Item | Status | Action |
|---|---|---|
| Physical validation | NOT PERFORMED (B10 A6) | Build + QEMU executed, but no physical board. Distinguish: cross-compiled (K210) → executed (QEMU) → physically measured (none). |
| QEMU latency (40.75 ms) | SIM | Cannot confirm manuscript 8.2 ms. Label as SIM. |

## 5. WP5 — Hardware performance (G4 = PASS with honest labels)

**Path B (honest choice)**: no cycle-accurate simulator is available. All metrics are classified MEAS/SIM/ANA/DER. This is not a failure; it is a documented limitation.

| Item | Status | Action |
|---|---|---|
| Latency 8.2 ms | ANA (estimate) | label as ANA, not measured |
| Energy 2.8 mJ | ANA (estimate) | label as ANA, not measured |
| TOPS/W 4.7 | ANA (estimate) | label as ANA; QEMU gives 5447.9 (calc error) |
| Flash 19.47 KiB | ANA (estimate) | need ELF size to confirm |

## 6. WP6 — Meta-controller (G3/G4 = PARTIAL PASS)

**Covered (5 deterministic cases PASS)**: missing_evidence, contradictory_evidence, hard_security_failure, lifecycle_drift, resource_infeasibility.
**Missing (6 cases required by B10)**: clear feasible, uncertain boundary, conflicting evidence, missing mandatory reliability evidence, no feasible candidate, budget exhaustion → DEFER.

## 7. Summary

- **G1**: PARTIAL PASS (parameters and operations PASS; memory UNVERIFIED; scales UNKNOWN)
- **G2**: PASS with divergence (C real and reproducible; PyTorch equivalence FAIL)
- **G3**: PASS with 3 discrepancies (E4, E6, E7 documented)
- **G4**: PASS with honest classification (ANA/SIM/DER labeled)

**The manuscript must be revised (after Stage 6.4 audit) to:**
1. Correct layer counts (LSTM 5,664, SNN-LIF 0, Dense 300).
2. Correct E4 DS04 (D1_light).
3. Correct E6 (overall 0.985, CF 1.0, 7/9 tests).
4. Correct E7 (DCR 0.8333, Overall 0.9395).
5. Label latency, energy, TOPS/W as ANA (estimates).
6. Disclose C ↔ PyTorch divergence.
7. Provide real quantization scales or document as limitation.
