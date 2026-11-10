#!/bin/bash
# Script de lancement E0 — Context-to-Contract

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 E0 — CONTEXT-TO-CONTRACT (RQ1)"
echo "=========================================="
echo ""

# Créer le dossier expérimental
mkdir -p experiments/E0_context_to_contract/results

# Lancer l'expérience
python experiments/E0_context_to_contract/run_experiment.py

echo ""
echo "=========================================="
echo "✅ E0 TERMINÉ"
echo "=========================================="
echo ""
echo "📄 Résultats disponibles dans :"
echo "   experiments/E0_context_to_contract/results/e0_results.json"
echo ""
