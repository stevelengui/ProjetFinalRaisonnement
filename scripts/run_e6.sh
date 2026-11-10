#!/bin/bash
cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 E6 — DESIGN DECISION RECORDS (RQ4)"
echo "=========================================="
echo ""

mkdir -p experiments/E6_decision_records/results

python experiments/E6_decision_records/run_experiment.py

echo ""
echo "=========================================="
echo "✅ E6 TERMINÉ"
echo "=========================================="
echo ""
echo "📄 Résultats:"
echo "   experiments/E6_decision_records/results/e6_results.json"
