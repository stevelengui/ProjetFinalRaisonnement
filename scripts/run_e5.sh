#!/bin/bash
cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 E5 — SECURITY META-REASONING (RQ3)"
echo "=========================================="
echo ""

mkdir -p experiments/E5_security/results

python experiments/E5_security/run_experiment.py

echo ""
echo "=========================================="
echo "✅ E5 TERMINÉ"
echo "=========================================="
echo ""
echo "📄 Résultats:"
echo "   experiments/E5_security/results/e5_results.json"
