#!/bin/bash
# Applique toutes les corrections P1

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🔧 CORRECTIONS P1-1, P1-2, P1-3"
echo "=========================================="
echo ""

# P1-1 : Provenance
echo "📊 P1-1 : Registre de provenance..."
python CORRECTIONS/12_add_provenance.py
echo ""

# P1-2 : Code generation
echo "📊 P1-2 : Code generation..."
cd artifacts/generated_code
gcc -O2 -Wall -o test_inference main_inference.c 2>&1 | tee compile.log
if [ -f test_inference ]; then
    echo ""
    echo "=== Exécution ==="
    ./test_inference
fi
cd ../..
echo ""

# P1-3 : Synchronisation claims
echo "📊 P1-3 : Synchronisation claims..."
if [ -f article.tex ]; then
    python CORRECTIONS/13_sync_claims.py
else
    echo "⚠️ article.tex non trouvé - à créer"
fi
echo ""

echo "=========================================="
echo "✅ CORRECTIONS P1 APPLIQUÉES"
echo "=========================================="
echo ""
echo "📄 Artefacts générés :"
echo "   - artifacts/provenance/provenance_registry.json"
echo "   - artifacts/provenance/PROVENANCE_REPORT.md"
echo "   - artifacts/generated_code/test_inference"
echo "   - artifacts/generated_code/compile.log"
echo ""
