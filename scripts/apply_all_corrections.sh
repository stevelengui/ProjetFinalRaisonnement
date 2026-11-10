#!/bin/bash
# Applique toutes les corrections

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🔧 APPLICATION DE TOUTES LES CORRECTIONS"
echo "=========================================="
echo ""

# 1. Corriger E5 (ASR différents)
echo "📊 1. Correction E5 (ASR différents)..."
python CORRECTIONS/1_fix_E5_ASR.py

# 2. Ajouter contrefactuels E6
echo ""
echo "📊 2. Ajout contrefactuels E6..."
python CORRECTIONS/2_add_counterfactuals_E6.py

# 3. Mesurer M_runtime/M_code
echo ""
echo "📊 3. Mesure M_runtime/M_code..."
python CORRECTIONS/3_measure_M_runtime_code.py

# 4. Calibrer les claims
echo ""
echo "📊 4. Calibration des claims..."
python CORRECTIONS/4_calibrate_claims.py

# 5. Relancer les expériences affectées
echo ""
echo "📊 5. Relancer E5..."
./scripts/run_e5.sh 2>&1 | tail -20

echo ""
echo "📊 6. Relancer E6..."
./scripts/run_e6.sh 2>&1 | tail -20

echo ""
echo "=========================================="
echo "✅ TOUTES LES CORRECTIONS APPLIQUÉES"
echo "=========================================="
echo ""
echo "📄 Documents générés :"
echo "   - CALIBRATED_CLAIMS.md"
echo "   - CORRECTIONS/5_limitations_section.md"
echo "   - evidence_registry/memory_reports_measured.json"
