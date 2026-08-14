#!/bin/bash
echo "🚀 Déploiement de ProjetFinalRaisonnement"

# Création de l'environnement virtuel
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p generated_projects

echo "✅ Déploiement terminé !"
echo "   - Backend: http://localhost:5000"
