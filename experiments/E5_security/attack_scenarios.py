"""
Attack Scenarios - Scénarios d'attaque adversariales
Exigence : "Perturbations intentionnelles/adversariales (distinct de E3)"
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class AttackType(Enum):
    """Types d'attaques adversariales"""
    FGSM = "fgsm"                    # Fast Gradient Sign Method
    PGD = "pgd"                      # Projected Gradient Descent
    C_W = "cw"                       # Carlini & Wagner
    BACKDOOR = "backdoor"            # Attaque par porte dérobée
    MODEL_EXTRACTION = "extraction"  # Vol de modèle
    MEMBERSHIP_INFERENCE = "membership"  # Inférence d'appartenance


@dataclass
class AttackScenario:
    """Un scénario d'attaque"""
    attack_id: str
    attack_type: AttackType
    name: str
    description: str
    
    # Caractéristiques
    target_asset: str
    requires_white_box: bool
    perturbation_budget: float  # ε
    computational_cost: float   # Coût relatif 0-10
    
    # Impact attendu
    expected_asr_range: tuple  # (min, max) Attack Success Rate
    
    # Contexte
    threat_model_id: str
    domain: str
    notes: str = ""


# ============================================================
# 6 SCÉNARIOS D'ATTAQUE
# ============================================================

def get_all_attack_scenarios() -> List[AttackScenario]:
    return [
        AttackScenario(
            attack_id="A1",
            attack_type=AttackType.FGSM,
            name="FGSM - Fast Gradient Sign Method",
            description="Attaque rapide par gradient (1 step)",
            target_asset="inference_input",
            requires_white_box=True,
            perturbation_budget=0.05,
            computational_cost=0.5,
            expected_asr_range=(0.10, 0.30),
            threat_model_id="T2",
            domain="medical",
            notes="Attaque basique, faible budget"
        ),
        
        AttackScenario(
            attack_id="A2",
            attack_type=AttackType.PGD,
            name="PGD - Projected Gradient Descent",
            description="Attaque itérative forte par gradient",
            target_asset="inference_input",
            requires_white_box=True,
            perturbation_budget=0.10,
            computational_cost=3.0,
            expected_asr_range=(0.40, 0.70),
            threat_model_id="T3",
            domain="medical",
            notes="Attaque forte, nécessite white-box"
        ),
        
        AttackScenario(
            attack_id="A3",
            attack_type=AttackType.C_W,
            name="C&W - Carlini & Wagner",
            description="Attaque optimisée avec faible perturbation",
            target_asset="inference_input",
            requires_white_box=True,
            perturbation_budget=0.03,
            computational_cost=5.0,
            expected_asr_range=(0.50, 0.80),
            threat_model_id="T3",
            domain="medical",
            notes="Attaque optimale mais coûteuse"
        ),
        
        AttackScenario(
            attack_id="A4",
            attack_type=AttackType.BACKDOOR,
            name="Backdoor Attack",
            description="Injection de porte dérobée dans le modèle",
            target_asset="model_weights",
            requires_white_box=False,
            perturbation_budget=0.0,
            computational_cost=8.0,
            expected_asr_range=(0.80, 0.98),
            threat_model_id="T4",
            domain="medical",
            notes="Attaque très dangereuse, difficile à détecter"
        ),
        
        AttackScenario(
            attack_id="A5",
            attack_type=AttackType.MODEL_EXTRACTION,
            name="Model Extraction",
            description="Vol du modèle par requêtes massives",
            target_asset="model_weights",
            requires_white_box=False,
            perturbation_budget=0.0,
            computational_cost=6.0,
            expected_asr_range=(0.60, 0.90),
            threat_model_id="T4",
            domain="medical",
            notes="Vole la propriété intellectuelle"
        ),
        
        AttackScenario(
            attack_id="A6",
            attack_type=AttackType.MEMBERSHIP_INFERENCE,
            name="Membership Inference",
            description="Déterminer si un échantillon était dans l'entraînement",
            target_asset="training_data",
            requires_white_box=False,
            perturbation_budget=0.0,
            computational_cost=2.0,
            expected_asr_range=(0.20, 0.40),
            threat_model_id="T3",
            domain="medical",
            notes="Viole la confidentialité des données"
        ),
    ]


class AttackScenarioRegistry:
    def __init__(self):
        self.scenarios = {a.attack_id: a for a in get_all_attack_scenarios()}
    
    def get_by_threat(self, threat_model_id: str) -> List[AttackScenario]:
        return [a for a in self.scenarios.values() 
                if a.threat_model_id == threat_model_id]
    
    def get_by_type(self, attack_type: AttackType) -> List[AttackScenario]:
        return [a for a in self.scenarios.values() 
                if a.attack_type == attack_type]
    
    def summary(self) -> Dict:
        return {
            a.attack_id: {
                "name": a.name,
                "type": a.attack_type.value,
                "budget": a.perturbation_budget,
                "cost": a.computational_cost,
                "expected_asr": a.expected_asr_range
            }
            for a in self.scenarios.values()
        }


if __name__ == "__main__":
    import json
    registry = AttackScenarioRegistry()
    print(f"✅ {len(registry.scenarios)} scénarios d'attaque")
    print(json.dumps(registry.summary(), indent=2))
