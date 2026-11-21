# WP1 — Numerical and resource reconciliation

**Date:** 20 November 2026
**Branch:** `stage-6.3-corrections`
**Gate:** G1
**Status:** reconciling

## 1. Parameter count

Four different values appear in the repository:

| Source | Value | Definition | Status |
|---|---|---|---|
| Manuscript §VI-A (text) | 7,651 | Sum of exported C arrays | ✅ verified |
| Manuscript §VI-A (layer list) | 9,317 | Sum of manuscript layer counts | ⚠️ manuscript error |
| Python simulator `hybrid_model.py` | 373,128 | `total_parameters` (mislabeled) | ❌ wrong label |
| README (v6.2) | 373,128 | repeated from Python | ❌ wrong label |

### Verified value: 7,651

From `evidence_registry/derived/parameter_tensors.csv`:

| Layer | Arrays | Parameters |
|---|---|---|
| Conv1D | `conv1_weight`, `conv1_bias` | 30 + 6 = 36 |
| Conv2D | `conv2_weight`, `conv2_bias` | 216 + 12 = 228 |
| LSTM | `lstm_weight_ih`, `lstm_weight_hh`, `lstm_bias_ih`, `lstm_bias_hh` | 3,168 + 2,304 + 96 + 96 = 5,664 |
| Router | `router_fc1_weight`, `router_fc1_bias`, `router_fc2_weight`, `router_fc2_bias` | 432 + 12 + 24 + 2 = 470 |
| Fusion | `fusion_weight`, `fusion_bias` | 864 + 24 = 888 |
| Classifier fc1 | `fc1_weight`, `fc1_bias` | 288 + 12 = 300 |
| Classifier fc2 | `fc2_weight`, `fc2_bias` | 60 + 5 = 65 |
| **Total** | 18 arrays | **7,651** |

### Why the manuscript says 9,317

| Layer | Manuscript | C code | Difference |
|---|---|---|---|
| Conv1D | 30 | 30 | 0 |
| Conv2D | 216 | 216 | 0 |
| LSTM | 5,472 | 5,664 | −192 |
| SNN-LIF | 2,176 | 0 | +2,176 |
| Dense | 470 | 300 (fc1 only) | +170 |
| Fusion | 888 | 888 | 0 |
| Output | 65 | 65 | 0 |
| **Sum** | **9,317** | **7,651** | **+1,666** |

The manuscript counts:
- LSTM as 5,472 (it is 5,664 in the C arrays: 3,168 + 2,304 + 96 + 96).
- SNN-LIF as 2,176 (there are **no trainable weights** for LIF; only a threshold constant).
- Dense as 470 (this includes the router: 432+12+24+2=470; the actual fc1 is 288+12=300, and the router is counted separately).

### Why 373,128 is not a parameter count

From `llm_nas/model_weights.h`:
#define TOTAL_OPS (CONV1_OPS + CONV2_OPS + LSTM_OPS + LIF_OPS + FC_OPS + ROUTER_OPS) // 373128

text

This is the **operation count (MACs per inference)**, not a parameter count. The Python simulator `hybrid_model.py` sets `self.total_parameters = 373128`, which is a **labeling error** that has been documented in `KNOWN_DISCREPANCIES.md` §1.4.

## 2. Operation count

### Verified value: 373,128 MACs

From `llm_nas/model_weights.h`:

| Macro | Expression | Value |
|---|---|---|
| `CONV1_OPS` | `6 × 180 × 5 × 2` | 10,800 |
| `CONV2_OPS` | `12 × 90 × 3 × 2` | 6,480 |
| `LSTM_OPS` | `4 × 24 × (33 + 24) × 32 × 2` | 350,208 |
| `LIF_OPS` | `32 × 24 × 3` | 2,304 |
| `FC_OPS` | `(24 × (12 + 24) + 12 × 24 + 5 × 12) × 2` | 2,424 |
| `ROUTER_OPS` | `(12 × (12 + 24) + 2 × 12) × 2` | 912 |
| **`TOTAL_OPS`** | sum | **373,128** |

**Definition:** this is a **static macro sum** (DER = derived, not measured). It is not a cycle trace and does not prove a real inference has been performed. WP2 will instrument the C to count executed operations.

## 3. Memory accounting

Three different memory values appear in the repository:

