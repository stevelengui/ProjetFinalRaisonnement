#!/usr/bin/env python3
"""
Correction P1-3 : Synchronisation des claims
"""

import os

# Fichier article
TEX_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "article.tex"
)


def sync_claims():
    """Applique les corrections de synchronisation"""

    print("=" * 70)
    print("📊 SYNCHRONISATION DES CLAIMS (P1-3)")
    print("=" * 70)

    if not os.path.exists(TEX_FILE):
        print(f"⚠️ {TEX_FILE} non trouvé")
        print("   Créer le fichier article.tex d'abord")
        return

    with open(TEX_FILE, 'r') as f:
        content = f.read()

    changes = 0

    # 1. Retirer Table X
    import re
    table_x_pattern = r'\\begin\{table\}.*?Three-Strict-Requirement.*?\\end\{table\}'
    if re.search(table_x_pattern, content, re.DOTALL):
        content = re.sub(table_x_pattern, '', content, flags=re.DOTALL)
        print("✅ Table X (three strict requirements) retirée")
        changes += 1

    # 2. Traduire Table XI
    french_to_english = {
        "Architecture méta-raisonnement": "Meta-reasoning architecture",
        "Formulation contexte-contrat": "Context-to-contract formulation",
        "Sélection adaptive": "Adaptive selection",
        "Réduction 65% coût": "65% cost reduction",
        "Fiabilité": "Reliability",
        "Domain-shift": "Domain-shift",
        "Sécurité": "Security",
        "Décisions auditables": "Auditable decisions",
        "Intervention cycle de vie": "Lifecycle intervention",
        "Adaptation runtime": "Runtime adaptation",
        "Validation 5-domaines": "5-domain validation",
        "Validation hardware": "Hardware validation",
        "MAML requis": "MAML required",
        "XAI = explicabilité": "XAI = explainability",
    }

    for fr, en in french_to_english.items():
        if fr in content:
            content = content.replace(fr, en)
            changes += 1
            print(f"✅ Traduit: {fr} → {en}")

    # 3. Reformuler "fully reproducible"
    old_repro = "The complete implementation is open-source and fully reproducible."
    new_repro = ("The complete implementation is open-source. "
                 "Reproducibility requires the artifacts (code, seeds, scripts) "
                 "available in the public repository.")
    if old_repro in content:
        content = content.replace(old_repro, new_repro)
        print("✅ 'fully reproducible' reformulé")
        changes += 1

    # 4. Retirer mention "audit committee"
    old_audit = "following the requirements established by the audit committee"
    new_audit = "as part of our evaluation protocol"
    if old_audit in content:
        content = content.replace(old_audit, new_audit)
        print("✅ Mention 'audit committee' retirée")
        changes += 1

    # Sauvegarder
    with open(TEX_FILE, 'w') as f:
        f.write(content)

    print(f"\n✅ {changes} corrections appliquées")


if __name__ == "__main__":
    sync_claims()
