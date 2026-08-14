# 🚀 ProjetFinalRaisonnement - LLM-NAS AutoCoDesign

## IEEE TETC 2026 - Algorithm-Architecture Co-Design Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Research](https://img.shields.io/badge/IEEE-TETC-red.svg)](https://ieeexplore.ieee.org/)

---

## 📋 Description

**ProjetFinalRaisonnement** est un framework complet de **coconception algorithm-architecture** pour l'IA embarquée. Il intègre les contributions des **Papers 4 et 5** :

### 🔬 2 Contributions Majeures

| Contribution | Description | Statut |
|--------------|-------------|--------|
| **AutoCoDesign (Paper 4)** | Exploration du design space (21,600 combinaisons) via NSGA-II et MOEA/D | ✅ |
| **Méta-Raisonneur (Paper 5)** | Couche de raisonnement qui pilote AutoCoDesign et justifie ses décisions | ✅ |

### 🧠 Fonctionnalités Principales

- **Exploration du design space** (21,600 combinaisons) via NSGA-II et MOEA/D
- **Modèle hybride QNN-SNN** avec 373,128 paramètres réels (entraînés sur ECG)
- **Explicabilité by-design** (attention sparse K=8, cartes de saillance)
- **Méta-apprentissage MAML** pour la robustesse inter-domaines (5-shot, 99% de rétention)
- **Extensions RV32X-SQ** personnalisées (MAC4, LIF, FUSION)
- **Gestion thermique** avec contraintes ΔT médical (≤5°C) et industriel (≤7°C)

---

## 🧠 LE MÉTA-RAISONNEUR (Paper 5)

### Qu'est-ce que le Méta-Raisonneur ?

Le **Méta-Raisonneur** est une couche de raisonnement de haut niveau qui pilote AutoCoDesign (Paper 4). Contrairement aux approches traditionnelles qui optimisent sans expliquer, le méta-raisonneur :

1. **Analyse le contexte applicatif** (domaine médical, industriel, etc.)
2. **Génère un contrat de conception** (objectifs et contraintes)
3. **Explore l'espace de conception** (appelle AutoCoDesign)
4. **Évalue les preuves** (latence, énergie, précision, fiabilité)
5. **Sélectionne le meilleur design** avec justification
6. **Génère un rapport d'assurance** expliquant la décision
7. **Surveille post-déploiement** et s'adapte si nécessaire

### Architecture du Méta-Raisonneur
┌─────────────────────────────────────────────────────────────────────────────┐
│ MÉTA-RAISONNEUR │
├─────────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐ │
│ │ 1. Analyse du │ │ 2. Contrat de │ │ 3. Exploration │ │
│ │ Contexte │───▶│ Conception │───▶│ (AutoCoDesign) │ │
│ │ (context_analyzer)│ │ (design_contract) │ │ (pareto_explorer) │ │
│ └───────────────────┘ └───────────────────┘ └───────────────────┘ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐ │
│ │ 4. Évaluation │ │ 5. Comparaison │ │ 6. Justification │ │
│ │ des Preuves │───▶│ et Classement │───▶│ et Assurance │ │
│ │(evidence_evaluator)│ │ (meta_controller) │ │(assurance_generator)│ │
│ └───────────────────┘ └───────────────────┘ └───────────────────┘ │
│ │
│ ┌───────────────────────────────────────────────────────────────────────┐ │
│ │ 7. Monitoring Post-Déploiement (post_deployment_monitor) │ │
│ │ - Détection des dérives de performance │ │
│ │ - Détection des changements de domaine │ │
│ │ - Déclenchement automatique du méta-raisonnement │ │
│ └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

text

### Exemple de Raisonnement Complet

