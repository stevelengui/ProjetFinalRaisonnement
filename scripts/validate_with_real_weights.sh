#!/bin/bash
# Validation avec les VRAIS fichiers de poids

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🔍 VALIDATION AVEC VRAIS POIDS"
echo "=========================================="
echo ""

echo "📊 1. Profiling mémoire RÉEL..."
python meta_reasoning/memory_profiler_v2.py

echo ""
echo "📊 2. Mise à jour du registre..."
python meta_reasoning/update_registry_real.py

echo ""
echo "📊 3. Validation externe des contrats..."
python experiments/E0_context_to_contract/external_validator.py

echo ""
echo "=========================================="
echo "✅ VALIDATION TERMINÉE"
echo "=========================================="