| Source | Value | Definition | Status |
|---|---|---|---|
| Manuscript Table I | 29.0 KiB | aggregate footprint | ⚠️ open |
| Manuscript §VI-A | 19.47 KiB Flash + 11.53 KiB SRAM = 31.0 KiB | sum of two regions | ⚠️ open |
| Struct SRAM (from `model.h`) | 11,025 bytes = 10,767 KiB | sum of buffer fields | ✅ verified |
| Header constants | `M_WEIGHTS_BYTES=7651`, `M_CODE_BYTES=12288`, `M_ACTIVATION_PEAK_BYTES=11014`, `M_RUNTIME_BYTES=2560` | declared constants | ⚠️ provenance unknown |

### Verified values

| Quantity | Value | Method |
|---|---|---|
| Weights | 7,651 B = 7.47 KiB | sum of 18 arrays |
| Struct SRAM | 11,025 B = 10.767 KiB | sum of `HybridModelBuffers` fields |
| `M_CODE_BYTES` | 12,288 B = 12.0 KiB | header constant |
| Flash (weights + code) | 19.47 KiB | 7.47 + 12.0 (consistent with §VI-A) |
| `M_ACTIVATION_PEAK_BYTES` | 11,014 B = 10.756 KiB | header constant (11 bytes less than struct) |
| `M_RUNTIME_BYTES` | 2,560 B = 2.5 KiB | header constant |

### Open items

1. **Table I 29.0 KiB vs §VI-A 31.0 KiB:** difference of 2.0 KiB. Possible causes: Table I excludes stack/heap, or uses a different accounting convention. **UNVERIFIED** until a compiled ELF section report is available.
2. **`M_ACTIVATION_PEAK_BYTES` (11,014) vs struct SRAM (11,025):** difference of 11 bytes. Likely alignment/padding. **UNVERIFIED**.
3. **`M_RUNTIME_BYTES` (2,560):** provenance unknown (not in `model.c`, `model.h`, or `model_weights.h`). **UNVERIFIED**.

## 4. Stored vs executed parameters

From `architecture_weight_map.md`:

| Status | Tensors | Parameters |
|---|---|---|
| IMPLEMENTED (with learned values) | 8 | 629 |
| DIVERGENT (executed, but C differs from PyTorch) | 4 | 5,664 |
| UNUSED (stored but never executed) | 6 | 1,358 |
| **Total** | 18 | **7,651** |

**Critical finding:** the `fusion_weight` and `fusion_bias` (888 parameters) are stored but never used in `model.c`. The router weights (470 parameters) are also stored but unused (the C uses a heuristic). This means that **1,358 parameters (17.8%) are declared but not part of the executed model**.

## 5. Gate G1 status

| Criterion | Status | Evidence |
|---|---|---|
| Tensor/operation/memory accounting reconciled | ⚠️ **PARTIAL** | 7,651 and 373,128 verified; memory Table I vs §VI-A open |
| Reproducible | ✅ **YES** | `parameter_tensors.csv`, `ops_ledger.csv`, `memory_ledger.csv` |
| Unambiguous definition | ⚠️ **PARTIAL** | 7,651 = exported arrays; 9,317 = manuscript layer counts; 373,128 = MACs |
| Arithmetic and implementation agree | ✅ **YES** for parameters | 7,651 = sum of declared arrays |
| Stored vs executed distinguished | ✅ **YES** | 1,358 parameters unused |

**G1 verdict: PARTIAL PASS**
- Parameters: PASS (7,651 verified, 9,317 explained).
- Operations: PASS (373,128 = MACs).
- Memory: UNVERIFIED (Table I vs §VI-A not reconciled without ELF).
- Stored vs executed: PASS (1,358 unused parameters documented).

## 6. Recommended manuscript corrections (not applied)

| Claim | Current wording | Recommended wording |
|---|---|---|
| Parameters | "7,651 parameters" | "7,651 exported parameters (6,293 executed, 1,358 stored but unused)" |
| Operations | "373,128 operations" | "373,128 MACs (static macro sum, DER)" |
| Memory | "29.0 KiB" (Table I) | "31.0 KiB aggregate (19.47 KiB Flash + 11.53 KiB SRAM)" or "10.767 KiB struct SRAM" |
| SNN-LIF | "2,176 parameters" | "0 trainable weights; threshold-based LIF" |
| Dense | "470 parameters" | "300 parameters (fc1); router 470 counted separately" |
| LSTM | "5,472 parameters" | "5,664 parameters (3,168+2,304+96+96)" |

## 7. Reproducibility

```bash
# Parameter tensors
python3 scripts/param_tensors_ledger.py

# Operations
python3 scripts/ops_ledger.py --header llm_nas/model_weights.h --out evidence_registry/derived/ops_ledger.csv

# Memory
python3 scripts/memory_ledger.py --model-h firmware/model/model.h --weights-h llm_nas/model_weights.h --out evidence_registry/derived/memory_ledger.csv
