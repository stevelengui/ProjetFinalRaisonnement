#!/bin/bash
cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 E2 — LIFECYCLE REPLAY (RQ5)"
echo "=========================================="
echo ""

mkdir -p experiments/E2_lifecycle_replay/results

python experiments/E2_lifecycle_replay/run_experiment.py

echo ""
echo "=========================================="
echo "✅ E2 TERMINÉ"
echo "=========================================="
echo ""
echo "📄 Résultats:"
echo "   experiments/E2_lifecycle_replay/results/e2_results.json"
