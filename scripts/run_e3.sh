#!/bin/bash
# Script de lancement E3 — Fault Injection

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 E3 — FAULT INJECTION (RQ3)"
echo "=========================================="
echo ""

mkdir -p experiments/E3_fault_injection/results

python experiments/E3_fault_injection/run_experiment.py

echo ""
echo "=========================================="
echo "✅ E3 TERMINÉ"
echo "=========================================="
echo ""
echo "📄 Résultats:"
echo "   experiments/E3_fault_injection/results/e3_results.json"
