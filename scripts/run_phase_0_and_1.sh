#!/bin/bash
# Script de lancement Phase 0 + Phase 1
# Exécute l'intégrité numérique et teste le contrôleur

cd ~/ProjetFinalRaisonnement

echo "=========================================="
echo "🚀 PHASE 0 : INTÉGRITÉ NUMÉRIQUE"
echo "=========================================="

# 1. Memory profiler
echo -e "\n📊 1. Profiling mémoire..."
python meta_reasoning/memory_profiler.py

# 2. Evidence registry
echo -e "\n📋 2. Enregistrement des preuves..."
python meta_reasoning/evidence_registry.py

# 3. QA Gate
echo -e "\n✅ 3. Vérification QA..."
python meta_reasoning/qa_gate.py

echo -e "\n=========================================="
echo "🏗️ PHASE 1 : CONTRÔLEUR MÉTA-OPÉRATIONNEL"
echo "=========================================="

# 4. Test tri-state
echo -e "\n🔍 4. Test tri-état..."
python meta_reasoning/tri_state_logic.py

# 5. Test EVI
echo -e "\n💰 5. Test EVI..."
python meta_reasoning/evi_calculator.py

# 6. Test conflict resolver
echo -e "\n⚖️ 6. Test résolution de conflits..."
python meta_reasoning/conflict_resolver.py

echo -e "\n=========================================="
echo "✅ PHASE 0 + PHASE 1 TERMINÉES"
echo "=========================================="
echo ""
echo "📄 Fichiers générés :"
echo "   - evidence_registry/memory_reports.json"
echo "   - evidence_registry/registry.json"
echo "   - evidence_registry/transitions.jsonl"
