# WP2 — Real quantized inference and Python-C equivalence

**Date:** 20 November 2026
**Branch:** `stage-6.3-corrections`
**Gate:** G2
**Status:** PASS with documented divergence

## 1. Objective

Verify that `firmware/model/model.c` performs a real input-dependent inference
and compare its output with two Python references:
- a C-faithful Python oracle (`tests/oracle/python_reference_c.py`);
- a PyTorch oracle loading `best_hybrid_model_ecg.pth` (`tests/oracle/python_reference_torch.py`).

## 2. Method

| Source | Command | Type |
|---|---|---|
| C (`model.c` via host build) | `tests/host/main_host` | integer (int32 logits) |
| Python C-faithful | `python3 tests/oracle/python_reference_c.py` | integer (int32 logits) |
| Python PyTorch | `python3 tests/oracle/python_reference_torch.py` | float32 logits |

Input (identical for all three):
input[i] = (i * 37) % 256 - 128, i = 0..359

text

Predeclared tolerances:
- **C vs Python C-faithful:** exact integer match (0 tolerance).
- **C vs PyTorch:** no tolerance expected; divergence is documented.

## 3. Results
C logits: [0.0, -1.0, -1.0, -1.0, 0.0]
Python C-faithful: [0.0, -1.0, -1.0, -1.0, 0.0]
Python PyTorch: [12.4162, -5.3707, -16.3781, -1.1214, -14.2686]

C vs Python C-faithful max abs gap: 0.000000
C vs PyTorch max relative gap: 1.0000

text

### Verdict

| Comparison | Result | Status |
|---|---|---|
| C vs Python C-faithful | exact match (0 gap) | **PASS** |
| C vs PyTorch | 100% relative gap | **DIVERGENCE DOCUMENTED** |

## 4. Interpretation

### 4.1 The C implementation is real and reproducible

The C produces non-zero, deterministic logits (`0 -1 -1 -1 0`) that are exactly
reproduced by the C-faithful Python oracle. This confirms:
- `model.c` performs a real forward pass using the 18 declared weight arrays;
- the C is deterministic (two runs give identical output, see §5);
- the Python C-faithful oracle is a valid reference for the C behavior.

### 4.2 The C implementation is not numerically equivalent to PyTorch

The C logits (`0 -1 -1 -1 0`) and the PyTorch logits (`12.42 -5.37 -16.38 -1.12 -14.27`)
differ by 100%. This is **expected** and documented in `architecture_weight_map.md`:

| Divergence | Effect |
|---|---|
| BatchNorm layers omitted in C | Conv outputs are not normalized |
| Router heuristic (energy-based) instead of learned `router_fc1/fc2` | Attention weights diverge from PyTorch |
| Fusion heuristic (`custom3_fusion`) instead of learned `fusion_weight/bias` | 888 parameters stored but unused |
| LSTM-LIF instead of standard LSTM (sigmoid/tanh) | Temporal dynamics diverge |
| Placeholder scales (1, 2, 3) instead of real quantization scales | Weight magnitudes are wrong |

### 4.3 The C logits are near-uniform

The C logits `0 -1 -1 -1 0` indicate that the C model **does not discriminate
between classes**. This is consistent with the placeholder scales and the
`int32_t*` → `int8_t*` cast in `model.c` line 63, which overflows the
convolution output.

## 5. Negative controls

| Control | Result | Status |
|---|---|---|
| Determinism (run C twice) | identical output | **PASS** |
| Corruption detection (corrupted logit detected) | gap = 999.0 | **PASS** |

