#!/bin/bash
cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 E4 — DOMAIN-SHIFT META-REASONING (RQ3)"
echo "=========================================="
echo ""

mkdir -p experiments/E4_domain_shift/results

python experiments/E4_domain_shift/run_experiment.py

echo ""
echo "=========================================="
echo "✅ E4 TERMINÉ"
echo "=========================================="
echo ""
echo "📄 Résultats:"
echo "   experiments/E4_domain_shift/results/e4_results.json"
