"""
Threat Models - Modèle de menace T_sec = {A, K, C, G, B}
Exigence : "Modèle de menace : T_sec = {A, K, C, G, B}"
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class AssetType(Enum):
    """A = Asset (ce qu'on protège)"""
    MODEL_WEIGHTS = "model_weights"
    TRAINING_DATA = "training_data"
    INFERENCE_INPUT = "inference_input"
    INFERENCE_OUTPUT = "inference_output"
    PATIENT_DATA = "patient_data"
    CONTROL_FLOW = "control_flow"


class AttackKnowledge(Enum):
    """K = Knowledge (ce que l'attaquant sait)"""
    BLACK_BOX = "black_box"      # Seulement entrées/sorties
    GREY_BOX = "grey_box"        # Architecture connue
    WHITE_BOX = "white_box"      # Poids et architecture connus


class AttackCapability(Enum):
    """C = Capability (ce que l'attaquant peut faire)"""
    QUERY_ONLY = "query_only"           # Requêtes normales
    INPUT_PERTURBATION = "input_perturbation"  # Perturber les entrées
    SIDE_CHANNEL = "side_channel"      # Mesures physiques
    FAULT_INJECTION = "fault_injection"  # Injection de fautes intentionnelles
    MODEL_EXTRACTION = "model_extraction"  # Voler le modèle


class AttackGoal(Enum):
    """G = Goal (objectif de l'attaquant)"""
    MISCLASSIFICATION = "misclassification"    # Faire mal classifier
    TARGETED_ATTACK = "targeted_attack"        # Classe spécifique
    MODEL_EXTRACTION = "model_extraction"      # Voler le modèle
    DATA_POISONING = "data_poisoning"          # Empoisonner
    DENIAL_OF_SERVICE = "dos"                  # Déni de service
    PRIVACY_BREACH = "privacy_breach"          # Fuite de données


class AttackBoundary(Enum):
    """B = Boundaries (limites de l'attaque)"""
    NONE = "none"
    PERTURBATION_BUDGET = "perturbation_budget"  # ε-bounded
    TIME_BUDGET = "time_budget"
    QUERY_BUDGET = "query_budget"


@dataclass
class ThreatModel:
    """Modèle de menace complet"""
    threat_id: str
    name: str
    description: str
    
    # T_sec = {A, K, C, G, B}
    asset: AssetType
    knowledge: AttackKnowledge
    capability: AttackCapability
    goal: AttackGoal
    boundary: AttackBoundary
    
    # Caractéristiques quantitatives
    threat_level: float  # 0-1 (sévérité de la menace)
    perturbation_budget: float  # ε
    query_budget: int
    
    # Contexte
    domain: str  # "medical", "industrial"
    notes: str = ""


# ============================================================
# 5 MODÈLES DE MENACE
# ============================================================

def get_all_threat_models() -> List[ThreatModel]:
    return [
        # Menace 1 : Aucune menace (baseline)
        ThreatModel(
            threat_id="T0",
            name="No Threat",
            description="Aucune menace - environnement de confiance",
            asset=AssetType.MODEL_WEIGHTS,
            knowledge=AttackKnowledge.BLACK_BOX,
            capability=AttackCapability.QUERY_ONLY,
            goal=AttackGoal.MISCLASSIFICATION,
            boundary=AttackBoundary.NONE,
            threat_level=0.0,
            perturbation_budget=0.0,
            query_budget=0,
            domain="medical"
        ),
        
        # Menace 2 : Faible (black-box)
        ThreatModel(
            threat_id="T1",
            name="Low Threat - Black Box",
            description="Attaquant en boîte noire avec budget limité",
            asset=AssetType.INFERENCE_OUTPUT,
            knowledge=AttackKnowledge.BLACK_BOX,
            capability=AttackCapability.QUERY_ONLY,
            goal=AttackGoal.MISCLASSIFICATION,
            boundary=AttackBoundary.QUERY_BUDGET,
            threat_level=0.25,
            perturbation_budget=0.01,
            query_budget=1000,
            domain="medical"
        ),
        
        # Menace 3 : Moyenne (grey-box adversarial)
        ThreatModel(
            threat_id="T2",
            name="Medium Threat - Grey Box Adversarial",
            description="Attaquant en boîte grise avec perturbations",
            asset=AssetType.MODEL_WEIGHTS,
            knowledge=AttackKnowledge.GREY_BOX,
            capability=AttackCapability.INPUT_PERTURBATION,
            goal=AttackGoal.TARGETED_ATTACK,
            boundary=AttackBoundary.PERTURBATION_BUDGET,
            threat_level=0.50,
            perturbation_budget=0.05,  # ε = 5%
            query_budget=10000,
            domain="medical"
        ),
        
        # Menace 4 : Élevée (white-box adversarial)
        ThreatModel(
            threat_id="T3",
            name="High Threat - White Box Adversarial",
            description="Attaquant avec accès complet au modèle",
            asset=AssetType.MODEL_WEIGHTS,
            knowledge=AttackKnowledge.WHITE_BOX,
            capability=AttackCapability.INPUT_PERTURBATION,
            goal=AttackGoal.TARGETED_ATTACK,
            boundary=AttackBoundary.PERTURBATION_BUDGET,
            threat_level=0.75,
            perturbation_budget=0.10,  # ε = 10%
            query_budget=100000,
            domain="medical"
        ),
        
        # Menace 5 : Critique (side-channel + extraction)
        ThreatModel(
            threat_id="T4",
            name="Critical Threat - Model Extraction + Side Channel",
            description="Attaquant sophistiqué avec canaux auxiliaires",
            asset=AssetType.PATIENT_DATA,
            knowledge=AttackKnowledge.WHITE_BOX,
            capability=AttackCapability.SIDE_CHANNEL,
            goal=AttackGoal.PRIVACY_BREACH,
            boundary=AttackBoundary.TIME_BUDGET,
            threat_level=0.95,
            perturbation_budget=0.15,
            query_budget=1000000,
            domain="medical"
        ),
    ]


class ThreatModelRegistry:
    def __init__(self):
        self.models = {t.threat_id: t for t in get_all_threat_models()}
    
    def get_by_id(self, threat_id: str) -> ThreatModel:
        return self.models.get(threat_id)
    
    def get_by_level(self, min_level: float, max_level: float) -> List[ThreatModel]:
        return [t for t in self.models.values() 
                if min_level <= t.threat_level <= max_level]
    
    def summary(self) -> Dict:
        return {
            t.threat_id: {
                "name": t.name,
                "level": t.threat_level,
                "knowledge": t.knowledge.value,
                "capability": t.capability.value,
                "goal": t.goal.value
            }
            for t in self.models.values()
        }


if __name__ == "__main__":
    import json
    registry = ThreatModelRegistry()
    print(f"✅ {len(registry.models)} modèles de menace")
    print(json.dumps(registry.summary(), indent=2))
