"""
Adaptation Methods - 6 méthodes d'adaptation
Exigence : "MAML = UN OUTIL parmi : recalibration, MAML, fine-tuning, 
changement précision, switch sous-réseau, remapping, rerun AutoCoDesign"
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class AdaptationMethodType(Enum):
    NONE = "none"
    RECALIBRATE = "recalibrate"
    MAML = "maml"
    FINE_TUNE = "fine_tune"
    PRECISION_CHANGE = "precision_change"
    SWITCH_SUBNETWORK = "switch_subnetwork"
    REMAP = "remap"
    REDESIGN = "redesign"


@dataclass
class AdaptationMethod:
    """Description d'une méthode d'adaptation"""
    method_type: AdaptationMethodType
    name: str
    description: str
    
    # Coûts
    compute_cost: float       # Coût relatif (0-10)
    time_s: float             # Temps en secondes
    memory_overhead: float    # Overhead mémoire en % (0-1)
    
    # Capacité de restauration
    restoration_capability: float  # 0-1 (combien de la performance peut être restaurée)
    
    # Contraintes
    requires_labels: bool
    requires_retraining: bool
    min_severity: float  # Sévérité minimale requise
    max_severity: float  # Sévérité maximale supportée
    
    # Applicabilité
    applicable_domains: List[str] = field(default_factory=list)


# ============================================================
# 6 MÉTHODES D'ADAPTATION
# ============================================================

ADAPTATION_METHODS = {
    AdaptationMethodType.NONE: AdaptationMethod(
        method_type=AdaptationMethodType.NONE,
        name="None",
        description="Aucune adaptation - nominal",
        compute_cost=0.0,
        time_s=0.0,
        memory_overhead=0.0,
        restoration_capability=0.0,
        requires_labels=False,
        requires_retraining=False,
        min_severity=0.0,
        max_severity=0.05,
        applicable_domains=["medical", "industrial"]
    ),
    
    AdaptationMethodType.RECALIBRATE: AdaptationMethod(
        method_type=AdaptationMethodType.RECALIBRATE,
        name="Recalibrate",
        description="Recalibration des paramètres (biais, seuils)",
        compute_cost=0.5,
        time_s=1.0,
        memory_overhead=0.0,
        restoration_capability=0.30,  # 30%
        requires_labels=False,
        requires_retraining=False,
        min_severity=0.05,
        max_severity=0.20,
        applicable_domains=["medical", "industrial"]
    ),
    
    AdaptationMethodType.MAML: AdaptationMethod(
        method_type=AdaptationMethodType.MAML,
        name="MAML",
        description="Model-Agnostic Meta-Learning (5-shot adaptation)",
        compute_cost=2.0,
        time_s=10.0,
        memory_overhead=0.30,  # +30% mémoire (support set + gradients)
        restoration_capability=0.75,  # 75%
        requires_labels=True,
        requires_retraining=False,
        min_severity=0.15,
        max_severity=0.40,
        applicable_domains=["medical", "industrial"]
    ),
    
    AdaptationMethodType.FINE_TUNE: AdaptationMethod(
        method_type=AdaptationMethodType.FINE_TUNE,
        name="Fine-Tune",
        description="Fine-tuning complet sur nouvelles données",
        compute_cost=5.0,
        time_s=60.0,
        memory_overhead=0.50,
        restoration_capability=0.85,  # 85%
        requires_labels=True,
        requires_retraining=True,
        min_severity=0.20,
        max_severity=0.50,
        applicable_domains=["medical", "industrial"]
    ),
    
    AdaptationMethodType.PRECISION_CHANGE: AdaptationMethod(
        method_type=AdaptationMethodType.PRECISION_CHANGE,
        name="Precision Change",
        description="Changement de précision (8→4 bits ou 4→8 bits)",
        compute_cost=0.2,
        time_s=0.5,
        memory_overhead=-0.40,  # -40% (moins de mémoire)
        restoration_capability=0.20,
        requires_labels=False,
        requires_retraining=False,
        min_severity=0.10,
        max_severity=0.35,
        applicable_domains=["medical", "industrial"]
    ),
    
    AdaptationMethodType.SWITCH_SUBNETWORK: AdaptationMethod(
        method_type=AdaptationMethodType.SWITCH_SUBNETWORK,
        name="Switch Subnetwork",
        description="Switch vers un sous-réseau spécialisé",
        compute_cost=1.0,
        time_s=2.0,
        memory_overhead=0.20,
        restoration_capability=0.60,
        requires_labels=False,
        requires_retraining=False,
        min_severity=0.25,
        max_severity=0.49,  # ← Réduit pour exclure D3
        applicable_domains=["medical", "industrial"]
    ),
    
    AdaptationMethodType.REMAP: AdaptationMethod(
        method_type=AdaptationMethodType.REMAP,
        name="Remap",
        description="Remapping complet de l'architecture",
        compute_cost=8.0,
        time_s=300.0,
        memory_overhead=0.60,
        restoration_capability=0.90,
        requires_labels=True,
        requires_retraining=True,
        min_severity=0.40,
        max_severity=0.80,
        applicable_domains=["medical", "industrial"]
    ),
    
    AdaptationMethodType.REDESIGN: AdaptationMethod(
        method_type=AdaptationMethodType.REDESIGN,
        name="Redesign",
        description="Nouvelle conception via AutoCoDesign",
        compute_cost=10.0,
        time_s=3000.0,
        memory_overhead=0.0,
        restoration_capability=0.98,
        requires_labels=True,
        requires_retraining=True,
        min_severity=0.60,
        max_severity=1.0,
        applicable_domains=["medical", "industrial"]
    ),
}


class AdaptationMethodRegistry:
    def __init__(self):
        self.methods = ADAPTATION_METHODS
    
    def get_all(self) -> List[AdaptationMethod]:
        return list(self.methods.values())
    
    def get_applicable(self, severity: float, domain: str) -> List[AdaptationMethod]:
        """Méthodes applicables selon sévérité et domaine"""
        return [
            m for m in self.methods.values()
            if m.min_severity <= severity <= m.max_severity
            and domain in m.applicable_domains
        ]
    
    def get_by_type(self, method_type: AdaptationMethodType) -> AdaptationMethod:
        return self.methods.get(method_type)
    
    def summary(self) -> Dict:
        return {
            mt.value: {
                "name": m.name,
                "restoration": m.restoration_capability,
                "cost": m.compute_cost,
                "time_s": m.time_s,
                "memory_overhead": m.memory_overhead,
                "severity_range": (m.min_severity, m.max_severity)
            }
            for mt, m in self.methods.items()
        }


if __name__ == "__main__":
    import json
    registry = AdaptationMethodRegistry()
    print(f"✅ {len(registry.get_all())} méthodes d'adaptation")
    print(json.dumps(registry.summary(), indent=2))
