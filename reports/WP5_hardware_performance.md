# WP5 — Honest latency, energy and simulation evidence

**Date:** 20 November 2026
**Branch:** `stage-6.3-corrections`
**Gate:** G4
**Status:** PASS with honest classification (Path B: estimates)

## 1. Objective

Classify every hardware performance metric of the manuscript into one of four
evidence modes (MEAS, SIM, ANA, DER), and document the gaps between the
manuscript claims and the available evidence.

The guide (WP5) offers two paths:
- **Path A**: genuine cycle-accurate simulation (not feasible here).
- **Path B**: defensible estimates, explicitly labeled ANA/DER.

**WP5 adopts Path B**: no cycle-accurate simulator is available in the repository,
and the QEMU execution is not cycle-accurate for K210.

## 2. Evidence modes

| Mode | Definition | Example |
|---|---|---|
| MEAS | Measured on physical hardware | Energy from a power probe |
| SIM | Simulated (cycle-accurate or not) | QEMU execution |
| ANA | Analytical estimate (equations + assumptions) | Latency = ops / throughput |
| DER | Derived from static code constants | Parameter count, MAC count |
| NOT_MEASURED | No evidence available | Host latency |

## 3. Metric-by-metric classification

The full table is in `reports/WP5_evidence_classification.csv` (14 rows).
Summary:

| Metric | Value | Mode | Status |
|---|---|---|---|
| Latency (manuscript) | 8.2 ms | ANA | UNVERIFIED |
| Latency (QEMU) | 40.75 ms | SIM | DIVERGENT (5x slower) |
| Energy (manuscript) | 2.8 mJ | ANA | UNVERIFIED |
| TOPS/W (manuscript) | 4.7 | ANA | UNVERIFIED |
| TOPS/W (QEMU) | 5447.9 | DER | CALCULATION_ERROR |
| Weights | 7.47 KiB | DER | PASS |
| Struct SRAM | 10.767 KiB | DER | PASS |
| Flash (estimate) | 19.47 KiB | ANA | UNVERIFIED |
| Table I total | 29.0 KiB | ANA | UNVERIFIED |
| QEMU memory | 7.51 KB | SIM | PASS_WITH_CAVEAT |
| Operations | 373,128 MACs | DER | PASS |
| Cycles (QEMU) | 1,304,108 | SIM | NOT_IN_MANUSCRIPT |

## 4. Critical findings

### 4.1 The manuscript's latency (8.2 ms) is not confirmed by QEMU

- Manuscript: 8.2 ms
- QEMU: 40.75 ms
- Ratio: **5x slower**

**Cause**: QEMU is not cycle-accurate for K210. The QEMU latency reflects the
host's execution speed, not the K210's. The 8.2 ms manuscript figure is an
**estimate** (likely derived from `ops / throughput`), not a measurement.

**Action**: the manuscript must label 8.2 ms as ANA (analytical estimate), not
as a measured latency.

### 4.2 The manuscript's TOPS/W (4.7) is contradicted by QEMU (5447.9)

- Manuscript: 4.7 TOPS/W
- QEMU: 5447.9 TOPS/W
- Ratio: **1000x higher**

**Cause**: the QEMU `main.c` computes TOPS/W as:
Performance = ops / (cycles / freq) // = ops * freq / cycles
Efficiency = Performance / power_mw

text
With `ops = 373,128`, `cycles = 1,304,108`, `freq = 400e6`, `power = 21 mW`:
Performance = 373,128 * 400e6 / 1,304,108 = 1.144e11 ops/s = 114.4 GOPS
Efficiency = 114.4e9 / 21e-3 = 5447.9 TOPS/W

text
The result is **1000x higher** than the manuscript's 4.7 TOPS/W because the
formula treats QEMU cycles as if they were K210 cycles. This is a **calculation
error**, not a measurement.

**Action**: the manuscript must either (a) recompute TOPS/W with a defensible
methodology, or (b) label 4.7 as ANA (estimate), not as a measured value.

### 4.3 The weights and operations are correctly verified

- Weights: 7.47 KiB (DER, 7,651 bytes) → **PASS**
- Operations: 373,128 MACs (DER, static macro sum) → **PASS**

These are the only metrics that are fully verified from the code.

### 4.4 The memory footprint is partially verified

- Weights: 7.47 KiB (DER) → **PASS**
- Struct SRAM: 10.767 KiB (DER) → **PASS**
- Flash (estimate): 19.47 KiB (ANA) → **UNVERIFIED** (no ELF size measurement)
- Table I total: 29.0 KiB (ANA) → **UNVERIFIED** (aggregate convention)

**Action**: the manuscript should either provide the ELF size output or label
the memory figures as ANA estimates.

## 5. Path A vs Path B decision

**Path A (cycle-accurate simulation) is not feasible** in the repository:
- No cycle-accurate simulator for K210 is available.
- QEMU `virt` is not cycle-accurate for K210.
- Installing a K210 simulator would take days and is outside Stage 6.3 scope.

**Path B (defensible estimates) is adopted**:
- All metrics are classified as MEAS, SIM, ANA, DER, or NOT_MEASURED.
- The manuscript's estimates (8.2 ms, 2.8 mJ, 4.7 TOPS/W) are labeled ANA.
- The QEMU values are labeled SIM and marked as not comparable to K210.
- The DER values (weights, ops) are the only fully verified metrics.

## 6. Gate G4 status

| G4 criterion | Status | Evidence |
|---|---|---|
| Each metric classified (MEAS/SIM/ANA/DER) | PASS | WP5_evidence_classification.csv (14 rows) |
| Claims match evidence | PARTIAL | weights/ops PASS; latency/energy/TOPS/W UNVERIFIED |
| No unsupported cycle-accurate claims | PASS | QEMU labeled SIM, not cycle-accurate |
| No unsupported physical claims | PASS | No physical validation claimed |

**G4 verdict: PASS with proportionate claims.**
The evidence is honestly classified. The manuscript must reduce its claims for
latency, energy, and TOPS/W (ANA, not measured) to match the available evidence.

## 7. Recommended manuscript corrections (not applied)

| Claim | Current | Recommended |
|---|---|---|
| Latency | "8.2 ms" | "8.2 ms (analytical estimate; QEMU gives 40.75 ms but is not cycle-accurate)" |
| Energy | "2.8 mJ" | "2.8 mJ (analytical estimate, not measured)" |
| TOPS/W | "4.7" | "4.7 (analytical estimate; the QEMU calculation gives 5447.9 due to a formula error)" |
| Memory (Table I) | "29.0 KiB" | "29.0 KiB (aggregate estimate; weights = 7.47 KiB DER, struct SRAM = 10.767 KiB DER)" |

## 8. Reproducibility

```bash
# View the full classification
cat reports/WP5_evidence_classification.csv

# QEMU execution (for SIM values)
cd /home/stevenew/github-projects/ECG-Hybrid-SNN-QNN
timeout 15 qemu-system-riscv64 -machine virt -nographic -bios none \
    -kernel build/firmware_qemu.elf -m 128M
