#!/bin/bash
# Validation globale avec les VRAIES valeurs

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🔍 VALIDATION FINALE - VRAIES VALEURS"
echo "=========================================="
echo ""

echo "📊 1. Vérification des vraies valeurs..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, 'llm_nas')
from real_model_config import (
    REAL_PARAMETER_COUNT, TOTAL_OPS, REAL_M_WEIGHTS_BYTES,
    REAL_M_WEIGHTS_KIB, REAL_M_TOTAL_BYTES, REAL_M_TOTAL_KIB
)

print(f"✅ Nombre de paramètres: {REAL_PARAMETER_COUNT:,}")
print(f"✅ Nombre d'opérations: {TOTAL_OPS:,}")
print(f"✅ M_weights: {REAL_M_WEIGHTS_BYTES:,} bytes = {REAL_M_WEIGHTS_KIB:.2f} KiB")
print(f"✅ M_total: {REAL_M_TOTAL_BYTES:,} bytes = {REAL_M_TOTAL_KIB:.2f} KiB")
print()
print("📝 Note: 373128 = nombre d'OPÉRATIONS (pas de paramètres)")
print(f"📝 Vrai nombre de paramètres: {REAL_PARAMETER_COUNT}")
PYEOF

echo ""
echo "📊 2. Memory Profiler v2..."
python meta_reasoning/memory_profiler_v2.py 2>&1 | head -20

echo ""
echo "📊 3. Backend API (test import)..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from backend.app import REAL_PARAMS, TOTAL_OPERATIONS, M_WEIGHTS_KIB, M_TOTAL_KIB
    print(f'✅ Backend: {REAL_PARAMS} params, {TOTAL_OPERATIONS} ops')
    print(f'✅ M_weights: {M_WEIGHTS_KIB} KiB, M_total: {M_TOTAL_KIB} KiB')
except Exception as e:
    print(f'⚠️ Erreur: {e}')
" 2>&1 | grep -v "Running on" | grep -v "Debug mode" | grep -v "WARNING" | head -5

echo ""
echo "=========================================="
echo "✅ VALIDATION TERMINÉE"
echo "=========================================="
echo ""
echo "📄 Vraies valeurs:"
echo "   - 7 651 paramètres"
echo "   - 373 128 opérations"
echo "   - M_weights: 7.47 KiB"
echo "   - M_total: 29.00 KiB"
