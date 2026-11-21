#!/usr/bin/env python3
"""
compare_c_python.py - Real comparator for WP2

Runs three sources and computes the gap:
  - C (model.c via tests/host/main_host)
  - Python C-faithful oracle (tests/oracle/python_reference_c.py)
  - Python PyTorch oracle (tests/oracle/python_reference_torch.py)

Predeclared tolerances:
  - C vs Python C-faithful: exact integer match (0 tolerance)
  - C vs PyTorch: relative gap > 50% is expected (divergence documented)
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, result.stderr
    for line in result.stdout.splitlines():
        if line.startswith("LOGITS"):
            values = [float(v) for v in line.split()[1:]]
            return values, None
    return None, f"No LOGITS line in: {result.stdout}"


def main():
    # 1. C
    c_logits, err = run(["./main_host"], cwd=ROOT / "tests/host")
    if c_logits is None:
        sys.exit(f"C failed: {err}")

    # 2. Python C-faithful
    py_c, err = run(["python3", "tests/oracle/python_reference_c.py"], cwd=ROOT)
    if py_c is None:
        sys.exit(f"Python C-faithful failed: {err}")

    # 3. Python PyTorch
    py_t, err = run(["python3", "tests/oracle/python_reference_torch.py"], cwd=ROOT)
    if py_t is None:
        sys.exit(f"Python PyTorch failed: {err}")

    # C vs Python C-faithful: exact match required
    c_vs_pyc = [abs(a - b) for a, b in zip(c_logits, py_c)]
    c_vs_pyc_max = max(c_vs_pyc)

    # C vs PyTorch: relative gap
    c_vs_pyt = [abs(a - b) / (abs(b) + 1e-9) for a, b in zip(c_logits, py_t)]
    c_vs_pyt_max = max(c_vs_pyt)

    print("=" * 60)
    print("WP2 - Python-C equivalence")
    print("=" * 60)
    print(f"C logits:              {c_logits}")
    print(f"Python C-faithful:     {py_c}")
    print(f"Python PyTorch:        {py_t}")
    print()
    print(f"C vs Python C-faithful max abs gap: {c_vs_pyc_max:.6f}")
    print(f"C vs PyTorch max relative gap:      {c_vs_pyt_max:.4f}")
    print()

    # Verdict
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    if c_vs_pyc_max == 0:
        print("PASS: C and Python C-faithful agree exactly.")
    else:
        print(f"FAIL: C and Python C-faithful differ (max gap {c_vs_pyc_max}).")

    if c_vs_pyt_max > 0.5:
        print(f"DOCUMENTED DIVERGENCE: C and PyTorch differ by {c_vs_pyt_max*100:.1f}% (expected, see architecture_weight_map.md).")
    else:
        print("UNEXPECTED: C and PyTorch are close. Check architecture mapping.")


if __name__ == "__main__":
    main()
