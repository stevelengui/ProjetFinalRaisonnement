#!/usr/bin/env python3
"""
param_ledger.py — Parameter ledger for the hybrid QNN-SNN model.

Parses the declared int8_t weight arrays in model_weights.h, sums them,
groups by functional layer, and writes:
  - a per-layer CSV   (evidence_registry/ledgers/param_ledger.csv)
  - a summary JSON    (evidence_registry/ledgers/param_ledger.json)
  - a console report

The expected total for the current model is 7,651 parameters.
If the parsed total differs, the script exits with a non-zero code.

Usage:
    python3 scripts/param_ledger.py \
        --header firmware/model/model_weights.h \
        --out evidence_registry/ledgers/param_ledger.csv
"""

import argparse
import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

# Map array name -> functional layer
LAYER_MAP = OrderedDict([
    ("conv1_weight",     "Conv1D"),
    ("conv1_bias",       "Conv1D"),
    ("conv2_weight",     "Conv2D"),
    ("conv2_bias",       "Conv2D"),
    ("lstm_weight_ih",   "LSTM"),
    ("lstm_weight_hh",   "LSTM"),
    ("lstm_bias_ih",     "LSTM"),
    ("lstm_bias_hh",     "LSTM"),
    ("router_fc1_weight", "Router"),
    ("router_fc1_bias",   "Router"),
    ("router_fc2_weight", "Router"),
    ("router_fc2_bias",   "Router"),
    ("fusion_weight",    "Fusion"),
    ("fusion_bias",      "Fusion"),
    ("fc1_weight",       "FC1"),
    ("fc1_bias",         "FC1"),
    ("fc2_weight",       "Output"),
    ("fc2_bias",         "Output"),
])

# Expected total (from the C declarations, verified manually)
EXPECTED_TOTAL = 7651

ARRAY_RE = re.compile(
    r"extern\s+const\s+int8_t\s+(\w+)\s*\[\s*(\d+)\s*\]\s*;"
)


def parse_header(path: Path):
    text = path.read_text(encoding="utf-8")
    arrays = OrderedDict()
    for match in ARRAY_RE.finditer(text):
        name, size = match.group(1), int(match.group(2))
        if name in arrays:
            raise ValueError(f"Duplicate declaration: {name}")
        arrays[name] = size
    return arrays


def build_rows(arrays):
    rows = []
    for name, size in arrays.items():
        layer = LAYER_MAP.get(name, "UNMAPPED")
        rows.append({
            "array": name,
            "layer": layer,
            "elements": size,
        })
    return rows


def build_layer_summary(rows):
    summary = OrderedDict()
    for row in rows:
        layer = row["layer"]
        summary.setdefault(layer, 0)
        summary[layer] += row["elements"]
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--header", required=True,
                        help="Path to model_weights.h")
    parser.add_argument("--out", required=True,
                        help="Path to output CSV")
    args = parser.parse_args()

    header_path = Path(args.header)
    if not header_path.is_file():
        sys.exit(f"ERROR: header not found: {header_path}")

    arrays = parse_header(header_path)
    if not arrays:
        sys.exit(f"ERROR: no int8_t arrays found in {header_path}")

    rows = build_rows(arrays)
    layer_summary = build_layer_summary(rows)
    total = sum(row["elements"] for row in rows)

    out_csv = Path(args.out)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["array", "layer", "elements"])
        writer.writeheader()
        writer.writerows(rows)

    out_json = out_csv.with_suffix(".json")
    summary = {
        "header": str(header_path),
        "expected_total": EXPECTED_TOTAL,
        "parsed_total": total,
        "match": total == EXPECTED_TOTAL,
        "layer_summary": layer_summary,
        "arrays": rows,
    }
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Console report
    print(f"Parsed header : {header_path}")
    print(f"Arrays found  : {len(rows)}")
    print(f"Total params  : {total}")
    print(f"Expected      : {EXPECTED_TOTAL}")
    print("")
    print("Per-layer summary:")
    for layer, count in layer_summary.items():
        print(f"  {layer:<10} {count:>6}")
    print("")

    if total != EXPECTED_TOTAL:
        print(f"ERROR: total mismatch ({total} != {EXPECTED_TOTAL})",
              file=sys.stderr)
        sys.exit(2)

    print(f"OK: {total} parameters verified. CSV: {out_csv}")
    print(f"OK: JSON: {out_json}")


if __name__ == "__main__":
    main()
