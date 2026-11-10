#!/bin/bash
# Validation globale de toutes les expériences E0-E7

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🎯 VALIDATION GLOBALE - E0 à E7"
echo "=========================================="
echo ""

declare -A experiments=(
    ["E0"]="experiments/E0_context_to_contract/results/e0_results.json"
    ["E1"]="experiments/E1_adaptive_fidelity/results/e1_results.json"
    ["E2"]="experiments/E2_lifecycle_replay/results/e2_results.json"
    ["E3"]="experiments/E3_fault_injection/results/e3_results.json"
    ["E4"]="experiments/E4_domain_shift/results/e4_results.json"
    ["E5"]="experiments/E5_security/results/e5_results.json"
    ["E6"]="experiments/E6_decision_records/results/e6_results.json"
    ["E7"]="experiments/E7_ablation/results/e7_results.json"
)

all_pass=true

for exp_id in E0 E1 E2 E3 E4 E5 E6 E7; do
    result_file="${experiments[$exp_id]}"
    
    if [ -f "$result_file" ]; then
        # Vérifier si le fichier contient des erreurs
        if grep -q '"error"' "$result_file" 2>/dev/null; then
            echo "❌ $exp_id: ERREUR DÉTECTÉE"
            all_pass=false
        else
            echo "✅ $exp_id: Résultats présents ($(du -h "$result_file" | cut -f1))"
        fi
    else
        echo "❌ $exp_id: Fichier manquant"
        all_pass=false
    fi
done

echo ""
echo "=========================================="
if [ "$all_pass" = true ]; then
    echo "🎉 TOUTES LES EXPÉRIENCES SONT VALIDÉES"
else
    echo "⚠️ Certaines expériences ont échoué"
fi
echo "=========================================="
