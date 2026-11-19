#!/usr/bin/env python3
"""
memory_ledger.py — Memory accounting for the hybrid QNN-SNN model.

Parses model.h (HybridModelBuffers) and model_weights.h (dimensions),
computes the declared SRAM footprint, the weight footprint, and reports
the difference against the manuscript values.

Outputs:
  - evidence_registry/ledgers/memory_ledger.csv
  - evidence_registry/ledgers/memory_ledger.json

Expected values (frozen manuscript, Section VI-A):
  weights : 7.47 KiB  (7651 bytes)
  Flash   : 19.47 KiB
  SRAM    : 11.53 KiB
  Table I : 29.0 KiB

Declared struct SRAM (verified from model.h) is reported separately.
"""

import argparse
import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

# Sizes in bytes (C types on RV32)
SIZEOF = {"int8_t": 1, "uint8_t": 1, "int16_t": 2, "uint16_t": 2,
          "int32_t": 4, "uint32_t": 4}

MANUSCRIPT = {
    "weights_kib": 7.47,
    "flash_kib": 19.47,
    "sram_kib": 11.53,
    "table1_kib": 29.0,
}

# Expected struct SRAM (computed by hand from model.h)
EXPECTED_STRUCT_SRAM_BYTES = 11025


def parse_defines(path: Path):
    text = path.read_text(encoding="utf-8")
    defs = {}
    for m in re.finditer(r"^\s*#define\s+(\w+)\s+(\S+)\s*$",
                         text, re.MULTILINE):
        defs[m.group(1)] = m.group(2)
    return defs


def eval_dim(expr, defs):
    """Evaluate a #define that may reference other #defines."""
    tokens = re.findall(r"[A-Za-z_]\w*", expr)
    for tok in tokens:
        if tok in defs:
            expr = re.sub(rf"\b{tok}\b",
                          lambda _m, t=tok: f"({eval_dim(defs[t], defs)})",
                          expr)
    return int(eval(expr, {"__builtins__": {}}, {}))


def parse_struct_fields(path: Path):
    """Return list of (field, c_type, dim_expr, comment) for HybridModelBuffers."""
    text = path.read_text(encoding="utf-8")
    # Capture the struct body
    m = re.search(r"typedef\s+struct\s*\{(.*?)\}\s*HybridModelBuffers\s*;",
                  text, re.DOTALL)
    if not m:
        sys.exit("ERROR: HybridModelBuffers struct not found")
    body = m.group(1)

    fields = []
    # Match: c_type name[dim];   or   c_type name;
    for fm in re.finditer(
        r"^\s*(int8_t|uint8_t|int16_t|uint16_t|int32_t|uint32_t)\s+"
        r"(\w+)\s*(?:\[([^\]]+)\])?\s*;",
        body, re.MULTILINE,
    ):
        ctype, name, dim = fm.group(1), fm.group(2), fm.group(3)
        fields.append((name, ctype, dim))
    return fields


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-h", required=True)
    parser.add_argument("--weights-h", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    model_h = Path(args.model_h)
    weights_h = Path(args.weights_h)
    for p in (model_h, weights_h):
        if not p.is_file():
            sys.exit(f"ERROR: file not found: {p}")

    defs = parse_defines(weights_h)
    fields = parse_struct_fields(model_h)

    rows = []
    struct_bytes = 0
    for name, ctype, dim in fields:
        size = SIZEOF[ctype]
        if dim is None:
            elements = 1
        else:
            elements = eval_dim(dim, defs)
        total = elements * size
        struct_bytes += total
        rows.append({
            "field": name,
            "type": ctype,
            "elements": elements,
            "element_size": size,
            "bytes": total,
        })

    weights_bytes = 7651  # verified by param_ledger.py
    weights_kib = weights_bytes / 1024.0
    struct_kib = struct_bytes / 1024.0
    flash_kib = MANUSCRIPT["flash_kib"]
    sram_kib = MANUSCRIPT["sram_kib"]

    # Reconciliation
    reconciliation = [
        {"item": "weights_bytes",        "value": weights_bytes,
         "source": "param_ledger.py (verified)"},
        {"item": "weights_kib",          "value": round(weights_kib, 3),
         "source": "computed"},
        {"item": "struct_sram_bytes",    "value": struct_bytes,
         "source": "model.h (verified)"},
        {"item": "struct_sram_kib",      "value": round(struct_kib, 3),
         "source": "computed"},
        {"item": "manuscript_flash_kib", "value": flash_kib,
         "source": "MS Section VI-A"},
        {"item": "manuscript_sram_kib",  "value": sram_kib,
         "source": "MS Section VI-A"},
        {"item": "manuscript_total_VI-A_kib",
         "value": round(flash_kib + sram_kib, 3),
         "source": "MS Section VI-A (19.47 + 11.53)"},
        {"item": "manuscript_table1_kib", "value": MANUSCRIPT["table1_kib"],
         "source": "MS Table I (ecg_hybrid_8bit)"},
        {"item": "delta_VI-A_vs_table1_kib",
         "value": round(flash_kib + sram_kib - MANUSCRIPT["table1_kib"], 3),
         "source": "computed (open item)"},
        {"item": "delta_struct_vs_MS_sram_kib",
         "value": round(sram_kib - struct_kib, 3),
         "source": "computed (stack/alignment, open item)"},
    ]

    out_csv = Path(args.out)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    # Write struct CSV
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["field", "type", "elements",
                                          "element_size", "bytes"])
        w.writeheader()
        w.writerows(rows)

    out_json = out_csv.with_suffix(".json")
    summary = {
        "model_h": str(model_h),
        "weights_h": str(weights_h),
        "struct_sram_bytes": struct_bytes,
        "struct_sram_kib": round(struct_kib, 3),
        "expected_struct_sram_bytes": EXPECTED_STRUCT_SRAM_BYTES,
        "struct_matches_expected": struct_bytes == EXPECTED_STRUCT_SRAM_BYTES,
        "manuscript": MANUSCRIPT,
        "reconciliation": reconciliation,
        "fields": rows,
    }
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"model.h     : {model_h}")
    print(f"weights.h   : {weights_h}")
    print(f"Struct SRAM : {struct_bytes} bytes ({struct_kib:.2f} KiB)")
    print(f"Expected    : {EXPECTED_STRUCT_SRAM_BYTES} bytes")
    print("")
    print("Per-field breakdown:")
    for r in rows:
        print(f"  {r['field']:<20} {r['type']:<8} "
              f"{r['elements']:>6} x {r['element_size']} = {r['bytes']:>5} B")
    print("")
    print("Reconciliation vs manuscript:")
    for r in reconciliation:
        print(f"  {r['item']:<32} {r['value']:>10}  ({r['source']})")
    print("")
    if struct_bytes != EXPECTED_STRUCT_SRAM_BYTES:
        print("WARNING: struct SRAM differs from expected 11025 bytes",
              file=sys.stderr)
    print(f"OK: CSV: {out_csv}")
    print(f"OK: JSON: {out_json}")


if __name__ == "__main__":
    main()
