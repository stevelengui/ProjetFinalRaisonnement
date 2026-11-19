# MANUSCRIPT_EVIDENCE_MAP.md

**Repository:** stevelengui/ProjetFinalRaisonnement  
**Stage:** 6.2 — Independent Scientific and Numerical Verification  
**Frozen manuscript reference:** "A Meta-Reasoning Framework for Lifecycle-Aware Hardware-Software Co-Design of Embedded AI Systems", revision of 18 November 2026  
**Status:** Traceability map. The manuscript is **not** modified at this stage.

---

## 1. Purpose

This document links every important claim, table, figure and experiment of the frozen manuscript to its corresponding code, configuration, and result files across the four related repositories. It is the entry point requested by the reviewer to locate the evidence for each result.

---

## 2. Repositories and their role

| Repository | Phase | Role | HEAD commit | Tag |
|---|---|---|---|---|
| `ECG-Hybrid-SNN-QNN` | Phase 1 — medical | Published hybrid SNN-QNN model (MIT-BIH) | `8acc23e` | — |
| `Vibration-Fault-Detection` | Phase 1 — industrial | Published hybrid model (CWRU bearing) | `38ef89b` | — |
| `llm-nas-autocodesign` | Phase 2 — AutoCoDesign | Published/submitted co-design framework (Paper 4) | `833b218` | `v1.0.0` (`90329a4`) |
| `ProjetFinalRaisonnement` | Phase 3 — Meta-reasoning | This work (Paper 5) | `8a77d81` (branch `stage-6.2-verification`) | — |

**URLs:**
- https://github.com/stevelengui/ECG-Hybrid-SNN-QNN
- https://github.com/stevelengui/Vibration-Fault-Detection
- https://github.com/stevelengui/llm-nas-autocodesign
- https://github.com/stevelengui/ProjetFinalRaisonnement

---

## 3. Claim-to-evidence map

### 3.1 Numerical claims

| Claim in manuscript | Location in MS | Repository | File | Verified in | Status |
|---|---|---|---|---|---|
| 7,651 parameters | §VI-A | `ProjetFinalRaisonnement` | `llm_nas/model_weights.h` (18 `int8_t` arrays) | `evidence_registry/ledgers/param_ledger.csv` | ✅ verified |
| 373,128 operations per inference | §VI-A | `ProjetFinalRaisonnement` | `llm_nas/model_weights.h` (`TOTAL_OPS`) | `evidence_registry/ledgers/ops_ledger.csv` | ✅ verified |
| 7.47 KiB weights | §VI-A | `ProjetFinalRaisonnement` | `llm_nas/model_weights.h` | `evidence_registry/ledgers/param_ledger.csv` | ✅ verified |
| 10.77 KiB struct SRAM | §VI-A | `ProjetFinalRaisonnement` | `firmware/model/model.h` | `evidence_registry/ledgers/memory_ledger.csv` | ✅ verified |
| Flash 19.47 KiB | §VI-A | `ProjetFinalRaisonnement` | `llm_nas/model_weights.h` (`M_CODE_BYTES = 12,288`) | `NUMERICAL_VERIFICATION.md` §4.3 | ⏳ open (ELF pending) |
| Table I total 29.0 KiB | Table I | `ProjetFinalRaisonnement` | — | `KNOWN_DISCREPANCIES.md` §2.3 | ⏳ open (Δ 2.0 KiB) |
| 21,600 design configurations | §VI-A | `llm-nas-autocodesign` | `llm_nas/pareto_explorer.py`, `llm_nas/real_designs.py` | to be confirmed by ledger | ⏳ to verify |

### 3.2 Model accuracy

| Claim in manuscript | Location in MS | Repository | File | Note | Status |
|---|---|---|---|---|---|
| 96.1 % on MIT-BIH ECG | Table I, §VI-A | `ProjetFinalRaisonnement` (quantized 8-bit model) | `llm_nas/real_designs.py` | Phase-1 published article reports 97.49 % (different protocol — see `KNOWN_DISCREPANCIES.md` §5.2) | ⏳ protocol to document |
| 95.8 % on CWRU bearing | Table I, §VI-A | `ProjetFinalRaisonnement` (quantized 8-bit model) | `llm_nas/real_designs.py` | Phase-1 published article reports 100 % (different protocol — see `KNOWN_DISCREPANCIES.md` §5.2) | ⏳ protocol to document |

### 3.3 Experiments E0–E7

| Experiment | Manuscript section | Repository | Files | Status |
|---|---|---|---|---|
| E0 — Context-to-contract | §VI-C | `ProjetFinalRaisonnement` | `experiments/`, `meta_reasoning/context_analyzer.py`, `meta_reasoning/design_contract.py` | ⏳ to package |
| E1 — Adaptive fidelity | §VI-D | `ProjetFinalRaisonnement` | `experiments/`, `meta_reasoning/meta_controller.py` | ⏳ to package |
| E2 — Lifecycle replay | §VI-E | `ProjetFinalRaisonnement` | `experiments/`, `meta_reasoning/post_deployment_monitor.py` | ⏳ to package |
| E3 — Fault injection | §VI-F | `ProjetFinalRaisonnement` | `experiments/`, `meta_reasoning/fault_injector.py` | ⏳ to package |
| E4 — Domain shift | §VI-G | `ProjetFinalRaisonnement` | `experiments/`, `meta_reasoning/meta_controller.py`, `llm_nas/metalearn.py` | ⏳ to package |
| E5 — Security | §VI-H | `ProjetFinalRaisonnement` | `experiments/`, `meta_reasoning/meta_controller.py` | ⏳ to package |
| E6 — Decision records | §VI-I | `ProjetFinalRaisonnement` | `experiments/`, `meta_reasoning/assurance_generator.py` | ⏳ to package |
| E7 — Ablation | §VI-J | `ProjetFinalRaisonnement` | `experiments/`, `meta_reasoning/` | ⏳ to package |