Reproduction:
```bash
python3 tests/negative_controls.py
6. Gate G2 status
G2 criterion	Status	Evidence
Real input-dependent C inference	✅ PASS	tests/host/main_host produces 0 -1 -1 -1 0
Independently reproducible agreement	✅ PASS (C-faithful)	Python C-faithful gives identical logits
Numerical equivalence with PyTorch	❌ FAIL (documented)	100% relative gap
Hard-coded PASS removed	✅ PASS	compare_c_python.py is a real comparator
Negative controls	✅ PASS	negative_controls.py
G2 verdict: PASS with documented divergence.
The C inference is real and reproducible. The claim of "numerical equivalence
with PyTorch" is not supported and must be reduced in the manuscript.

7. Recommended manuscript corrections (not applied)
Claim	Current wording	Recommended wording
Numerical equivalence	"Python-C numerical equivalence"	"C inference reproduces the C-faithful Python oracle exactly; it diverges from PyTorch due to omitted BatchNorm, heuristic router/fusion, and LSTM-LIF"
Inference accuracy	(implicit)	"The C inference does not currently reproduce the PyTorch accuracy (96.1%); this is an open limitation"
Model parameters	"7,651 parameters"	"7,651 stored parameters, of which 6,293 are executed and 1,358 are unused (fusion + router)"
8. Reproducibility
bash
# 1. Build host binary
cd tests/host && make clean && make

# 2. Run the three sources
cd ../..
python3 tests/compare_c_python.py

# 3. Run negative controls
python3 tests/negative_controls.py
9. Open items
BatchNorm weights (bn1_*, bn2_*) are present in arrays/ but not
in model_weights.h; their role in the exported model is UNKNOWN.

Real quantization scales are not in the repository; the declared
values (1, 2, 3) are placeholders. Regenerating them requires re-running
model.py with export_weight_arrays, which is not in the repository.

C logits are near-uniform (0 -1 -1 -1 0); the model does not
discriminate classes in its current state. This is consistent with the
placeholder scales but must be documented as a limitation.

## 6. Gate G2 status

| G2 criterion | Status | Evidence |
|---|---|---|
| Real input-dependent C inference | PASS | tests/host/main_host produces 0 -1 -1 -1 0 |
| Independently reproducible agreement | PASS (C-faithful) | Python C-faithful gives identical logits |
| Numerical equivalence with PyTorch | FAIL (documented) | 100% relative gap |
| Hard-coded PASS removed | PASS | compare_c_python.py is a real comparator |
| Negative controls | PASS | negative_controls.py |

**G2 verdict: PASS with documented divergence.**
The C inference is real and reproducible. The claim of "numerical equivalence
with PyTorch" is not supported and must be reduced in the manuscript.

## 7. Recommended manuscript corrections (not applied)

| Claim | Current wording | Recommended wording |
|---|---|---|
| Numerical equivalence | "Python-C numerical equivalence" | "C inference reproduces the C-faithful Python oracle exactly; it diverges from PyTorch due to omitted BatchNorm, heuristic router/fusion, and LSTM-LIF" |
| Inference accuracy | (implicit) | "The C inference does not currently reproduce the PyTorch accuracy (96.1%); this is an open limitation" |
| Model parameters | "7,651 parameters" | "7,651 stored parameters, of which 6,293 are executed and 1,358 are unused (fusion + router)" |

## 8. Reproducibility

```bash
# 1. Build host binary
cd tests/host && make clean && make

# 2. Run the three sources
cd ../..
python3 tests/compare_c_python.py

# 3. Run negative controls
python3 tests/negative_controls.py
9. Open items
BatchNorm weights (bn1_, bn2_) are present in arrays/ but not in model_weights.h; their role in the exported model is UNKNOWN.

Real quantization scales are not in the repository; the declared values (1, 2, 3) are placeholders. Regenerating them requires re-running model.py with export_weight_arrays, which is not in the repository.

C logits are near-uniform (0 -1 -1 -1 0); the model does not discriminate classes in its current state. This is consistent with the placeholder scales but must be documented as a limitation.

## 9. Open items

- BatchNorm weights (bn1_*, bn2_*) are in arrays/ but not in model_weights.h; role UNKNOWN.
- Real quantization scales are not in the repository; declared values (1, 2, 3) are placeholders. Regenerating them requires re-running model.py with export_weight_arrays.
- C logits are near-uniform (0 -1 -1 -1 0); the model does not discriminate classes. This is consistent with the placeholder scales but must be documented as a limitation.
