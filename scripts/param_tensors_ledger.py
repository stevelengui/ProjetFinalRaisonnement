#!/usr/bin/env python3
"""
param_tensors_ledger.py - WP1 tensor inventory

Parses model_weights.h for the 18 declared int8_t arrays, checks their
initializers in arrays/*.txt, and writes a CSV with one row per tensor.

Output: evidence_registry/derived/parameter_tensors.csv
"""

import csv
import re
import sys
from pathlib import Path

HEADER = Path("firmware/model/model_weights.h")
ARRAYS_DIR = Path("firmware/model/arrays")
OUT = Path("evidence_registry/derived/parameter_tensors.csv")

# Layer mapping (from the thesis roadmap and model.py)
LAYER_MAP = {
    "conv1_weight": "Conv1D",
    "conv1_bias": "Conv1D",
    "conv2_weight": "Conv2D",
    "conv2_bias": "Conv2D",
    "lstm_weight_ih": "LSTM",
    "lstm_weight_hh": "LSTM",
    "lstm_bias_ih": "LSTM",
    "lstm_bias_hh": "LSTM",
    "router_fc1_weight": "Router",
    "router_fc1_bias": "Router",
    "router_fc2_weight": "Router",
    "router_fc2_bias": "Router",
    "fusion_weight": "Fusion",
    "fusion_bias": "Fusion",
    "fc1_weight": "Classifier",
    "fc1_bias": "Classifier",
    "fc2_weight": "Classifier",
    "fc2_bias": "Classifier",
}

ARRAY_RE = re.compile(r"extern\s+const\s+int8_t\s+(\w+)\s*\[\s*(\d+)\s*\]\s*;")


def main():
    if not HEADER.is_file():
        sys.exit(f"ERROR: header not found: {HEADER}")
    if not ARRAYS_DIR.is_dir():
        sys.exit(f"ERROR: arrays dir not found: {ARRAYS_DIR}")

    text = HEADER.read_text(encoding="utf-8")
    rows = []
    for match in ARRAY_RE.finditer(text):
        symbol = match.group(1)
        declared = int(match.group(2))
        layer = LAYER_MAP.get(symbol, "UNKNOWN")
        line_no = text[:match.start()].count("\n") + 1

        # Count initializer values in arrays/<symbol>_array.txt
        init_file = ARRAYS_DIR / f"{symbol}_array.txt"
        if init_file.is_file():
            init_text = init_file.read_text(encoding="utf-8")
            init_values = [v for v in re.split(r"[,\s]+", init_text) if v]
            initializer_count = len(init_values)
        else:
            initializer_count = -1  # missing

        storage_bytes = declared * 1  # int8_t
        status = "OK" if initializer_count == declared else "MISMATCH"
        if initializer_count == -1:
            status = "MISSING_INITIALIZER"

        rows.append({
            "symbol": symbol,
            "layer": layer,
            "shape": f"[{declared}]",
            "dtype": "int8_t",
            "declared_count": declared,
            "initializer_count": initializer_count,
            "storage_bytes": storage_bytes,
            "provenance": f"model_weights.h:{line_no}",
            "status": status,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "symbol", "layer", "shape", "dtype", "declared_count",
            "initializer_count", "storage_bytes", "provenance", "status"
        ])
        writer.writeheader()
        writer.writerows(rows)

    total_declared = sum(r["declared_count"] for r in rows)
    total_init = sum(r["initializer_count"] for r in rows if r["initializer_count"] > 0)
    mismatches = [r for r in rows if r["status"] != "OK"]

    print(f"Tensors found: {len(rows)}")
    print(f"Total declared: {total_declared}")
    print(f"Total initializer: {total_init}")
    if mismatches:
        print("Mismatches:")
        for r in mismatches:
            print(f"  {r['symbol']}: declared={r['declared_count']} init={r['initializer_count']} ({r['status']})")
    print(f"CSV written to {OUT}")


if __name__ == "__main__":
    main()
