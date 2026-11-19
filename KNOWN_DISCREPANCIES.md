# KNOWN_DISCREPANCIES.md

**Repository:** stevelengui/ProjetFinalRaisonnement  
**Stage:** 6.2 — Independent Scientific and Numerical Verification  
**Frozen manuscript reference:** "A Meta-Reasoning Framework for Lifecycle-Aware Hardware-Software Co-Design of Embedded AI Systems", revision of 18 November 2026  
**Status of this document:** Documentation of verified numerical discrepancies. The manuscript is **not** modified at this stage. All corrections will be consolidated after Stage 6.2.

---

## 0. Purpose and method

This document lists every numerical discrepancy detected between:

- **MS** — the frozen manuscript of 18 November 2026;
- **C-CODE** — the real C implementation (`firmware/model/model_weights.h`, `model_weights.c`, `model.c`, `model.h`), which is the **ground truth** for the deployed model;
- **PY-SIM** — the Python simulator `llm_nas/hybrid_model.py`;
- **README** — the public repository README.

Each discrepancy is documented with:
1. the values found in each source;
2. the independently verified value and the method used to obtain it;
3. the probable cause;
4. the recommended action (documentation only at this stage — no manuscript edit).

Verification scripts are provided in `scripts/`:
- `param_ledger.py` — parameter count per layer, from `model_weights.h` / `model_weights.c`;
- `memory_ledger.py` — Flash / SRAM / weights / activations / state / stack / heap breakdown, from `model.h` and `model.c`;
- `ops_ledger.py` — operation (MAC) count per layer, from `TOTAL_OPS` in `model_weights.h`.

All ledgers are machine-generated; their outputs are stored in `evidence_registry/ledgers/`.

---

## 1. Parameter count

### 1.1 Values in circulation

| Source | Value | What it actually counts |
|---|---|---|
| MS, Section VI-A (text) | **7,651** | Sum of quantized weight arrays (claimed) |
| MS, Section VI-A (layer list) | **9,317** | Sum of the seven layer counts quoted in the text |
| C-CODE, `model_weights.h` | **7,651** | Exact sum of all declared `int8_t` arrays (verified — see §1.2) |
| PY-SIM, `hybrid_model.py` | **373,128** | Hard-coded `self.total_parameters` |
| PY-SIM, `self.layers` | **9,883** | Sum of the six `LayerStats.parameters` |
| PY-SIM, allocated tensors | **205,121** | Sum of `np.random.randint` array shapes |
| README | **373,128** | Repeated from PY-SIM |

**Five different values** (7,651 / 9,317 / 9,883 / 205,121 / 373,128) appear across the four sources for what should be a single quantity.

### 1.2 Independently verified value

From `model_weights.h`, the declared array sizes are:

| Array | Size | Elements |
|---|---|---|
| `conv1_weight` | `[30]` | 30 |
| `conv1_bias` | `[6]` | 6 |
| `conv2_weight` | `[216]` | 216 |
| `conv2_bias` | `[12]` | 12 |
| `lstm_weight_ih` | `[3168]` | 3,168 |
| `lstm_weight_hh` | `[2304]` | 2,304 |
| `lstm_bias_ih` | `[96]` | 96 |
| `lstm_bias_hh` | `[96]` | 96 |
| `router_fc1_weight` | `[432]` | 432 |
| `router_fc1_bias` | `[12]` | 12 |
| `router_fc2_weight` | `[24]` | 24 |
| `router_fc2_bias` | `[2]` | 2 |
| `fusion_weight` | `[864]` | 864 |
| `fusion_bias` | `[24]` | 24 |
| `fc1_weight` | `[288]` | 288 |
| `fc1_bias` | `[12]` | 12 |
| `fc2_weight` | `[60]` | 60 |
| `fc2_bias` | `[5]` | 5 |
| **TOTAL** | | **7,651** |

**Verified value: 7,651 parameters** (all `int8_t`, 8-bit quantized).  
Method: exact sum of declared array sizes in `model_weights.h`. Reproducible with `scripts/param_ledger.py`.

### 1.3 Why the manuscript text says 9,317

The manuscript's Section VI-A lists seven layer counts:

| Layer (as quoted in MS) | MS count | C-CODE actual | Difference |
|---|---|---|---|
| Conv1D | 30 | 30 | 0 |
| Conv2D | 216 | 216 | 0 |
| LSTM | 5,472 | 3,168 + 2,304 + 96 + 96 = **5,664** | −192 |
| SNN-LIF | 2,176 | 0 declared weights (thresholds only) | +2,176 |
| Dense | 470 | 288 + 12 = **300** | +170 |
| Fusion | 888 | 864 + 24 = **888** | 0 |
| Output | 65 | 60 + 5 = **65** | 0 |
| **Sum** | **9,317** | **7,651** | **+1,666** |

