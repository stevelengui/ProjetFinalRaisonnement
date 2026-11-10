#!/usr/bin/env python3
"""Correction E6 - Ajouter contrefactuels"""
import os

FILEPATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments/E6_decision_records/run_experiment.py"
)

with open(FILEPATH, 'r') as f:
    content = f.read()

# Ajouter import Counterfactual si manquant
if "Counterfactual" not in content.split("def ")[0]:
    content = content.replace(
        "from decision_record import (",
        "from decision_record import (\n    Counterfactual,"
    )

# Ajouter contrefactuels à record2
if "cf_002a" not in content:
    old = '        records.append(record2)'
    new = '''        # Contrefactuels pour record2
        record2.counterfactuals = [
            Counterfactual("cf_002a", "Si accuracy_min était 0.91",
                          "rejeté", "accepté", "accuracy_min: 0.95→0.91", True),
            Counterfactual("cf_002b", "Si design avait ECC",
                          "rejeté", "accepté", "has_protection: False→True", True),
            Counterfactual("cf_002c", "Si mémoire relâchée",
                          "rejeté", "toujours rejeté", "memory: 32→64", True),
        ]
        records.append(record2)'''
    content = content.replace(old, new, 1)

# Ajouter contrefactuels à record3
if "cf_003a" not in content:
    old3 = '        records.append(record3)'
    new3 = '''        # Contrefactuels pour record3
        record3.counterfactuals = [
            Counterfactual("cf_003a", "Si incertitude faible",
                          "DEFER", "ACCEPT", "uncertainty: 0.15→0.03", True),
            Counterfactual("cf_003b", "Si évaluation HF dispo",
                          "DEFER", "ACCEPT", "hf: False→True", True),
            Counterfactual("cf_003c", "Si preuves contradictoires",
                          "DEFER", "Conflit", "contradictory: False→True", True),
        ]
        records.append(record3)'''
    content = content.replace(old3, new3, 1)

with open(FILEPATH, 'w') as f:
    f.write(content)

print(f"✅ E6 corrigé: {FILEPATH}")
print("   3 contrefactuels ajoutés par DDR")
