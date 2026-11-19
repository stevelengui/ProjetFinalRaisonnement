# NUMERICAL_VERIFICATION.md

**Repository:** stevelengui/ProjetFinalRaisonnement  
**Stage:** 6.2 — Independent Scientific and Numerical Verification  
**Frozen manuscript reference:** revision of 18 November 2026  
**Status:** Machine-generated ledgers, reproducible. Manuscript not modified.

---

## 1. Purpose

This document consolidates the three machine-generated ledgers that independently verify the numerical claims of the frozen manuscript:

| Ledger | Script | Output | Verifies |
|---|---|---|---|
| Parameters | `scripts/param_ledger.py` | `evidence_registry/ledgers/param_ledger.{csv,json}` | 7,651 parameters |
| Operations | `scripts/ops_ledger.py` | `evidence_registry/ledgers/ops_ledger.{csv,json}` | 373,128 MACs |
| Memory | `scripts/memory_ledger.py` | `evidence_registry/ledgers/memory_ledger.{csv,json}` | 7.47 KiB weights, 10.767 KiB struct SRAM |

All three scripts parse the repository's own source files (`llm_nas/model_weights.h`, `firmware/model/model.h`) and can be re-executed at any time.

---

## 2. Parameter verification (7,651)

**Source:** `llm_nas/model_weights.h` (identical to `firmware/model/model_weights.h` for the 18 weight arrays — see `KNOWN_DISCREPANCIES.md` §2.6).

| Layer | Arrays | Parameters |
|---|---|---|
| Conv1D | `conv1_weight`, `conv1_bias` | 30 + 6 = 36 |
| Conv2D | `conv2_weight`, `conv2_bias` | 216 + 12 = 228 |
| LSTM | `lstm_weight_ih`, `lstm_weight_hh`, `lstm_bias_ih`, `lstm_bias_hh` | 3,168 + 2,304 + 96 + 96 = 5,664 |
| Router | `router_fc1_weight`, `router_fc1_bias`, `router_fc2_weight`, `router_fc2_bias` | 432 + 12 + 24 + 2 = 470 |
| Fusion | `fusion_weight`, `fusion_bias` | 864 + 24 = 888 |
| FC1 | `fc1_weight`, `fc1_bias` | 288 + 12 = 300 |
| Output | `fc2_weight`, `fc2_bias` | 60 + 5 = 65 |
| **Total** | | **7,651** |

**Verified: 7,651 parameters.**

**Reconciliation with the manuscript:** the manuscript's Section VI-A quotes 9,317 as the sum of layer counts. The difference (1,666) is explained in `KNOWN_DISCREPANCIES.md` §1.3: the manuscript counts LSTM as 5,472 (actual 5,664), SNN-LIF as 2,176 (actual 0 declared weights), and Dense as 470 (actual 300 for `fc1`; the router is counted separately).

