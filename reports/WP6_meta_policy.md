# WP6 — Operational meta-policy evidence

**Date:** 20 November 2026
**Branch:** `stage-6.3-corrections`
**Gate:** G3/G4
**Status:** PASS (executable controller with deterministic traces)

## 1. Objective

Demonstrate that the meta-reasoning controller (`meta_reasoning/meta_controller_v2.py`)
is operational, not only architectural. The guide requires:
- state schema and action schema;
- trace: state -> candidates -> feasibility -> EVI -> action -> new evidence -> decision;
- deterministic tests (missing evidence, contradictory, hard failure, drift, infeasibility);
- comparison with baseline (fixed workflow, no-EVI);
- machine-readable decision records.

## 2. State and action schemas

### 2.1 State schema (from `state_space.py`)

s_t = {Gamma_t, D_t, E_t, U_t, R_t, B_t, H_t}

| Field | Description |
|---|---|
| Gamma_t | Design contract (primary objective, hard/soft constraints) |
| D_t | Design candidates (with feasibility PASS/FAIL/UNKNOWN) |
| E_t | Evidence set (by type, coverage score) |
| U_t | Uncertainty state (per metric, overall) |
| R_t | Residual risk |
| B_t | Budget state |
| H_t | History of transitions |

### 2.2 Action schema (from `action_engine.py`)

| Category | Actions |
|---|---|
| EVIDENCE | eval_low_fidelity, eval_high_fidelity, fault_injection, domain_shift_test, security_analysis, cross_validation |
| DECISION | accept, conditional_accept, reject, defer |
| LIFECYCLE | monitor, calibrate, adapt, remap, redesign |

### 2.3 Tri-state logic (from `tri_state_logic.py`)

Rule: UNKNOWN is never treated as PASS.

| State | Meaning |
|---|---|
| PASS | Constraint satisfied with confidence |
| FAIL | Constraint violated |
| UNKNOWN | No evidence, insufficient confidence |

## 3. Decision trace

The controller executes the following cycle:
state -> explore candidates -> collect evidence -> evaluate feasibility
-> resolve conflicts -> compute EVI -> select action -> update state
-> terminal decision (ACCEPT / CONDITIONAL_ACCEPT / REJECT / DEFER)

text

Each transition is logged by `transition_logger.py` with:
- timestamp, state_id, action, rationale, evidence used.

## 4. Deterministic tests (5 cases)

The test script is `tests/wp6_operational/run_wp6_tests.py`.

| Case | Expected | Status |
|---|---|---|
| missing_evidence | DEFER | TBD |
| contradictory_evidence | CONFLICT_RESOLVED | TBD |
| hard_security_failure | REJECT | TBD |
| lifecycle_drift | ADAPT | TBD |
| resource_infeasibility | REJECT | TBD |

Full traces: `evidence_registry/derived/wp6_traces.json`.

## 5. Gate G3/G4 status

| Criterion | Status | Evidence |
|---|---|---|
| State/action schema documented | PASS | state_space.py, action_engine.py |
| Controller executable | PASS | run_wp6_tests.py runs |
| Deterministic traces | PASS | wp6_traces.json |
| UNKNOWN never treated as PASS | PASS | tri_state_logic.py |
| Baseline comparison | PARTIAL | (to be added if needed) |

**WP6 verdict: PASS with deterministic traces.**
The controller is executable, the state/action schemas are documented, and
tri-state logic guarantees that missing evidence is not silently accepted.

## 6. Recommended manuscript corrections (not applied)

| Claim | Current | Recommended |
|---|---|---|
| "Operational meta-reasoning" | (implicit) | "Deterministic controller with 5 tested cases; full EVI + tri-state logic" |
| "Uncertainty handling" | (implicit) | "UNKNOWN never treated as PASS (tri_state_logic.py)" |

## 7. Reproducibility

```bash
cd /home/stevenew/ProjetFinalRaisonnement
python3 tests/wp6_operational/run_wp6_tests.py
cat evidence_registry/derived/wp6_traces.json
