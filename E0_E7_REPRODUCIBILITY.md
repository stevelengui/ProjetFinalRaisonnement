# E0_E7_REPRODUCIBILITY.md

**Repository:** stevelengui/ProjetFinalRaisonnement
**Stage:** 6.2 — Independent Scientific and Numerical Verification
**Frozen manuscript reference:** revision of 18 November 2026
**Status:** Reproducibility package for experiments E0–E7. The manuscript is not modified.

---

## 1. Overview

All eight experiments are implemented in `experiments/`, each with its own directory, scripts, and raw results:

| Experiment | Directory | Results file |
|---|---|---|
| E0 | `experiments/E0_context_to_contract/` | `results/e0_results.json` |
| E1 | `experiments/E1_adaptive_fidelity/` | `results/e1_results.json` |
| E2 | `experiments/E2_lifecycle_replay/` | `results/e2_results.json` |
| E3 | `experiments/E3_fault_injection/` | `results/e3_results.json` |
| E4 | `experiments/E4_domain_shift/` | `results/e4_results.json` |
| E5 | `experiments/E5_security/` | `results/e5_results.json` |
| E6 | `experiments/E6_decision_records/` | `results/e6_results.json` |
| E7 | `experiments/E7_ablation/` | `results/e7_results.json` |

---

## 2. E0 — Context-to-contract (RQ1)

**Directory:** `experiments/E0_context_to_contract/`
**Scripts:** `run_experiment.py`, `scenarios.py`, `ground_truth_contracts.py`, `metrics.py`, `perturbation_engine.py`, `clarification_handler.py`, `external_validator.py`, `decision_consequence_validator.py`, `register_e0_evidence.py`
**Results:** `results/e0_results.json`

**Protocol:** 30 controlled contexts (15 medical, 15 industrial), each perturbed along one dimension at a time (memory budget, latency criticality, reliability criticality, threat context, domain-shift exposure, missing information). 120 perturbations total.

**Verified metrics (from `e0_results.json`):**

| Metric | Value |
|---|---|
| contract_accuracy | 0.991 |
| primary_objective_accuracy | 1.0 |
| missing_info_detection_rate | 1.0 |
| missing_info_precision | 1.0 |
| reliability_transition_valid | true |
| decision_change_rate | 0.133 |

**Reproduction:**
```bash
python3 experiments/E0_context_to_contract/run_experiment.py
```

---

## 3. E1 — Adaptive evaluation fidelity (RQ2)

**Directory:** `experiments/E1_adaptive_fidelity/`
**Scripts:** `run_experiment.py`, `fidelity_hierarchy.py`, `policies.py`, `metrics.py`
**Results:** `results/e1_results.json`

**Protocol:** 40 controlled cases, 4 policies compared (low-fidelity-only, exhaustive, fixed workflow, adaptive meta-reasoner).

**Verified metrics (from `e1_results.json`):**

| Policy | Agreement | Avg cost | HF rate |
|---|---|---|---|
| low_fidelity_only | 0.95 | 0.010 | 0.0 |
| exhaustive | 1.0 | 1.0 | 1.0 |
| fixed_workflow | 1.0 | 0.485 | 0.475 |
| adaptive | 1.0 | 0.635 | 0.625 |

**Reproduction:**
```bash
python3 experiments/E1_adaptive_fidelity/run_experiment.py
```

---

## 4. E2 — Lifecycle replay (RQ5)

**Directory:** `experiments/E2_lifecycle_replay/`
**Scripts:** `run_experiment.py`, `deployment_contract.py`, `lifecycle_monitor.py`, `intervention_selector.py`, `lifecycle_perturbations.py`, `replay_engine.py`
**Results:** `results/e2_results.json`

**Protocol:** 2 deployment contracts (ECG medical, vibration industrial), 5 perturbation classes (P0 nominal, P1 minor, P2 moderate, P3 major, P4 structural), 10 events total.

**Verified metrics (from `e2_results.json`):**

| Perturbation | Expected | Match rate |
|---|---|---|
| P0 (C0_nominal) | continue | 1.0 |
| P1 (C1_minor) | calibrate | 1.0 |
| P2 (C2_moderate) | adapt | 1.0 |
| P3 (C3_major) | remap | 1.0 |
| P4 (C4_structural) | redesign | 1.0 |
| **Overall** | | **1.0** |

**Reproduction:**
```bash
python3 experiments/E2_lifecycle_replay/run_experiment.py
```

---

## 5. E3 — Fault injection (RQ3)

**Directory:** `experiments/E3_fault_injection/`
**Scripts:** `run_experiment.py`, `fault_injector.py`, `fault_models.py`, `reliability_metrics.py`, `renversement_test.py`, `candidate_designs.py`
**Results:** `results/e3_results.json`

**Protocol:** 4 candidate designs (ecg_hybrid_8bit, ecg_hybrid_4bit, ecg_snn_2bit, ecg_hybrid_8bit_protected), 5 fault models, 200 faults per design.

**Verified metrics (from `e3_results.json`):**

| Design | P_SDC | Delta_A_f mean |
|---|---|---|
| ecg_hybrid_8bit | 0.155 | 0.0183 |
| ecg_hybrid_4bit | 0.190 | 0.0355 |
| ecg_snn_2bit | 0.165 | 0.0499 |
| ecg_hybrid_8bit_protected | 0.0 | 0.0009 |

**Rank reversal:** before injection, ecg_hybrid_8bit is best (accuracy 0.961). After injection, ecg_hybrid_8bit_protected is best (P_SDC 0.0). The meta-reasoner correctly switches designs.

