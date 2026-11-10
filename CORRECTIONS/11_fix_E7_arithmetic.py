#!/usr/bin/env python3
"""
Correction P0-4 : E7 - Recalcul de la dégradation
Formule: D_degrad = (DCR_full - DCR_ablation) / DCR_full
"""

import os
import json

# Résultats E7 (DCR values)
E7_RESULTS = {
    "A0_FULL": 0.94,
    "A1_NO_ADAPTIVE": 0.70,
    "A2_NO_UNCERTAINTY": 0.63,
    "A3_NO_PROVENANCE": 0.70,
    "A4_FIXED_CONTRACT": 0.47,
    "A5_NO_RELIABILITY": 0.67,
    "A6_NO_DOMAIN_SHIFT": 0.60,
    "A7_NO_SECURITY": 0.57,
    "A8_NO_ASSURANCE": 0.83,
    "A9_NO_VALIDITY": 0.83,
    "A10_NO_EVI": 0.77,
}


def recalculate_degradation():
    """Recalcule les dégradations avec la formule exacte"""

    print("=" * 70)
    print("📊 E7 - RECALCUL DES DÉGRADATIONS (P0-4)")
    print("=" * 70)

    dcr_full = E7_RESULTS["A0_FULL"]
    print(f"\nDCR Full = {dcr_full:.2f}")
    print(f"\nFormule: D_degrad = (DCR_full - DCR_ablation) / DCR_full")
    print(f"\n{'Ablation':<25} {'DCR':<8} {'D_degrad':<10} {'D_degrad%':<10} {'Catégorie':<12}")
    print("-" * 70)

    results = []
    for ablation, dcr in E7_RESULTS.items():
        if ablation == "A0_FULL":
            continue

        d_degrad = (dcr_full - dcr) / dcr_full
        d_degrad_pct = d_degrad * 100

        if d_degrad_pct > 15:
            category = "CRITICAL"
        elif d_degrad_pct > 5:
            category = "IMPORTANT"
        else:
            category = "MINOR"

        results.append({
            "ablation": ablation,
            "dcr": dcr,
            "d_degrad": round(d_degrad, 4),
            "d_degrad_pct": round(d_degrad_pct, 2),
            "category": category
        })

        print(f"{ablation:<25} {dcr:<8.2f} {d_degrad:<10.4f} {d_degrad_pct:<10.2f} {category:<12}")

    results.sort(key=lambda r: r["d_degrad"], reverse=True)

    print(f"\n{'=' * 70}")
    print("📊 CLASSEMENT FINAL (P0-4 CORRIGÉ)")
    print("=" * 70)

    for i, r in enumerate(results, 1):
        marker = "🔴" if r["category"] == "CRITICAL" else ("🟡" if r["category"] == "IMPORTANT" else "🟢")
        print(f"{marker} {i}. {r['ablation']:<25} {r['d_degrad_pct']:.2f}%")

    print(f"\n{'=' * 70}")
    print("✅ VÉRIFICATION")
    print("=" * 70)

    critical_count = sum(1 for r in results if r["category"] == "CRITICAL")
    print(f"Mécanismes critiques (>15%): {critical_count}/10")
    print(f"Max dégradation: {results[0]['d_degrad_pct']:.2f}% ({results[0]['ablation']})")

    a4 = next(r for r in results if r["ablation"] == "A4_FIXED_CONTRACT")
    print(f"\n⚠️ A4_FIXED_CONTRACT: DCR = {a4['dcr']:.2f}")
    print(f"   D_degrad = ({dcr_full:.2f} - {a4['dcr']:.2f}) / {dcr_full:.2f} = {a4['d_degrad']:.4f}")
    print(f"   → {a4['d_degrad_pct']:.1f}% (pas 100%)")
    print(f"   → La valeur '100%' était INCORRECTE")

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "artifacts/e7_recalculated.json"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump({
            "dcr_full": dcr_full,
            "formula": "D_degrad = (DCR_full - DCR_ablation) / DCR_full",
            "results": results
        }, f, indent=2)

    print(f"\n💾 Résultats: {output_path}")

    return results


if __name__ == "__main__":
    recalculate_degradation()
