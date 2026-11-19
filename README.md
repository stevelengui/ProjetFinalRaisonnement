# ProjetFinalRaisonnement — Meta-Reasoning for Embedded AI Co-Design

**Stage 6.2 verification package** — Manuscript frozen at the 18 November 2026 revision.

This repository contains the implementation and verification evidence for the paper:

> *A Meta-Reasoning Framework for Lifecycle-Aware Hardware-Software Co-Design of Embedded AI Systems*

## What this repository contains

| Component | Location | Purpose |
|---|---|---|
| Meta-reasoning controller | `meta_reasoning/` | Paper 5 contribution: context to contract to tool selection to decision |
| AutoCoDesign engine | `llm_nas/` | Paper 4 contribution: NSGA-II / MOEA/D Pareto exploration |
| Phase-1 C implementation | `firmware/model/` | Trained hybrid SNN-QNN model (C, weights, arrays) |
| Experiments E0-E7 | `experiments/` | 8 experiments with scripts and raw JSON results |
| Verification ledgers | `evidence_registry/ledgers/` | Machine-generated parameter, operation, memory ledgers |

## Verified numerical facts

| Quantity | Verified value | Method |
|---|---|---|
| Parameters | **7,651** | Sum of `int8_t` arrays in `model_weights.h` |
| Operations per inference | **373,128 MACs** | Sum of `TOTAL_OPS` macros |
| Weights | **7.47 KiB** | 7,651 x 1 byte |
| Struct SRAM | **10.77 KiB** | Sum of `HybridModelBuffers` fields |

**Note:** the number 373,128 is an **operation count (MACs)**, not a parameter count. Earlier versions of this README (and the Python simulator `hybrid_model.py`) mislabeled it. The correct parameter count is 7,651.

## Verification documents

| Document | Purpose |
|---|---|
| KNOWN_DISCREPANCIES.md | Numerical discrepancies between manuscript, C code, Python simulator, README |
| NUMERICAL_VERIFICATION.md | Synthesis of the three ledgers |
| MANUSCRIPT_EVIDENCE_MAP.md | Claim to repository to file to commit traceability |
| IMPLEMENTATION_VALIDATION.md | Honest status of C, host, RISC-V, simulation |
| E0_E7_REPRODUCIBILITY.md | Protocol and raw results for E0-E7 |

## Quick start

### Reproduce the ledgers

```bash
python3 scripts/param_ledger.py --header llm_nas/model_weights.h --out evidence_registry/ledgers/param_ledger.csv
python3 scripts/ops_ledger.py --header llm_nas/model_weights.h --out evidence_registry/ledgers/ops_ledger.csv
python3 scripts/memory_ledger.py --model-h firmware/model/model.h --weights-h llm_nas/model_weights.h --out evidence_registry/ledgers/memory_ledger.csv
Reproduce the experiments
bash
python3 experiments/E0_context_to_contract/run_experiment.py
python3 experiments/E1_adaptive_fidelity/run_experiment.py
python3 experiments/E2_lifecycle_replay/run_experiment.py
python3 experiments/E3_fault_injection/run_experiment.py
python3 experiments/E4_domain_shift/run_experiment.py
python3 experiments/E5_security/run_experiment.py
python3 experiments/E6_decision_records/run_experiment.py
python3 experiments/E7_ablation/run_experiment.py

## Related repositories

| Phase | Repository | Role |
|---|---|---|
| Phase 1 medical | https://github.com/stevelengui/ECG-Hybrid-SNN-QNN | Published hybrid model (MIT-BIH) |
| Phase 1 industrial | https://github.com/stevelengui/Vibration-Fault-Detection | Published hybrid model (CWRU) |
| Phase 2 AutoCoDesign | https://github.com/stevelengui/llm-nas-autocodesign | Co-design framework (Paper 4) |
| Phase 3 this work | ProjetFinalRaisonnement | Meta-reasoning (Paper 5) |

## Open items (documented, not resolved)

- Table I (29.0 KiB) vs Section VI-A (31.0 KiB): 2.0 KiB gap.
- E6: manuscript overall 0.95 vs JSON 0.985.
- E7: manuscript A0_FULL DCR 0.94 vs JSON 0.8333.
- Python-C equivalence test: placeholder (hard-coded PASS).
- RISC-V ELF: no _start, no weights linked.
- Cycle-accurate simulation: not present in repository.
- Physical validation: not performed.

See KNOWN_DISCREPANCIES.md and IMPLEMENTATION_VALIDATION.md for details.

## License

MIT.
