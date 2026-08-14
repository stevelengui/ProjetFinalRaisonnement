#!/bin/bash
# Script de démonstration complet pour ProjetFinalRaisonnement

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🚀 ProjetFinalRaisonnement - Démonstration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. Afficher les designs disponibles
echo -e "${YELLOW}📊 1. Designs disponibles${NC}"
curl -s http://localhost:5000/api/designs/list 2>/dev/null | python3 -m json.tool || echo "  ⚠️ Designs non disponibles"
echo ""

# 2. Exécuter le méta-raisonnement pour le domaine médical
echo -e "${YELLOW}🧠 2. Méta-raisonnement - Domaine Médical${NC}"
curl -s -X POST http://localhost:5000/api/meta/reason \
  -H "Content-Type: application/json" \
  -d '{"domain":"medical","environment":"hospital"}' | python3 -m json.tool | head -40
echo ""

# 3. Exécuter le méta-raisonnement pour le domaine industriel
echo -e "${YELLOW}🧠 3. Méta-raisonnement - Domaine Industriel${NC}"
curl -s -X POST http://localhost:5000/api/meta/reason \
  -H "Content-Type: application/json" \
  -d '{"domain":"industrial","environment":"factory"}' | python3 -m json.tool | head -40
echo ""

# 4. Générer le code pour le design sélectionné
echo -e "${YELLOW}💻 4. Génération de code${NC}"
curl -s -X POST http://localhost:5000/api/generate/strict \
  -H "Content-Type: application/json" \
  -d '{"domain":"medical","mcu":"riscv_rv32x"}' | python3 -m json.tool
echo ""

# 5. Vérifier la conformité
echo -e "${YELLOW}✅ 5. Vérification de conformité${NC}"
curl -s http://localhost:5000/api/compliance/verify | python3 -m json.tool
echo ""

# 6. Rapport de monitoring
echo -e "${YELLOW}📈 6. Rapport de monitoring${NC}"
curl -s http://localhost:5000/api/meta/deployment/report | python3 -m json.tool
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Démonstration terminée !${NC}"
echo -e "${BLUE}========================================${NC}"
