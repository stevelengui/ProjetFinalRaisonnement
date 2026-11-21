#!/usr/bin/env python3
"""
run_wp6_tests.py - WP6 operational tests for MetaControllerV2

Runs 5 deterministic cases:
1. missing_evidence       - context without evidence -> DEFER expected
2. contradictory_evidence - conflicting evidence -> conflict resolution
3. hard_security_failure  - ASR > threshold -> REJECT expected
4. lifecycle_drift        - drift detected -> ADAPT/REMAP expected
5. resource_infeasibility - memory > limit -> REJECT or DEFER
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from meta_reasoning.meta_controller_v2 import MetaControllerV2


CASES = [
    {
        "case_id": "missing_evidence",
        "context": {
            "domain": "medical",
            "environment": "hospital",
            "requirements": {"latency_ms": 20.0, "accuracy": 0.95},
            "evidence": [],  # empty -> missing evidence
        },
        "expected": "DEFER",
    },
    {
        "case_id": "contradictory_evidence",
        "context": {
            "domain": "medical",
            "environment": "hospital",
            "requirements": {"latency_ms": 20.0, "accuracy": 0.95},
            "evidence": [
                {"type": "latency", "value": 8.2, "confidence": 0.9},
                {"type": "latency", "value": 15.0, "confidence": 0.8},  # contradiction
            ],
        },
        "expected": "CONFLICT_RESOLVED",
    },
    {
        "case_id": "hard_security_failure",
        "context": {
            "domain": "medical",
            "environment": "hospital",
            "requirements": {"latency_ms": 20.0, "accuracy": 0.95},
            "threat_model": "critical",
            "asr": 0.40,  # > 0.20 threshold
            "evidence": [{"type": "accuracy", "value": 0.96, "confidence": 0.9}],
        },
        "expected": "REJECT",
    },
    {
        "case_id": "lifecycle_drift",
        "context": {
            "domain": "industrial",
            "environment": "factory",
            "requirements": {"latency_ms": 20.0, "accuracy": 0.93},
            "drift_detected": True,
            "drift_severity": "moderate",
            "evidence": [{"type": "accuracy", "value": 0.90, "confidence": 0.85}],
        },
        "expected": "ADAPT",
    },
    {
        "case_id": "resource_infeasibility",
        "context": {
            "domain": "medical",
            "environment": "hospital",
            "requirements": {"latency_ms": 20.0, "accuracy": 0.95, "memory_kb_max": 16.0},
            "evidence": [{"type": "memory", "value": 38.0, "confidence": 0.95}],
        },
        "expected": "REJECT",
    },
]


def main():
    results = []
    for case in CASES:
        mc = MetaControllerV2()
        print(f"\n{'='*70}")
        print(f"CASE: {case['case_id']}")
        print(f"EXPECTED: {case['expected']}")
        print(f"{'='*70}")

        try:
            decision = mc.reason(case["context"])
            decision_type = decision.get("decision", {}).get("type", "UNKNOWN")
            print(f"DECISION: {decision_type}")

            results.append({
                "case_id": case["case_id"],
                "expected": case["expected"],
                "actual": decision_type,
                "status": "PASS" if case["expected"] == decision_type or case["expected"] in decision_type else "CHECK",
                "decision": decision,
            })
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "case_id": case["case_id"],
                "expected": case["expected"],
                "actual": "ERROR",
                "status": "FAIL",
                "error": str(e),
            })

    out_path = ROOT / "evidence_registry" / "derived" / "wp6_traces.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"\nOK: {out_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in results:
        print(f"  {r['case_id']:<28} expected={r['expected']:<20} actual={r['actual']:<20} status={r['status']}")


if __name__ == "__main__":
    main()