```json
{
  "status": "success",
  "decision": {
    "design": {
      "id": "ecg_hybrid_4bit",
      "name": "ECG Hybrid 4-bit",
      "algorithm": {
        "model_type": "hybrid",
        "quantization_bits": 4,
        "parameters": 186564
      },
      "hardware": {
        "mcu_type": "riscv_rv32x",
        "clock_mhz": 120,
        "memory_kb": 12
      },
      "metrics": {
        "accuracy": 0.948,
        "latency_ms": 6.2,
        "energy_mj": 1.9,
        "memory_kb": 12.0,
        "explainability_score": 0.89,
        "reliability": 0.88
      },
      "source": "ECG MIT-BIH Database (quantized)",
      "validation_status": "validated"
    },
    "confidence": 0.92,
    "justification": "Design sélectionné: ecg_hybrid_4bit\n  - Nom: ECG Hybrid 4-bit\n  - Source: ECG MIT-BIH Database (quantized)\n  - Validation: validated\n\nMétriques de performance:\n  - Précision: 94.8%\n  - Latence: 6.2ms\n  - Énergie: 1.90mJ\n  - Mémoire: 12.0KB\n\nJustification: Ce design a été validé sur des données réelles\navec une précision de 94.8% sur ECG MIT-BIH Database.\nIl représente le meilleur compromis performance/énergie pour ce domaine."
  },
  "reasoning_traces": [
    {"state": "analyzing_context", "message": "Début du méta-raisonnement"},
    {"state": "analyzing_context", "message": "Domaine: medical"},
    {"state": "exploring_designs", "message": "3 designs réels disponibles"},
    {"state": "making_decision", "message": "Design sélectionné: ecg_hybrid_4bit (score: 0.847)"}
  ]
}
Pourquoi un Méta-Raisonneur ?
Approche Traditionnelle	Méta-Raisonneur
Optimise sans expliquer	Justifie chaque décision
Fixe et rigide	Adaptatif et contextuel
Aucune traçabilité	Trace complète du raisonnement
Pas de suivi post-déploiement	Monitoring et adaptation continue
Décisions opaques	Décisions transparentes et auditées
🏆 Contributions Principales
Contribution	Description	Statut
HW-SW Codesign	21,600 designs explorés en <50s	✅
Modèle Explicable	Attention sparse + saliency	✅
Méta-Apprentissage	MAML, 5-shot, 99% rétention	✅
RV32X-SQ	3 instructions personnalisées	✅
Gestion Thermique	ΔT médical 5°C / industriel 7°C	✅
Méta-Raisonneur	Raisonnement justifié et tracé (Paper 5)	✅
📊 Métriques de Performance (Article Table VI)
Domaine	Design	Précision	Latence (ms)	Énergie (mJ)	Mémoire (KB)
Médical	ecg_hybrid_4bit	94.8%	6.2	1.9	12
Médical	ecg_hybrid_8bit	96.1%	8.2	2.8	24
Industriel	vibration_hybrid_8bit	95.8%	6.8	2.2	32
IoT	vibration_qnn_4bit	93.4%	15.2	1.9	16
IoT	iot_snn_lowpower	89.0%	18.6	0.6	4
Automobile	auto_hybrid_8bit	90.2%	18.6	4.2	48
Robotique	robot_slam_8bit	89.0%	22.4	5.1	64
🚀 Installation Rapide
Prérequis
bash
- Python 3.9+
- 4GB RAM minimum
- 2GB d'espace disque
Installation
bash
# 1. Cloner le projet
git clone https://github.com/stevelengui/ProjetFinalRaisonnement.git
cd ProjetFinalRaisonnement

# 2. Lancer le déploiement
chmod +x deploy.sh
./deploy.sh

# 3. Accéder à l'interface
# Frontend: http://localhost:8080
# Backend API: http://localhost:5000
📁 Structure du Projet
text
ProjetFinalRaisonnement/
├── README.md
├── requirements.txt
├── deploy.sh
├── docker-compose.yml
├── Dockerfile
├── .env
├── .gitignore
│
├── backend/
│   └── app.py                    # API Flask (10 endpoints)
│
├── llm_nas/                      # AutoCoDesign (Paper 4)
│   ├── real_designs.py           # 8 designs réels
│   ├── pareto_explorer.py        # NSGA-II + MOEA/D
│   ├── hybrid_model.py           # Modèle QNN-SNN (373,128 params)
│   ├── explainability.py         # Modules d'explicabilité
│   ├── metalearn.py              # MAML meta-learning
│   ├── rv32x_extensions.py       # RV32X-SQ instructions
│   └── surrogate_models.py       # Modèles prédictifs
│
├── meta_reasoning/               # ⭐ MÉTA-RAISONNEUR (Paper 5)
│   ├── meta_controller.py        # Cœur du méta-raisonneur
│   ├── context_analyzer.py       # Analyse du contexte
│   ├── design_contract.py        # Contrat de conception
│   ├── evidence_evaluator.py     # Évaluation des preuves
│   ├── post_deployment_monitor.py # Monitoring post-déploiement
│   ├── fault_injector.py         # Injection de fautes
│   └── assurance_generator.py    # Génération de justifications
│
├── hardware/
│   ├── rv32x_custom_instructions.sv
│   └── memory_hierarchy_controller.sv
│
├── frontend/
│   ├── index.html
│   └── app.js
│
├── scripts/
│   └── demo.sh
│
└── generated_projects/
    └── .gitkeep
🔌 API Endpoints
Endpoint	Méthode	Description
/api/health	GET	Santé du système
/api/meta/health	GET	Santé du méta-raisonneur
/api/meta/reason	POST	⭐ Méta-raisonnement complet (Paper 5)
/api/meta/trace	GET	Trace du raisonnement
/api/meta/deployment/report	GET	Rapport de monitoring post-déploiement
/api/designs/list	GET	Liste des 8 designs réels
/api/designs/domain/<domain>	GET	Designs par domaine
/api/generate/strict	POST	Génération stricte (AutoCoDesign)
/api/generate/design	POST	Génération par design spécifique
/api/compliance/verify	GET	Vérification des 3 contraintes strictes
/api/download/<id>	GET	Télécharger un projet généré
🧠 Exemples d'Utilisation
1. Exécuter le Méta-Raisonneur (⭐ Paper 5)
bash
# Pour le domaine médical
curl -X POST http://localhost:5000/api/meta/reason \
  -H "Content-Type: application/json" \
  -d '{"domain":"medical","environment":"hospital"}'

# Pour le domaine industriel
curl -X POST http://localhost:5000/api/meta/reason \
  -H "Content-Type: application/json" \
  -d '{"domain":"industrial","environment":"factory"}'
2. Lister les Designs Disponibles
bash
# Tous les designs
curl http://localhost:5000/api/designs/list | python3 -m json.tool

# Designs médicaux uniquement
curl http://localhost:5000/api/designs/domain/medical | python3 -m json.tool
3. Générer un Projet
bash
# Générer à partir d'un design spécifique
curl -X POST http://localhost:5000/api/generate/design \
  -H "Content-Type: application/json" \
  -d '{"design_id":"ecg_hybrid_4bit"}'

# Générer avec contraintes strictes (AutoCoDesign)
curl -X POST http://localhost:5000/api/generate/strict \
  -H "Content-Type: application/json" \
  -d '{"domain":"medical","mcu":"riscv_rv32x"}'
4. Monitoring Post-Déploiement
bash
# Obtenir le rapport de monitoring
curl http://localhost:5000/api/meta/deployment/report | python3 -m json.tool
📈 Résultats de l'Étude d'Ablation
Configuration	Précision	Latence (ms)	Impact
Framework Complet	96.1%	8.2	Référence
Sans LLM	94.0%	8.5	-2.1% précision
Sans XAI	95.8%	8.1	-0.3% précision
Sans MAML	92.0%	8.2	-4.1% précision
NSGA-II seulement	95.5%	9.1	+0.9ms latence
MOEA/D seulement	95.3%	9.3	+1.1ms latence
📋 3 Exigences Strictes (IEEE TETC)
Exigence	Description	Statut
1. HW-SW Codesign	21,600 designs explorés, exploration <50s	✅
2. Modèle Explicable	Sparse attention (K=8) + saliency maps	✅
3. Méta-Apprentissage	MAML, 5-shot, 99% de rétention	✅
bash
# Vérifier la conformité
curl http://localhost:5000/api/compliance/verify | python3 -m json.tool
🐳 Docker
bash
# Construire l'image Docker
docker build -t projetfinalraisonnement .

# Lancer avec Docker Compose
docker-compose up -d

# Arrêter
docker-compose down
📝 Citation
bibtex
@article{lengui2026autocodesign,
  title={LLM-NAS-Driven AutoCoDesign: A Hybrid Self-Adaptive Framework 
         for Algorithm-Architecture Co-Design of Embedded Artificial Intelligence},
  author={Lengui Lengui, S. and Ahmed Ouameur, M. and Lemaire, M. 
          and Bagaa, M. and Massicotte, D.},
  journal={IEEE Transactions on Emerging Topics in Computing},
  year={2026}
}


