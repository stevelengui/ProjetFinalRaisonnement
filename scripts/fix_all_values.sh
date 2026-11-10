#!/bin/bash
# Corrige les valeurs dans les fichiers clés

cd ~/ProjetFinalRaisonnement

echo "🔧 Correction des valeurs dans les fichiers clés..."
echo ""

# Backup
BACKUP_DIR=".backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Fichiers à corriger
FILES=(
    "backend/app.py"
    "llm_nas/real_designs.py"
    "frontend/app.js"
)

for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
        cp "$f" "$BACKUP_DIR/$(basename $f)"
        
        # Corrections
        sed -i 's/373128 params/7651 params/g' "$f" 2>/dev/null
        sed -i 's/373,128 paramètres/7,651 paramètres/g' "$f" 2>/dev/null
        sed -i 's/8,53 KB/7,47 KiB/g' "$f" 2>/dev/null
        
        echo "✅ $f corrigé (backup dans $BACKUP_DIR)"
    else
        echo "⚠️ $f non trouvé"
    fi
done

echo ""
echo "✅ Correction terminée"
echo "📁 Backups dans: $BACKUP_DIR"
