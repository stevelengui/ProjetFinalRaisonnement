"""
Fidelity Hierarchy - Hiérarchie de fidélité F0-F3
Exigence : "F0 (analytique) < F1 (surrogate+incertitude) < F2 (simulation haute fidélité) < F3 (référence)"
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Fidelity(Enum):
    """Niveaux de fidélité"""
    F0_ANALYTICAL = 0    # Analytique (formule simple)
    F1_SURROGATE = 1     # Surrogate model + incertitude
    F2_SIMULATION = 2    # Simulation haute fidélité (cycle-accurate)
    F3_REFERENCE = 3     # Référence (mesure physique / ground truth)


@dataclass
class FidelityLevel:
    """Description d'un niveau de fidélité"""
    fidelity: Fidelity
    name: str
    cost: float              # Coût relatif
    time_s: float            # Temps en secondes
    uncertainty_range: tuple # (min, max) incertitude
    accuracy_range: tuple    # (min, max) précision
    description: str


FIDELITY_LEVELS = {
    Fidelity.F0_ANALYTICAL: FidelityLevel(
        fidelity=Fidelity.F0_ANALYTICAL,
        name="Analytical",
        cost=0.001,
        time_s=0.001,
        uncertainty_range=(0.20, 0.40),
        accuracy_range=(0.70, 0.85),
        description="Formule analytique simple (rapide, imprécis)"
    ),
    Fidelity.F1_SURROGATE: FidelityLevel(
        fidelity=Fidelity.F1_SURROGATE,
        name="Surrogate",
        cost=0.01,
        time_s=0.01,
        uncertainty_range=(0.05, 0.15),
        accuracy_range=(0.88, 0.95),
        description="Surrogate model entraîné (rapide, précis)"
    ),
    Fidelity.F2_SIMULATION: FidelityLevel(
        fidelity=Fidelity.F2_SIMULATION,
        name="Simulation",
        cost=1.0,
        time_s=10.0,
        uncertainty_range=(0.01, 0.05),
        accuracy_range=(0.95, 0.98),
        description="Simulation cycle-accurate (lent, très précis)"
    ),
    Fidelity.F3_REFERENCE: FidelityLevel(
        fidelity=Fidelity.F3_REFERENCE,
        name="Reference",
        cost=10.0,
        time_s=3600.0,
        uncertainty_range=(0.0, 0.01),
        accuracy_range=(1.0, 1.0),
        description="Mesure physique / ground truth (très lent, exact)"
    ),
}


class FidelityHierarchy:
    """
    Gestion de la hiérarchie de fidélité
    """
    
    def __init__(self):
        self.levels = FIDELITY_LEVELS
    
    def get_level(self, fidelity: Fidelity) -> FidelityLevel:
        return self.levels[fidelity]
    
    def get_cost(self, fidelity: Fidelity) -> float:
        return self.levels[fidelity].cost
    
    def get_time(self, fidelity: Fidelity) -> float:
        return self.levels[fidelity].time_s
    
    def get_uncertainty(self, fidelity: Fidelity) -> float:
        """Retourne l'incertitude moyenne"""
        r = self.levels[fidelity].uncertainty_range
        return (r[0] + r[1]) / 2
    
    def get_accuracy(self, fidelity: Fidelity) -> float:
        """Retourne la précision moyenne"""
        r = self.levels[fidelity].accuracy_range
        return (r[0] + r[1]) / 2
    
    def can_escalate(self, current: Fidelity) -> bool:
        """Peut-on escalader à une fidélité supérieure ?"""
        return current != Fidelity.F3_REFERENCE
    
    def next_fidelity(self, current: Fidelity) -> Fidelity:
        """Retourne la fidélité suivante"""
        levels = list(Fidelity)
        idx = levels.index(current)
        if idx < len(levels) - 1:
            return levels[idx + 1]
        return current
    
    def summary(self) -> dict:
        """Résumé de la hiérarchie"""
        return {
            f.name: {
                "cost": f.cost,
                "time_s": f.time_s,
                "uncertainty": f.uncertainty_range,
                "accuracy": f.accuracy_range,
                "description": f.description
            }
            for f in self.levels.values()
        }


if __name__ == "__main__":
    h = FidelityHierarchy()
    import json
    print(json.dumps(h.summary(), indent=2))
