# Registre de Provenance E0-E7

Généré: 2026-11-03T15:57:36.028970

## Résumé

| Exp | Nom | Cas | Seeds | Oracle |
|-----|-----|-----|-------|--------|
| E0 | Context-to-Contract (RQ1) | 30 | [42] | ground_truth_contracts.py (man... |
| E1 | Adaptive Evaluation-Fidelity (RQ2) | 40 | [42] | expected_verdict (computed fro... |
| E2 | Lifecycle Replay (RQ5) | 10 | [42] | expected_intervention... |
| E3 | Fault Injection (RQ3) | 800 | [42] | nominal_accuracy + fault_sensi... |
| E4 | Domain-Shift (RQ3) | 6 | [42] | expected_intervention... |
| E5 | Security (RQ3) | 25 | [42] | asr_threshold (0.20)... |
| E6 | Decision Records (RQ4) | 3 | [42] | counterfactual_tests... |
| E7 | Ablation (Cross-RQ) | 30 | [42] | dcr_full (0.94)... |

## Fichiers sources

### E0
- Cases: `experiments/E0_context_to_contract/scenarios.py` (hash: d0e7351171ea38bd)
- Script: `scripts/run_e0.sh` (hash: fcd302f3899a19ad)
- Results: `experiments/E0_context_to_contract/results/e0_results.json` (✅)

### E1
- Cases: `experiments/E1_adaptive_fidelity/test_cases.py` (hash: 8cea9363ef4182b9)
- Script: `scripts/run_e1.sh` (hash: 62949093627bde69)
- Results: `experiments/E1_adaptive_fidelity/results/e1_results.json` (✅)

### E2
- Cases: `experiments/E2_lifecycle_replay/lifecycle_perturbations.py` (hash: eb20274d4ef05701)
- Script: `scripts/run_e2.sh` (hash: c6491342aba7e0ae)
- Results: `experiments/E2_lifecycle_replay/results/e2_results.json` (✅)

### E3
- Cases: `experiments/E3_fault_injection/candidate_designs.py` (hash: c1641f74b6bfd76b)
- Script: `scripts/run_e3.sh` (hash: ae714a4b6dd1192b)
- Results: `experiments/E3_fault_injection/results/e3_results.json` (✅)

### E4
- Cases: `experiments/E4_domain_shift/domain_shift_scenarios.py` (hash: 5d75b2a0dd95b6bc)
- Script: `scripts/run_e4.sh` (hash: 64ef9f8084b8ae01)
- Results: `experiments/E4_domain_shift/results/e4_results.json` (✅)

### E5
- Cases: `experiments/E5_security/security_designs.py` (hash: a933701d12b6c3ab)
- Script: `scripts/run_e5.sh` (hash: 674ca4e79a2ac2e8)
- Results: `experiments/E5_security/results/e5_results.json` (✅)

### E6
- Cases: `experiments/E6_decision_records/decision_record.py` (hash: d7a29bf693655183)
- Script: `scripts/run_e6.sh` (hash: 39a43473cd7aa363)
- Results: `experiments/E6_decision_records/results/e6_results.json` (✅)

### E7
- Cases: `experiments/E7_ablation/ablation_configs.py` (hash: a9d503a7412cd739)
- Script: `scripts/run_e7.sh` (hash: 4344fe2606d44f23)
- Results: `experiments/E7_ablation/results/e7_results.json` (✅)