The 9,317 figure is the **sum of layer counts as written in the manuscript**, not the sum of the real weight arrays. Three layer counts in the manuscript do not match the C implementation:

- **LSTM**: the manuscript writes 5,472; the C code has 3,168 (`weight_ih`) + 2,304 (`weight_hh`) + 96 (`bias_ih`) + 96 (`bias_hh`) = **5,664**.
- **SNN-LIF**: the manuscript writes 2,176; the C code declares **no trainable weights** for the LIF layer (only a threshold constant, `custom2_lif(..., 50)`).
- **Dense**: the manuscript writes 470; the C code has `fc1_weight[288] + fc1_bias[12]` = **300**. (The manuscript's 470 likely includes the router, which is counted separately in C-CODE.)

### 1.4 Why PY-SIM says 373,128

`hybrid_model.py` sets `self.total_parameters = 373128`. This is the **operation count (MACs)**, not the parameter count. The same file confirms this indirectly: the sum of `LayerStats.operation_count` across the six layers is exactly **373,128**, while the sum of `LayerStats.parameters` is 9,883 (itself inconsistent with the real model).

The file also contains internal draft comments (lines 48–68) that explicitly acknowledge the confusion ("*Wait, article says 373,128*", "*this suggests much larger hidden dimensions*"). These comments must be removed from the published code and their content is preserved here for historical traceability.

### 1.5 Probable cause

1. An early version of the manuscript conflated **operations** (373,128 MACs) with **parameters**.
2. The layer counts in Section VI-A were written from an intermediate spreadsheet, before the C implementation was finalized, and were never re-summed against `model_weights.h`.
3. `hybrid_model.py` was written as a standalone statistical simulator for the AutoCoDesign Pareto exploration; it was never aligned with the C model and kept the erroneous 373,128 as `total_parameters`.

### 1.6 Recommended action (documentation only)

- **Do not edit the manuscript at this stage.**
- Publish `scripts/param_ledger.py` and its output `evidence_registry/ledgers/param_ledger.csv`, which proves **7,651**.
- Publish this section as the explanation of the 9,317 figure.
- In the consolidated correction list (after Stage 6.2), the manuscript's Section VI-A layer table will need to be reconciled with the C arrays (LSTM 5,664, SNN-LIF 0, Dense 300).

---

## 2. Memory accounting

### 2.1 Values in circulation

| Source | Weights | Flash | SRAM | Total |
|---|---|---|---|---|
| MS, Section VI-A | 7.47 KiB | 19.47 KiB | 11.53 KiB | 31.00 KiB (sum) |
| MS, Table I (`ecg_hybrid_8bit`) | — | — | — | **29.0 KiB** |
| PY-SIM, `total_memory_bytes` | 8,736 B (8.52 KiB) | — | — | 8.52 KiB + 2.1 + 1.8 = **12.42 KiB** |
| README (`ecg_hybrid_8bit`) | — | — | — | **24 KB** |

Four different totals for the same design: **29.0 / 31.0 / 12.42 / 24**.

### 2.2 Independently verified values from C-CODE

**Weights (Flash):** 7,651 `int8_t` = **7,651 bytes = 7.47 KiB**. ✅ Matches MS Section VI-A.

**SRAM (buffers declared in `model.h`):**

| Buffer | Elements | Element size | Bytes |
|---|---|---|---|
| `input_buf[360]` | 360 | 1 | 360 |
| `conv1_out[6×180]` | 1,080 | 4 | 4,320 |
| `conv2_out[12×90]` | 1,080 | 4 | 4,320 |
| `snn_input[33×32]` | 1,056 | 1 | 1,056 |
| `spike_train[32×24]` | 768 | 1 | 768 |
| `lstm_state[24]` | 24 | 1 | 24 |
| `router_output[2]` | 2 | 1 | 2 |
| `fused_features[24]` | 24 | 4 | 96 |
| `fc1_out[12]` | 12 | 4 | 48 |
| `output[5]` | 5 | 4 | 20 |
| `precision_mode` | 1 | 1 | 1 |
| `temperature` | 1 | 2 | 2 |
| `total_cycles` | 1 | 4 | 4 |
| `inference_count` | 1 | 4 | 4 |
| **Sum of struct fields** | | | **11,025 B ≈ 10.77 KiB** |

The manuscript reports **11.53 KiB SRAM**. Difference: **0.76 KiB ≈ 778 bytes**, attributable to:
- local arrays in `model_predict` (`spatial_features[12]`, `snn_features[24]`, `qnn_features[12]` = 48 bytes);
- stack frame, alignment, and compiler-allocated temporaries.

This is plausible and will be confirmed by `scripts/memory_ledger.py` combined with `riscv64-unknown-elf-size` on the compiled ELF.

**Flash (code):** MS reports 19.47 KiB total Flash, of which 7.47 KiB weights → **12.0 KiB code**. This must be confirmed by `size` on the cross-compiled ELF (see `IMPLEMENTATION_VALIDATION.md`).

### 2.3 The 29.0 KiB vs 31.0 KiB discrepancy (Table I vs Section VI-A)

- Section VI-A: Flash 19.47 + SRAM 11.53 = **31.00 KiB**.
- Table I: **29.0 KiB** for `ecg_hybrid_8bit`.

Difference: **2.0 KiB**. Probable causes (to be confirmed by `memory_ledger.py`):
- Table I may exclude the stack/heap or a reserved region;
- Table I may have been rounded or computed from an earlier model revision;
- Section VI-A may double-count a buffer.

**Verified value for the struct alone: 10.77 KiB SRAM + 7.47 KiB weights = 18.24 KiB.** Neither 29.0 nor 31.0 is directly reproducible from the C declarations alone; both require the code size and stack allocation from the compiled binary. This is documented here as an **open item** for Stage 6.2, to be closed by the ELF `size` output.

### 2.4 PY-SIM and README values

- `hybrid_model.py` reports `total_memory_bytes = 8736` (8.52 KiB) for weights, but its allocated tensors total **205,121 bytes** (8-bit) — a factor of ~23 discrepancy. The 8,736 figure is arbitrary.
- The README reports 24 KB for `ecg_hybrid_8bit`, 12 KB for `ecg_hybrid_4bit`, 32 KB for `vibration_hybrid_8bit`, 4 KB for `iot_snn_lowpower`. None matches Table I of the manuscript (29.0 / 14.5 / 38.0 / 8.0 KiB). The README was not updated after the manuscript was corrected.

### 2.5 Recommended action (documentation only)

- Publish `scripts/memory_ledger.py` and its output, with the struct breakdown above (verified 10.77 KiB) and the ELF-based code/stack figures.
- Document the 29.0 vs 31.0 discrepancy as an **open item**, to be resolved by the ELF `size` output.
- In the consolidated correction list, align Table I and Section VI-A on a single accounting convention (e.g., "weights + code + declared buffers + measured stack").

---

## 3. Operation count

### 3.1 Values in circulation

| Source | Value |
|---|---|
| MS, Section VI-A | **373,128** operations per inference |
| C-CODE, `model_weights.h` (`TOTAL_OPS`) | **373,128** |
| PY-SIM, sum of `operation_count` | **373,128** |
| PY-SIM, `total_parameters` | **373,128** (mislabeled) |

### 3.2 Independently verified value

From `model_weights.h`:

| Macro | Expression | Value |
|---|---|---|
| `CONV1_OPS` | `6 × 180 × 5 × 2` | 10,800 |
| `CONV2_OPS` | `12 × 90 × 3 × 2` | 6,480 |
| `LSTM_OPS` | `4 × 24 × (33 + 24) × 32 × 2` | 350,208 |
| `LIF_OPS` | `32 × 24 × 3` | 2,304 |
| `FC_OPS` | `(24 × (12 + 24) + 12 × 24 + 5 × 12) × 2` | 2,424 |
| `ROUTER_OPS` | `(12 × (12 + 24) + 2 × 12) × 2` | 912 |
| **`TOTAL_OPS`** | sum | **373,128** |

**Verified value: 373,128 MACs per inference.** ✅ This is correct in the C code and in the manuscript. The only error is that PY-SIM and README label this number as "parameters".

### 3.3 Recommended action (documentation only)

- Publish `scripts/ops_ledger.py` and its output.
- No manuscript change needed for the 373,128 figure itself — only for its **label** (operations, not parameters) in the README and PY-SIM.

---

## 4. Quantized weights ↔ architecture correspondence

### 4.1 Status

The C implementation (`model_weights.c`) loads its weights from `arrays/*.txt` via `#include`. The C header declares exact array sizes that match the architecture in `model_weights.h` (INPUT_SIZE 360, CONV1_FILTERS 6, CONV2_FILTERS 12, LSTM_HIDDEN 24, SNN_HIDDEN 24, OUTPUT_SIZE 5, TIME_STEPS 32, FUSION_SIZE 24, FC1_SIZE 12).

The Python simulator (`hybrid_model.py`) uses **different dimensions** (Conv1D 32 filters, Conv2D 64, LSTM 128 hidden, FC1 256, FC2 64). It therefore **does not correspond** to the C architecture.

### 4.2 Verified correspondence

The correspondence between exported quantized weights and the C architecture is **verified** for the C path: the array sizes in `model_weights.h` match the layer dimensions in the same header.

The correspondence between the Python simulator and the C architecture is **not verified** and **cannot be** in the current state, because the simulator uses different dimensions. This will be resolved by the rewritten `hybrid_model.py` (see §5).

### 4.3 Recommended action (documentation only)

- Publish the rewritten `hybrid_model.py` aligned on the C dimensions (Conv1D 6, Conv2D 12, LSTM 24, etc.), with the same totals (7,651 parameters, 373,128 MACs).
- Publish a `pytest`-style equivalence test between Python and C (see `IMPLEMENTATION_VALIDATION.md`).

---

## 5. Cross-cutting discrepancies (README vs manuscript vs code)

| Item | README | MS (18 Nov) | C-CODE | Verified |
|---|---|---|---|---|
| `ecg_hybrid_8bit` memory | 24 KB | 29.0 KiB (Table I) / 31.0 KiB (VI-A) | 10.77 KiB buffers + 7.47 KiB weights | Open (ELF pending) |
| `ecg_hybrid_4bit` memory | 12 KB | 14.5 KiB | — | Open |
| `vibration_hybrid_8bit` memory | 32 KB | 38.0 KiB | — | Open |
| `iot_snn_lowpower` memory | 4 KB | 8.0 KiB | — | Open |
| MAML retention | 99 % | 1 tool among 8 (E4) | — | README claim not supported |
| "Sans MAML → −4.1 % accuracy" | presented as accuracy gain | E7 measures DCR, not accuracy | — | README metric mismatch |
| Domains validated | implied 5 | 2 (medical, industrial) | — | README overstates |
| Parameter count | 373,128 | 7,651 | 7,651 | **7,651** |

### 5.1 Recommended action (documentation only)

- Update the README to align with the frozen manuscript (7,651 parameters, 2 domains validated, no 99 % MAML claim, no −4.1 % accuracy claim).
- Do **not** modify the manuscript.

---

## 6. Summary table of verified values

| Quantity | Verified value | Method | Source |
|---|---|---|---|
| Parameters | **7,651** | Sum of `int8_t` arrays in `model_weights.h` | C-CODE |
| Operations per inference | **373,128** | Sum of `TOTAL_OPS` macros | C-CODE |
| Weights memory | **7.47 KiB** | 7,651 × 1 byte | C-CODE |
| SRAM (struct only) | **10.77 KiB** | Sum of `HybridModelBuffers` fields | C-CODE |
| Flash (code) | **12.0 KiB** (claimed) | 19.47 − 7.47 | MS, to confirm via ELF |
| Total memory (Table I) | **29.0 KiB** (claimed) | — | MS, **open item** |
| Total memory (VI-A) | **31.00 KiB** (claimed) | 19.47 + 11.53 | MS, **open item** |

---

## 7. Open items for Stage 6.2

The following items cannot be closed from the C declarations alone and require the compiled ELF, the linker script, and the simulator rewrite:

1. Exact code size (Flash) from `riscv64-unknown-elf-size`.
2. Exact stack/heap allocation from the linker script.
3. Reconciliation of Table I (29.0 KiB) with Section VI-A (31.00 KiB).
4. Rewritten `hybrid_model.py` aligned on C dimensions.
5. Parameter ledger CSV for the 8 designs in `real_designs.py` (not just `ecg_hybrid_8bit`).

Each of these items will be addressed in `NUMERICAL_VERIFICATION.md` and `IMPLEMENTATION_VALIDATION.md`.

---

## 8. Statement of compliance with Stage 6.2 instructions

- The manuscript of 18 November 2026 has **not** been modified.
- All values above are documented from the repository's own code.
- No result has been overwritten; the original `hybrid_model.py` is preserved in `legacy/hybrid_model_v0.py` for traceability.
- All scripts are reproducible and their outputs are stored in `evidence_registry/ledgers/`.

---

*End of KNOWN_DISCREPANCIES.md*
