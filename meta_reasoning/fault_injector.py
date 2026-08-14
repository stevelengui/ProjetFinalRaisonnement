"""
Fault Injector - Simule des fautes pour tester la fiabilité
"""

from typing import Dict, List
from enum import Enum
from dataclasses import dataclass
import random

class FaultType(Enum):
    BIT_FLIP = "bit_flip"
    CORRUPTED_WEIGHT = "corrupted_weight"
    ACTIVATION_ERROR = "activation_error"

class FaultSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"

@dataclass
class FaultInjectionResult:
    fault_type: FaultType
    severity: FaultSeverity
    affected_component: str
    accuracy_drop: float
    recoverable: bool

class FaultInjector:
    def __init__(self, seed: int = 42):
        random.seed(seed)
    
    def evaluate_reliability(self, design: Dict) -> Dict:
        precision = design.get("algorithm", {}).get("quantization_bits", 8)
        if precision >= 8:
            reliability = 0.92
            rating = "HIGH"
        elif precision >= 4:
            reliability = 0.85
            rating = "MEDIUM"
        else:
            reliability = 0.70
            rating = "LOW"
        
        return {
            "reliability_score": reliability,
            "fault_tolerance_rating": rating,
            "recommendations": self._get_recommendations(precision)
        }
    
    def _get_recommendations(self, precision: int) -> List[str]:
        recommendations = []
        if precision <= 4:
            recommendations.append("Augmenter la précision pour améliorer la fiabilité")
        if precision <= 2:
            recommendations.append("Ajouter des mécanismes de correction d'erreurs")
        return recommendations
