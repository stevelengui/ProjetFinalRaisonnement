# WP1 — Architecture-to-weight map

**Date:** 20 November 2026
**Branch:** `stage-6.3-corrections`
**Sources inspected:**
- `firmware/model/model.c` (C inference, canonical for Paper 2)
- `firmware/model/model_weights.h` (18 weight declarations)
- `ECG-Hybrid-SNN-QNN/model.py` (PyTorch training script, attached separately)
- `ops/math_ops.c` (C operator implementations)

## Status vocabulary

- **IMPLEMENTED**: the operator is executed in `model.c` with the declared weights.
- **OMITTED**: the operator exists in PyTorch but is absent from the C inference.
- **UNUSED**: the weight is declared and exported, but never used in `model.c`.
- **DIVERGENT**: the operator exists in both, but the C implementation differs from PyTorch.
- **UNKNOWN**: the operator or weight could not be verified.

## Block-by-block mapping

| PyTorch block | C operator | Weight symbols | Dimensions | Status | Notes |
|---|---|---|---|---|---|
| `conv_blocks.0` (Conv1d + BatchNorm + ReLU + Dropout) | `quantized_conv1d_rv32x` (model.c:49) | `conv1_weight`, `conv1_bias` | [6,1,5]=30, [6]=6 | **IMPLEMENTED (conv)** / **OMITTED (BN, Dropout)** | BN weights not exported; Dropout is inference-inactive |
| `conv_blocks.4` (Conv1d + BatchNorm + ReLU + Dropout) | `quantized_conv1d_rv32x` (model.c:63) | `conv2_weight`, `conv2_bias` | [12,6,3]=216, [12]=12 | **IMPLEMENTED (conv)** / **OMITTED (BN, Dropout)** | BN weights not exported |
| `lstm` (nn.LSTM(33, 24)) | `quantized_lstm_layer_rv32x` (model.c:101) | `lstm_weight_ih`, `lstm_weight_hh`, `lstm_bias_ih`, `lstm_bias_hh` | [96,33]=3168, [96,24]=2304, [96]=96, [96]=96 | **DIVERGENT** | C uses `custom2_lif` instead of sigmoid/tanh; missing 4-gate structure |
| SNN-LIF (LIFNeuron) | `custom2_lif` (in model.c loop) | — (threshold-based, no weights) | — | **DIVERGENT** | PyTorch `LIFNeuron` has decay=0.95, threshold=0.5; C uses threshold=50, no decay |
| `feature_router.0` (Linear(36, 12)) + `feature_router.2` (Linear(12, 2)) | `feature_router` heuristic (model.c) | `router_fc1_weight`, `router_fc1_bias`, `router_fc2_weight`, `router_fc2_bias` | 432+12, 24+2 | **UNUSED** | C uses energy heuristic (returns 89/51/70), not the learned weights |
| `fusion_layer` (Linear(36, 24)) | `dynamic_fusion_rv32x` (model.c:132) | `fusion_weight`, `fusion_bias` | [24,36]=864, [24]=24 | **UNUSED** | C uses `custom3_fusion` (attention heuristic), not the learned weights |
| `classifier.0` (Linear(24, 12)) | fc1 loop (model.c) | `fc1_weight`, `fc1_bias` | [12,24]=288, [12]=12 | **IMPLEMENTED** | |
| `classifier.3` (Linear(12, 5)) | fc2 loop (model.c) | `fc2_weight`, `fc2_bias` | [5,12]=60, [5]=5 | **IMPLEMENTED** | |

## Summary by status

| Status | Tensors | Parameters |
|---|---|---|
| IMPLEMENTED | `conv1_weight`, `conv1_bias`, `conv2_weight`, `conv2_bias`, `fc1_weight`, `fc1_bias`, `fc2_weight`, `fc2_bias` | 30+6+216+12+288+12+60+5 = **629** |
| DIVERGENT | `lstm_weight_ih`, `lstm_weight_hh`, `lstm_bias_ih`, `lstm_bias_hh` | 3168+2304+96+96 = **5,664** |
| UNUSED | `router_fc1_weight`, `router_fc1_bias`, `router_fc2_weight`, `router_fc2_bias`, `fusion_weight`, `fusion_bias` | 432+12+24+2+864+24 = **1,358** |
| **Total declared** | 18 | **7,651** |
| **Total executed (IMPLEMENTED + DIVERGENT)** | 12 | **6,293** |
| **Total unused** | 6 | **1,358** |

## Critical findings

1. **BatchNorm layers are omitted in the C inference.** The PyTorch model has `BatchNorm1d(6)` and `BatchNorm1d(12)` after each convolution. Their weights (`bn1_w.txt`, `bn1_b.txt`, `bn2_w.txt`, `bn2_b.txt` in `arrays/`) exist but are **not declared in `model_weights.h`** and **not used in `model.c`**.
2. **The feature router is a heuristic, not a learned network.** It returns one of 89, 51, or 70 based on energy comparison, ignoring `router_fc1_weight` and `router_fc2_weight`.
3. **The fusion layer is a heuristic, not a learned network.** It uses `custom3_fusion` (a simple attention formula) instead of `fusion_weight` and `fusion_bias`. This means **888 parameters are stored but never executed**.
4. **The LSTM is a simplified LSTM-LIF hybrid.** It uses `custom2_lif` (threshold-based) instead of the standard LSTM sigmoid/tanh gates. This diverges from `nn.LSTM`.
5. **Only 629 parameters (8.2%) are executed with their learned values** (conv + classifier). 5,664 parameters (74%) are executed in a divergent way. 1,358 parameters (17.8%) are stored but unused.

## Consequences for WP2 (Python-C equivalence)

The C inference is **not** numerically equivalent to the PyTorch model for four independent reasons:
1. BatchNorm omission (affects Conv1D and Conv2D outputs).
2. Router divergence (heuristic vs learned).
3. Fusion divergence (heuristic vs learned).
4. LSTM divergence (LIF vs sigmoid/tanh).

A faithful Python-C equivalence test can only be built by **reproducing the C behavior in Python**, not by reproducing PyTorch. The PyTorch comparison will show a non-zero gap, which must be documented in `WP2_validation.md`.

## Open items

- BatchNorm weights (`bn1_*`, `bn2_*`) are not in `model_weights.h`; their role in the exported model is **UNKNOWN**.
- The `M_STATE_BYTES` constant (792 bytes) is not reflected in the buffer struct; its provenance is **UNKNOWN**.
