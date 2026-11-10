"""
Intervention Selector - VERSION CORRIGÉE
Utilise la classe de perturbation pour déterminer la sévérité
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from lifecycle_perturbations import (
    InterventionType, LifecyclePerturbation, PerturbationClass
)


@dataclass
class InterventionOption:
    intervention_type: InterventionType
    name: str
    description: str
    restoration_capability: float
    cost: float
    time_hours: float
    residual_risk: float
    min_severity: float
    max_severity: float


# ============================================================
# 5 INTERVENTIONS
# ============================================================

INTERVENTION_OPTIONS = {
    InterventionType.CONTINUE: InterventionOption(
        intervention_type=InterventionType.CONTINUE,
        name="Continue",
        description="Aucune action",
        restoration_capability=0.0,
        cost=0.0,
        time_hours=0.0,
        residual_risk=0.0,
        min_severity=0.0,
        max_severity=0.10
    ),
    InterventionType.CALIBRATE: InterventionOption(
        intervention_type=InterventionType.CALIBRATE,
        name="Calibrate",
        description="Recalibration",
        restoration_capability=0.50,
        cost=0.10,
        time_hours=1.0,
        residual_risk=0.05,
        min_severity=0.10,
        max_severity=0.30
    ),
    InterventionType.ADAPT: InterventionOption(
        intervention_type=InterventionType.ADAPT,
        name="Adapt",
        description="Adaptation",
        restoration_capability=0.75,
        cost=0.30,
        time_hours=10.0,
        residual_risk=0.10,
        min_severity=0.25,
        max_severity=0.55
    ),
    InterventionType.REMAP: InterventionOption(
        intervention_type=InterventionType.REMAP,
        name="Remap",
        description="Remapping",
        restoration_capability=0.90,
        cost=0.60,
        time_hours=48.0,
        residual_risk=0.15,
        min_severity=0.50,
        max_severity=0.80
    ),
    InterventionType.REDESIGN: InterventionOption(
        intervention_type=InterventionType.REDESIGN,
        name="Redesign",
        description="Nouvelle conception",
        restoration_capability=0.98,
        cost=1.0,
        time_hours=720.0,
        residual_risk=0.05,
        min_severity=0.75,
        max_severity=1.0
    ),
}


class InterventionSelector:
    """
    Sélectionne l'intervention optimale
    a* = argmax[Q_restore(a) - λ_C·C(a) - λ_R·R_residual(a)]
    """
    
    def __init__(self, lambda_cost: float = 0.3, lambda_risk: float = 0.5):
        self.lambda_cost = lambda_cost
        self.lambda_risk = lambda_risk
        self.options = INTERVENTION_OPTIONS
    
    def compute_severity_score(self, perturbation: LifecyclePerturbation) -> float:
        """
        Calcule un score de sévérité EN UTILISANT LA CLASSE
        C0 = 0.0, C1 = 0.20, C2 = 0.40, C3 = 0.65, C4 = 0.90
        """
        # Mapping direct classe → sévérité
        class_to_severity = {
            PerturbationClass.C0_NOMINAL: 0.0,
            PerturbationClass.C1_MINOR: 0.20,
            PerturbationClass.C2_MODERATE: 0.40,
            PerturbationClass.C3_MAJOR: 0.65,
            PerturbationClass.C4_STRUCTURAL: 0.90,
        }
        
        base_severity = class_to_severity.get(perturbation.perturbation_class, 0.5)
        
        # Ajuster légèrement selon l'impact réel
        impact = (
            perturbation.accuracy_impact * 0.4 +
            perturbation.latency_impact * 0.2 +
            perturbation.memory_impact * 0.15 +
            perturbation.energy_impact * 0.1 +
            perturbation.reliability_impact * 0.15
        )
        
        # Moyenne pondérée : 70% classe + 30% impact
        severity = 0.7 * base_severity + 0.3 * impact
        
        return severity
    
    def evaluate_intervention(self, intervention_type: InterventionType,
                            severity_score: float) -> Tuple[float, Dict]:
        option = self.options[intervention_type]
        
        # Vérifier l'applicabilité
        applicable = option.min_severity <= severity_score <= option.max_severity
        
        if not applicable:
            return -999, {
                "applicable": False,
                "reason": f"Severity {severity_score:.2f} outside [{option.min_severity}, {option.max_severity}]"
            }
        
        # Q_restore
        q_restore = option.restoration_capability * min(1.0, severity_score * 1.5)
        
        # Score
        score = q_restore - self.lambda_cost * option.cost - self.lambda_risk * option.residual_risk
        
        return score, {
            "applicable": True,
            "intervention": option.name,
            "q_restore": q_restore,
            "cost": option.cost,
            "residual_risk": option.residual_risk,
            "score": score,
            "time_hours": option.time_hours
        }
    
    def select_intervention(self, perturbation: LifecyclePerturbation) -> Dict:
        severity_score = self.compute_severity_score(perturbation)
        
        evaluations = []
        for intervention_type in InterventionType:
            score, details = self.evaluate_intervention(intervention_type, severity_score)
            evaluations.append((intervention_type, score, details))
        
        applicable = [(t, s, d) for t, s, d in evaluations if d.get("applicable", False)]
        
        if not applicable:
            return {
                "perturbation_id": perturbation.perturbation_id,
                "severity_score": severity_score,
                "selected_intervention": "redesign",
                "selected_type": InterventionType.REDESIGN,
                "score": 0,
                "reasoning": "Fallback to redesign",
                "matches_expected": False,
                "expected_intervention": perturbation.expected_intervention,
                "all_evaluations": [
                    {"intervention": t.value, "score": s, "details": d}
                    for t, s, d in evaluations
                ]
            }
        
        applicable.sort(key=lambda x: x[1], reverse=True)
        best_type, best_score, best_details = applicable[0]
        
        expected = perturbation.expected_intervention
        matches_expected = best_type.value == expected
        
        return {
            "perturbation_id": perturbation.perturbation_id,
            "perturbation_class": perturbation.perturbation_class.value,
            "severity_score": severity_score,
            "selected_intervention": best_type.value,
            "selected_type": best_type,
            "score": best_score,
            "details": best_details,
            "matches_expected": matches_expected,
            "expected_intervention": expected,
            "reasoning": f"Selected {best_type.value} (score={best_score:.3f})",
            "all_evaluations": [
                {"intervention": t.value, "score": s, "details": d}
                for t, s, d in evaluations
            ]
        }


if __name__ == "__main__":
    from lifecycle_perturbations import get_all_perturbations
    import json
    
    selector = InterventionSelector()
    perturbations = get_all_perturbations()
    
    print("✅ InterventionSelector CORRIGÉ\n")
    
    for p in perturbations:
        result = selector.select_intervention(p)
        status = "✅" if result["matches_expected"] else "❌"
        print(f"{status} {p.perturbation_id} ({p.perturbation_class.value}): "
              f"severity={result['severity_score']:.3f}, "
              f"selected={result['selected_intervention']}, "
              f"expected={result['expected_intervention']}")