### 3.4 C implementation and RISC-V

| Claim in manuscript | Location in MS | Repository | File | Status |
|---|---|---|---|---|
| Generated C inference code | §VI-K | `ProjetFinalRaisonnement` | `firmware/model/model.c`, `firmware/model/model.h` | ✅ imported |
| Exported quantized weights | §VI-K | `ProjetFinalRaisonnement` | `firmware/model/model_weights.c`, `firmware/model/arrays/` (38 files) | ✅ imported |
| Host compilation log | §VI-K | `ProjetFinalRaisonnement` | `artifacts/generated_code/main_inference.c` | ⏳ to document |
| RISC-V cross-compilation | §VI-K | `ProjetFinalRaisonnement` | `artifacts/generated_code/main_inference_riscv.c` | ⏳ to document |
| ELF size, stack, heap | §VI-A | `ProjetFinalRaisonnement` | — | ⏳ open (see `NUMERICAL_VERIFICATION.md` §4.4) |

### 3.5 Meta-reasoning controller

| Claim in manuscript | Location in MS | Repository | File | Status |
|---|---|---|---|---|
| Context → contract | §III, §IV-C | `ProjetFinalRaisonnement` | `meta_reasoning/context_analyzer.py`, `meta_reasoning/design_contract.py` | ✅ present |
| Tool selection | §IV-D | `ProjetFinalRaisonnement` | `meta_reasoning/meta_controller.py` | ✅ present |
| Evaluation fidelity | §IV-D, §V | `ProjetFinalRaisonnement` | `meta_reasoning/meta_controller.py` | ✅ present |
| Uncertainty / evidence handling | §IV-E, §V | `ProjetFinalRaisonnement` | `meta_reasoning/evidence_evaluator.py` | ✅ present |
| EVI / stopping | §V-C | `ProjetFinalRaisonnement` | `meta_reasoning/meta_controller.py` | ⏳ to show trace |
| ACCEPT/REJECT/DEFER/ADAPT/REDESIGN | §IV-G | `ProjetFinalRaisonnement` | `meta_reasoning/meta_controller.py`, `meta_reasoning/assurance_generator.py` | ⏳ to show trace |
| Auditable explanations | §IV-G | `ProjetFinalRaisonnement` | `meta_reasoning/assurance_generator.py` | ⏳ to show trace |

---

## 4. Documents supporting traceability

| Document | Purpose | Repository | Status |
|---|---|---|---|
| `KNOWN_DISCREPANCIES.md` | Numerical discrepancies between MS, C-CODE, PY-SIM, README | `ProjetFinalRaisonnement` | ✅ committed (`8a77d81`) |
| `NUMERICAL_VERIFICATION.md` | Synthesis of the three ledgers | `ProjetFinalRaisonnement` | ✅ committed |
| `IMPLEMENTATION_VALIDATION.md` | C, host, RISC-V, simulation evidence | `ProjetFinalRaisonnement` | ⏳ to write |
| `E0_E7_REPRODUCIBILITY.md` | Experiment protocols, seeds, raw results | `ProjetFinalRaisonnement` | ⏳ to write |
| `evidence_registry/ledgers/param_ledger.{csv,json}` | 7,651 parameters | `ProjetFinalRaisonnement` | ✅ committed |
| `evidence_registry/ledgers/ops_ledger.{csv,json}` | 373,128 MACs | `ProjetFinalRaisonnement` | ✅ committed |
| `evidence_registry/ledgers/memory_ledger.{csv,json}` | 10.77 KiB struct SRAM | `ProjetFinalRaisonnement` | ✅ committed |

---

## 5. Open items

The following items are pending and will be addressed in the companion documents:

1. `IMPLEMENTATION_VALIDATION.md`: host compilation log, RISC-V cross-compilation, ELF `size` output, Python↔C equivalence tests.
2. `E0_E7_REPRODUCIBILITY.md`: seeds, configurations, raw results for E0–E7.
3. Trace generation for the meta-reasoning controller (`ACCEPT`/`REJECT`/`DEFER`/`ADAPT`/`REDESIGN`).
4. Protocol documentation for the 96.1 % / 95.8 % accuracy figures (see `KNOWN_DISCREPANCIES.md` §5.2).
5. Confirmation of the 21,600 design configurations from `llm-nas-autocodesign`.

---

## 6. Statement of compliance

- The manuscript of 18 November 2026 has **not** been modified.
- Every claim is linked to a repository, a file, and (where possible) a commit.
- The four repositories are independently versioned; their commits are recorded in §2.
- All statuses are either ✅ (verified), ⏳ (in progress), or documented as open items.

---

*End of MANUSCRIPT_EVIDENCE_MAP.md*
