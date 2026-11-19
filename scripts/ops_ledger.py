#!/usr/bin/env python3
"""
ops_ledger.py — Operation (MAC) ledger for the hybrid QNN-SNN model.

Parses the *_OPS and TOTAL_OPS macros in model_weights.h, evaluates them,
and writes:
  - a per-layer CSV   (evidence_registry/ledgers/ops_ledger.csv)
  - a summary JSON    (evidence_registry/ledgers/ops_ledger.json)
  - a console report

The expected total for the current model is 373,128 MACs.
If the parsed total differs, the script exits with a non-zero code.

Usage:
    python3 scripts/ops_ledger.py \
        --header llm_nas/model_weights.h \
        --out evidence_registry/ledgers/ops_ledger.csv
"""

import argparse
import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

EXPECTED_TOTAL = 373128

# Layer order (from model_weights.h)
OPS_ORDER = [
    ("CONV1_OPS",  "Conv1D"),
    ("CONV2_OPS",  "Conv2D"),
    ("LSTM_OPS",   "LSTM"),
    ("LIF_OPS",    "SNN-LIF"),
    ("FC_OPS",     "FC"),
    ("ROUTER_OPS", "Router"),
]

# Matches:  #define NAME (expression)   or   #define NAME value
DEFINE_RE = re.compile(
    r"^\s*#define\s+(\w+)\s+(.+?)\s*$",
    re.MULTILINE,
)


def parse_defines(path: Path):
    text = path.read_text(encoding="utf-8")
    defs = OrderedDict()
    for match in DEFINE_RE.finditer(text):
        name, expr = match.group(1), match.group(2)
        # Strip trailing // comment
        expr = re.sub(r"//.*$", "", expr).strip()
        defs[name] = expr
    return defs


def evaluate(expr: str, defs: dict, seen=None):
    """Recursively evaluate an arithmetic macro expression."""
    if seen is None:
        seen = set()

    # Replace identifiers by their values
    def repl(m):
        name = m.group(0)
        if name in seen:
            raise ValueError(f"Circular macro: {name}")
        if name in defs:
            return f"({evaluate(defs[name], defs, seen | {name})})"
        return name  # leave unknown (will fail eval)

    # Only replace identifiers that are known macros
    tokens = re.findall(r"[A-Za-z_]\w*", expr)
    for tok in tokens:
        if tok in defs:
            expr = re.sub(rf"\b{tok}\b",
                          lambda _m, t=tok: f"({evaluate(defs[t], defs, seen | {t})})",
                          expr)

    # Now evaluate the arithmetic expression
    try:
        return int(eval(expr, {"__builtins__": {}}, {}))
    except Exception as e:
        raise ValueError(f"Cannot evaluate expression: {expr!r} ({e})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--header", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    header_path = Path(args.header)
    if not header_path.is_file():
        sys.exit(f"ERROR: header not found: {header_path}")

    defs = parse_defines(header_path)

    rows = []
    for macro, layer in OPS_ORDER:
        if macro not in defs:
            sys.exit(f"ERROR: macro {macro} not found in {header_path}")
        value = evaluate(defs[macro], defs)
        rows.append({"macro": macro, "layer": layer, "operations": value})

    total = sum(r["operations"] for r in rows)

    out_csv = Path(args.out)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["macro", "layer", "operations"])
        writer.writeheader()
        writer.writerows(rows)

    out_json = out_csv.with_suffix(".json")
    summary = {
        "header": str(header_path),
        "expected_total": EXPECTED_TOTAL,
        "parsed_total": total,
        "match": total == EXPECTED_TOTAL,
        "layers": rows,
        "TOTAL_OPS_macro": defs.get("TOTAL_OPS", None),
    }
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Parsed header : {header_path}")
    print(f"Macros found  : {len(defs)}")
    print(f"Total ops     : {total}")
    print(f"Expected      : {EXPECTED_TOTAL}")
    print("")
    print("Per-layer summary:")
    for r in rows:
        print(f"  {r['layer']:<10} {r['operations']:>8}")
    print("")

    if total != EXPECTED_TOTAL:
        print(f"ERROR: total mismatch ({total} != {EXPECTED_TOTAL})",
              file=sys.stderr)
        sys.exit(2)

    print(f"OK: {total} operations verified. CSV: {out_csv}")
    print(f"OK: JSON: {out_json}")


if __name__ == "__main__":
    main()