**Reproduction:**
```bash
python3 experiments/E3_fault_injection/run_experiment.py
```

---

## 6. E4 — Domain-shift meta-reasoning (RQ3)

**Directory:** `experiments/E4_domain_shift/`
**Scripts:** `run_experiment.py`, `domain_shift_scenarios.py`, `adaptation_methods.py`, `severity_classifier.py`, `meta_reasoner_selector.py`, `post_adaptation_validator.py`
**Results:** `results/e4_results.json`

**Protocol:** 6 domain-shift scenarios (DS01–DS06), classified as D0 nominal to D3 severe, 8 adaptation methods available (none, recalibrate, MAML, fine-tune, precision change, switch subnetwork, remap, redesign).

**Verified classifications (from `e4_results.json`):**

| Scenario | Severity | Score |
|---|---|---|
| DS01 | D0_nominal | 0.0 |
| DS02 | D1_light | 0.09 |
| DS03 | D1_light | 0.12 |
| DS04 | D1_light | 0.23 |
| DS05 | D2_moderate | 0.28 |
| DS06 | D3_severe | 0.58 |

**Reproduction:**
```bash
python3 experiments/E4_domain_shift/run_experiment.py
```

---

## 7. E5 — Security meta-reasoning (RQ3)

**Directory:** `experiments/E5_security/`
**Scripts:** `run_experiment.py`, `threat_models.py`, `attack_scenarios.py`, `security_designs.py`, `asr_evaluator.py`, `security_meta_reasoner.py`
**Results:** `results/e5_results.json`

**Protocol:** 5 threat models (T0–T4), 6 attack scenarios (FGSM, PGD, C&W, backdoor, extraction, membership), 5 security designs (none, input_validation, adversarial_training, randomized_smoothing, ensemble).

**Verified metrics (from `e5_results.json`):** ASR per design under each threat. Under T4 (critical), no design satisfies the ASR threshold; the meta-reasoner returns DEFER for designs that violate ASR but satisfy resources, and REJECT for sec_ensemble (best ASR but violates memory).

**Reproduction:**
```bash
python3 experiments/E5_security/run_experiment.py
```

---

## 8. E6 — Decision records (RQ4)

**Directory:** `experiments/E6_decision_records/`
**Scripts:** `run_experiment.py`, `decision_record.py`, `explanation_generator.py`, `counterfactual_engine.py`, `audit_metrics.py`
**Results:** `results/e6_results.json`, `results/ddr_001.json`, `results/ddr_002.json`, `results/ddr_003.json`

**Protocol:** 3 decision records (ACCEPT, REJECT, DEFER), each with 9 components (C, Gamma, A, E, U, R, Alt, Dec, CF). 3 counterfactual tests.

**Verified metrics (from `e6_results.json`):**

| Metric | Value |
|---|---|
| EC (Explanation Completeness) | 1.0 |
| CT (Counterfactual Testability) | 0.9 |
| DF (Decision Fidelity) | 1.0 |
| CF (Counterfactual Fidelity) | 1.0 |
| AC (Audit Consistency) | 1.0 |
| AV (Audit Verifiability) | 1.0 |
| Overall | 0.985 |

**Note:** the manuscript reports overall 0.95 and CF 0.85; the JSON gives 0.985 and 1.0. This is an open item (see KNOWN_DISCREPANCIES.md section 5.3).

**Reproduction:**
```bash
python3 experiments/E6_decision_records/run_experiment.py
```

---

## 9. E7 — Ablation (cross-RQ)

**Directory:** `experiments/E7_ablation/`
**Scripts:** `run_experiment.py`, `ablation_runner.py`, `ablation_configs.py`, `ablation_metrics.py`, `ablation_analyzer.py`
**Results:** `results/e7_results.json`

**Protocol:** 11 configurations (A0_FULL + 10 ablations), 30 scenarios per configuration.

**Verified metrics (from `e7_results.json`, selected):**

| Config | DCR | Regret | Overall |
|---|---|---|---|
| A0_FULL | 0.8333 | 0.0789 | 0.9395 |
| A1_NO_ADAPTIVE | 0.70 | 0.4568 | 0.6235 |
| A2_NO_UNCERTAINTY | (see JSON) | (see JSON) | (see JSON) |

**Note:** the manuscript reports A0_FULL DCR = 0.94; the JSON gives 0.8333. This is an open item (see KNOWN_DISCREPANCIES.md section 5.3).

**Reproduction:**
```bash
python3 experiments/E7_ablation/run_experiment.py
```

---

## 10. Open items

1. E6: manuscript overall 0.95 vs JSON 0.985; CF 0.85 vs 1.0.
2. E7: manuscript A0_FULL DCR 0.94 vs JSON 0.8333.
3. E4: severity classification of DS04 (D1_light, score 0.23) and DS05 (D2_moderate, score 0.28) — threshold to confirm.
4. E5: T4 DEFER/REJECT decisions — to be verified against the JSON ASR table.
5. Seeds: verify that each `run_experiment.py` sets a deterministic seed.

---

## 11. Statement of compliance

- The manuscript of 18 November 2026 has not been modified.
- All 8 experiments have code and raw JSON results in the repository.
- Every metric quoted in this document is taken from the JSON files.
- Discrepancies between JSON and manuscript are listed in section 10 and in KNOWN_DISCREPANCIES.md section 5.3.

---

*End of E0_E7_REPRODUCIBILITY.md*