**Reproduction:**
```bash
python3 scripts/param_ledger.py \
  --header llm_nas/model_weights.h \
  --out evidence_registry/ledgers/param_ledger.csv
3. Operation verification (373,128)
Source: llm_nas/model_weights.h, macros *_OPS and TOTAL_OPS.

Layer	Macro	Operations
Conv1D	CONV1_OPS = 6×180×5×2	10,800
Conv2D	CONV2_OPS = 12×90×3×2	6,480
LSTM	LSTM_OPS = 4×24×(33+24)×32×2	350,208
SNN-LIF	LIF_OPS = 32×24×3	2,304
FC	FC_OPS = (24×(12+24)+12×24+5×12)×2	2,424
Router	ROUTER_OPS = (12×(12+24)+2×12)×2	912
Total	TOTAL_OPS	373,128
Verified: 373,128 MACs per inference.

Note: this number is sometimes labelled "parameters" in the Python simulator and README. It is an operation count, not a parameter count. The manuscript correctly uses it as an operation count in Section VI-A.

Reproduction:

bash
python3 scripts/ops_ledger.py \
  --header llm_nas/model_weights.h \
  --out evidence_registry/ledgers/ops_ledger.csv
4. Memory verification
4.1 Weights
Source: llm_nas/model_weights.h, 18 int8_t arrays totaling 7,651 elements.

7,651 × 1 byte = 7,651 bytes = 7.472 KiB.

Manuscript: 7.47 KiB. ✅ Match.

4.2 SRAM (struct HybridModelBuffers)
Source: firmware/model/model.h.

Field	Type	Elements	Bytes
input_buf	int8_t	360	360
conv1_out	int32_t	1,080	4,320
conv2_out	int32_t	1,080	4,320
snn_input	int8_t	1,056	1,056
spike_train	int8_t	768	768
lstm_state	int8_t	24	24
router_output	int8_t	2	2
fused_features	int32_t	24	96
fc1_out	int32_t	12	48
output	int32_t	5	20
precision_mode	uint8_t	1	1
temperature	int16_t	1	2
total_cycles	uint32_t	1	4
inference_count	uint32_t	1	4
Total			11,025 B = 10.767 KiB
4.3 Reconciliation table
Item	Value	Source	Status
Weights	7.472 KiB	param_ledger.py	✅ verified
Struct SRAM	10.767 KiB	memory_ledger.py	✅ verified
M_ACTIVATION_PEAK_BYTES	11,014 B = 10.756 KiB	llm_nas/model_weights.h	✅ consistent (Δ 11 B vs struct)
M_CODE_BYTES	12,288 B = 12.000 KiB	llm_nas/model_weights.h	documented
M_RUNTIME_BYTES	2,560 B = 2.500 KiB	llm_nas/model_weights.h	documented
MS Flash (VI-A)	19.47 KiB	MS	= 7.47 (weights) + 12.00 (code) ✅
MS SRAM (VI-A)	11.53 KiB	MS	vs struct 10.767 → Δ 0.763 KiB (open)
MS total (VI-A)	31.00 KiB	19.47 + 11.53	—
MS Table I	29.00 KiB	MS Table I	Δ 2.00 KiB vs VI-A (open)
4.4 Open items
Two discrepancies remain open and are documented, not resolved:

Δ 0.763 KiB between struct SRAM (10.767 KiB) and MS SRAM (11.53 KiB). Probable cause: stack frame, local arrays in model_predict (spatial_features[12], snn_features[24], qnn_features[12] = 48 B), and alignment padding. Will be closed by the ELF size output (see IMPLEMENTATION_VALIDATION.md).

Δ 2.00 KiB between MS total VI-A (31.00 KiB) and MS Table I (29.00 KiB). Probable cause: Table I may exclude stack/heap or use a different accounting convention. Will be closed by the linker script analysis (see IMPLEMENTATION_VALIDATION.md).

These are documentation items, not corrections. The manuscript is not modified at this stage.

4.5 Reproduction
bash
python3 scripts/memory_ledger.py \
  --model-h firmware/model/model.h \
  --weights-h llm_nas/model_weights.h \
  --out evidence_registry/ledgers/memory_ledger.csv
5. Summary of verified values
Quantity	Verified value	Method
Parameters	7,651	param_ledger.py
Operations per inference	373,128	ops_ledger.py
Weights	7.472 KiB	param_ledger.py
Struct SRAM	10.767 KiB	memory_ledger.py
M_ACTIVATION_PEAK_BYTES	11,014 B	header constant
M_CODE_BYTES	12,288 B	header constant
6. Statement of compliance
The manuscript of 18 November 2026 has not been modified.

All values are produced by scripts parsing the repository's own source files.

All scripts are deterministic and can be re-executed.

Outputs are stored in evidence_registry/ledgers/.

The original phase-1 sources are preserved in firmware/model/.

End of NUMERICAL_VERIFICATION.md
