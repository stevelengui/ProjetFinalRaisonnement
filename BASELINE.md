# BASELINE.md — Stage 6.3 baseline

## Frozen inputs

- Manuscript: 18 November 2026 (unmodified)
- Tag: v6.2-verification (commit d3d2177)
- Working branch: stage-6.3-corrections
- Baseline date: 20 November 2026

## Canonical implementations

| Component | Canonical repository | Commit | Reference copy |
|---|---|---|---|
| Hybrid model (Paper 2) | ECG-Hybrid-SNN-QNN | 8acc23e | ProjetFinalRaisonnement/firmware/model/ |
| Vibration model (Paper 2) | Vibration-Fault-Detection | 38ef89b | — |
| AutoCoDesign (Paper 4) | llm-nas-autocodesign | 833b218 (tag v1.0.0) | ProjetFinalRaisonnement/llm_nas/ |
| Meta-reasoning (Paper 5) | ProjetFinalRaisonnement | d3d2177 (tag v6.2-verification) | — |

## Notes

- `firmware/model/model.c` in `ProjetFinalRaisonnement` is a reference copy of `ECG-Hybrid-SNN-QNN/firmware/model/model.c`. The canonical source is the phase-1 repository.
- `artifacts/generated_code/main_inference.c` is a structural skeleton (contains `output[i] = i * 10; // Simulated output`) and is not the canonical inference implementation.
- The thesis roadmap (July 2026) confirms that `ProjetFinalRaisonnement` is the Paper 5 repository (Design Intelligence), while the hybrid model belongs to Paper 2.

## Environment

- OS: Ubuntu 22.04 (WSL2)
- gcc: 11.4.0
- riscv64-unknown-elf-gcc: 10.2.0
- Python: 3.10

## Immutable files

The following files are frozen and must not be modified in this branch:
- Manuscript of 18 November 2026
- Tag v6.2-verification (commit d3d2177)
- experiments/E*/results/*.json (raw experiment results)
