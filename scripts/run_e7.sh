#!/bin/bash
cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 E7 — MECHANISM-LEVEL ABLATION (Cross-RQ)"
echo "=========================================="
echo ""

mkdir -p experiments/E7_ablation/results

python experiments/E7_ablation/run_experiment.py

echo ""
echo "=========================================="
echo "✅ E7 TERMINÉ"
echo "=========================================="
echo ""
echo "📄 Résultats:"
echo "   experiments/E7_ablation/results/e7_results.json"
