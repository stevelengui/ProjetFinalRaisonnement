#!/usr/bin/env python3
"""Calibrer les claims"""

import os

CLAIMS = {
    "Architecture méta-raisonnement": ("KEEP", "Conceptuelle"),
    "Formulation contexte-à-contrat": ("PROVE", "E0 99.1%"),
    "Sélection adaptive": ("PROVE", "E1 36.5%"),
    "Réduction 65% coût": ("REMOVE", "36.5% réel"),
    "Fiabilité": ("PROVE", "E3 renversement"),
    "Domain-shift": ("BOUNDED", "E4"),
    "Sécurité": ("PROVE", "E5"),
    "Décisions auditables": ("PROVE", "E6"),
    "Intervention cycle de vie": ("PROVE", "E2"),
    "Adaptation runtime": ("BOUNDED", "replay"),
    "Validation 5-domaines": ("REMOVE", "2 domaines"),
    "Validation hardware": ("REMOVE", "aucune"),
    "373128 params": ("REMOVE", "7651 réels"),
    "8.53 KB": ("REMOVE", "7.47 KiB"),
    "MAML requis": ("REMOVE", "1 outil/8"),
    "XAI = explicabilité": ("REMOVE", "niveau objet"),
}

def generate():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lines = ["# CALIBRATION DES CLAIMS", ""]
    lines.append(f"## Résumé")
    for status in ["KEEP", "PROVE", "BOUNDED", "REMOVE"]:
        count = sum(1 for s, _ in CLAIMS.values() if s == status)
        lines.append(f"- {status}: {count}")
    lines.append("")
    lines.append("## Détail")
    lines.append("| Claim | Statut | Evidence |")
    lines.append("|-------|--------|----------|")
    for claim, (status, evidence) in CLAIMS.items():
        lines.append(f"| {claim} | {status} | {evidence} |")
    
    output_path = os.path.join(base, "CALIBRATED_CLAIMS.md")
    with open(output_path, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"✅ Sauvegardé: {output_path}")
    for status in ["KEEP", "PROVE", "BOUNDED", "REMOVE"]:
        count = sum(1 for s, _ in CLAIMS.values() if s == status)
        print(f"   {status}: {count}")

if __name__ == "__main__":
    generate()
