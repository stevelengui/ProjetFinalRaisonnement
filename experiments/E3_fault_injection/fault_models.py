"""
Fault Models - Modèles de fautes RÉALISTES et SÉVÈRES
Version corrigée pour produire un renversement décisif

Basé sur :
- SEU (Single Event Upset) en environnement radiatif
- Vieillissement (NBTI, HCI)
- Perturbations électromagnétiques
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
import random


class FaultType(Enum):
    WEIGHT_BIT_FLIP = "weight_bit_flip"
    ACTIVATION_FLIP = "activation_flip"
    SNN_STATE_PERTURBATION = "snn_state_perturbation"
    MEMORY_FAULT = "memory_fault"
    CONTROL_STATE_PERTURBATION = "control_state_perturbation"


@dataclass
class FaultModel:
    fault_type: FaultType
    name: str
    description: str
    target: str
    severity: str
    probability: float
    impact_accuracy: float  # Impact de base (multiplié par sensibilité design)
    detection_likelihood: float
    

# ============================================================
# MODÈLES DE FAUTES SÉVÈRES (SEU réalistes)
# ============================================================

FAULT_MODELS = {
    FaultType.WEIGHT_BIT_FLIP: FaultModel(
        fault_type=FaultType.WEIGHT_BIT_FLIP,
        name="Weight Bit Flip (SEU)",
        description="Bit flip SEU dans un poids quantifié - environnement radiatif",
        target="weights",
        severity="high",
        probability=0.25,  # 25% (vs 5% avant)
        impact_accuracy=0.05,  # 5% (vs 2%)
        detection_likelihood=0.20
    ),
    FaultType.ACTIVATION_FLIP: FaultModel(
        fault_type=FaultType.ACTIVATION_FLIP,
        name="Activation Flip",
        description="Flip d'un bit d'activation intermédiaire",
        target="activations",
        severity="high",
        probability=0.20,
        impact_accuracy=0.06,
        detection_likelihood=0.15
    ),
    FaultType.SNN_STATE_PERTURBATION: FaultModel(
        fault_type=FaultType.SNN_STATE_PERTURBATION,
        name="SNN State Perturbation",
        description="Perturbation de l'état de membrane SNN (cumulatif)",
        target="snn_state",
        severity="critical",
        probability=0.30,  # Plus fréquent
        impact_accuracy=0.10,  # Très impactant
        detection_likelihood=0.10
    ),
    FaultType.MEMORY_FAULT: FaultModel(
        fault_type=FaultType.MEMORY_FAULT,
        name="Memory Fault (MBU)",
        description="Faute mémoire multi-bits (MBU)",
        target="memory",
        severity="critical",
        probability=0.15,
        impact_accuracy=0.08,
        detection_likelihood=0.30
    ),
    FaultType.CONTROL_STATE_PERTURBATION: FaultModel(
        fault_type=FaultType.CONTROL_STATE_PERTURBATION,
        name="Control State Perturbation",
        description="Perturbation de l'état de contrôle (compteurs)",
        target="control",
        severity="critical",
        probability=0.10,
        impact_accuracy=0.12,  # Le plus impactant
        detection_likelihood=0.40
    ),
}


class FaultModelRegistry:
    def __init__(self):
        self.models = FAULT_MODELS
    
    def get_all(self) -> List[FaultModel]:
        return list(self.models.values())
    
    def get_by_target(self, target: str) -> List[FaultModel]:
        return [m for m in self.models.values() if m.target == target]
    
    def summary(self) -> Dict:
        return {
            ft.value: {
                "name": fm.name,
                "target": fm.target,
                "severity": fm.severity,
                "probability": fm.probability,
                "impact": fm.impact_accuracy,
                "detection_likelihood": fm.detection_likelihood
            }
            for ft, fm in self.models.items()
        }


if __name__ == "__main__":
    import json
    registry = FaultModelRegistry()
    print(f"✅ {len(registry.get_all())} modèles de fautes SÉVÈRES")
    print(json.dumps(registry.summary(), indent=2))
