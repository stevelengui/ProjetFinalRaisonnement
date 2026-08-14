# 🚀 ProjetFinalRaisonnement - LLM-NAS AutoCoDesign

## IEEE TETC 2026 - Algorithm-Architecture Co-Design Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)

---

## 📋 Description

**ProjetFinalRaisonnement** est un framework complet de **coconception algorithm-architecture** pour l'IA embarquée.

### Fonctionnalités principales

- **Exploration du design space** (21,600 combinaisons) via NSGA-II et MOEA/D
- **Modèle hybride QNN-SNN** avec 373,128 paramètres réels (entraînés sur ECG)
- **Explicabilité by-design** (attention sparse K=8, cartes de saillance)
- **Méta-apprentissage MAML** pour la robustesse inter-domaines (5-shot, 99% de rétention)
- **Extensions RV32X-SQ** personnalisées (MAC4, LIF, FUSION)
- **Gestion thermique** avec contraintes ΔT médical (≤5°C) et industriel (≤7°C)

---

## 🏆 Contributions Principales

| Contribution | Description | Statut |
|--------------|-------------|--------|
| HW-SW Codesign | 21,600 designs explorés en <50s | ✅ |
| Modèle Explicable | Attention sparse + saliency | ✅ |
| Méta-Apprentissage | MAML, 5-shot, 99% rétention | ✅ |
| RV32X-SQ | 3 instructions personnalisées | ✅ |
| Gestion Thermique | ΔT médical 5°C / industriel 7°C | ✅ |

---

## 📊 Métriques de Performance

| Domaine | Précision | Latence (ms) | Énergie (mJ) | Mémoire (KB) |
|---------|-----------|--------------|--------------|--------------|
| Médical | 96.1% | 8.2 | 2.8 | 24 |
| Industriel | 95.8% | 6.8 | 2.2 | 22 |
| IoT | 93.4% | 15.2 | 1.9 | 16 |
| Automobile | 90.2% | 18.6 | 4.2 | 32 |
| Robotique | 89.0% | 22.4 | 5.1 | 32 |

---

## 🚀 Installation Rapide

### Prérequis
- Python 3.9+
- 4GB RAM minimum

### Installation

```bash
# 1. Cloner le projet
git clone https://github.com/stevelengui/ProjetFinalRaisonnement.git
cd ProjetFinalRaisonnement

# 2. Lancer le déploiement
chmod +x deploy.sh
./deploy.sh

# 3. Accéder à l'interface
# Frontend: http://localhost:8080
# Backend API: http://localhost:5000

