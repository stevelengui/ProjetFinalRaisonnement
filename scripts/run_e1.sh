#!/bin/bash
# Script de lancement E1 — Adaptive Evaluation-Fidelity

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 E1 — ADAPTIVE EVALUATION-FIDELITY (RQ2)"
echo "=========================================="
echo ""

mkdir -p experiments/E1_adaptive_fidelity/results

python experiments/E1_adaptive_fidelity/run_experiment.py

echo ""
echo "=========================================="
echo "✅ E1 TERMINÉ"
echo "=========================================="
echo ""
echo "📄 Résultats:"
echo "   experiments/E1_adaptive_fidelity/results/e1_results.json"
