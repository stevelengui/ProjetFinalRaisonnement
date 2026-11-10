import json
"""
import json
Tri-State Logic - PASS/FAIL/UNKNOWN
Exigence : "UNKNOWN n'est jamais PASS"
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


class TriState(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass
class ConstraintCheck:
    """Résultat d'une vérification de contrainte"""
    constraint_name: str
    state: TriState
    value: Optional[float]
    threshold: float
    reason: str
    confidence: float = 1.0


class TriStateEvaluator:
    """
    Évaluateur tri-état
    RÈGLE D'OR : UNKNOWN n'est jamais traité comme PASS
    """
    
    def __init__(self):
        self.checks: List[ConstraintCheck] = []
    
    def check_constraint(self, name: str, value: Optional[float], 
                        threshold: float, 
                        direction: str = "max",
                        confidence: float = 1.0,
                        uncertainty: float = 0.0) -> ConstraintCheck:
        """
        Vérifie une contrainte avec gestion tri-état
        
        Args:
            name: Nom de la contrainte
            value: Valeur mesurée (None si non disponible)
            threshold: Seuil
            direction: "max" (value <= threshold) ou "min" (value >= threshold)
            confidence: Confiance dans la mesure
            uncertainty: Incertitude de la mesure
        """
        
        # CAS 1 : Valeur manquante → UNKNOWN
        if value is None:
            return ConstraintCheck(
                constraint_name=name,
                state=TriState.UNKNOWN,
                value=None,
                threshold=threshold,
                reason="Valeur non disponible",
                confidence=0.0
            )
        
        # CAS 2 : Incertitude élevée → UNKNOWN
        if uncertainty > 0 and (uncertainty / max(abs(value), 1e-6)) > 0.5:
            return ConstraintCheck(
                constraint_name=name,
                state=TriState.UNKNOWN,
                value=value,
                threshold=threshold,
                reason=f"Incertitude trop élevée: ±{uncertainty}",
                confidence=confidence
            )
        
        # CAS 3 : Vérification normale
        if direction == "max":
            # PASS si value <= threshold
            if value > threshold:
                state = TriState.FAIL
                reason = f"{value:.2f} > {threshold:.2f}"
            else:
                state = TriState.PASS
                reason = f"{value:.2f} ≤ {threshold:.2f}"
        else:  # min
            if value < threshold:
                state = TriState.FAIL
                reason = f"{value:.2f} < {threshold:.2f}"
            else:
                state = TriState.PASS
                reason = f"{value:.2f} ≥ {threshold:.2f}"
        
        return ConstraintCheck(
            constraint_name=name,
            state=state,
            value=value,
            threshold=threshold,
            reason=reason,
            confidence=confidence
        )
    
    def aggregate_feasibility(self, checks: List[ConstraintCheck]) -> Dict:
        """
        Agrège les contraintes en un verdict global
        RÈGLES :
        - Si au moins un FAIL → FAIL
        - Si au moins un UNKNOWN (et pas de FAIL) → UNKNOWN
        - Si tous PASS → PASS
        """
        self.checks = checks
        
        states = [c.state for c in checks]
        n_fail = sum(1 for s in states if s == TriState.FAIL)
        n_unknown = sum(1 for s in states if s == TriState.UNKNOWN)
        n_pass = sum(1 for s in states if s == TriState.PASS)
        
        if n_fail > 0:
            overall = TriState.FAIL
        elif n_unknown > 0:
            overall = TriState.UNKNOWN  # ⚠️ JAMAIS traité comme PASS
        else:
            overall = TriState.PASS
        
        return {
            "overall": overall.value,
            "is_feasible": overall == TriState.PASS,
            "counts": {
                "PASS": n_pass,
                "FAIL": n_fail,
                "UNKNOWN": n_unknown
            },
            "checks": [
                {
                    "name": c.constraint_name,
                    "state": c.state.value,
                    "value": c.value,
                    "threshold": c.threshold,
                    "reason": c.reason
                }
                for c in checks
            ]
        }
    
    def should_escalate(self, checks: List[ConstraintCheck]) -> bool:
        """
        Détermine si une escalade vers évaluation haute fidélité est nécessaire
        OUI si : contrainte limite (proche du seuil) OU UNKNOWN
        """
        for c in checks:
            # UNKNOWN → escalade
            if c.state == TriState.UNKNOWN:
                return True
            
            # Proche du seuil (±10%)
            if c.value is not None and c.threshold != 0:
                ratio = abs(c.value - c.threshold) / abs(c.threshold)
                if ratio < 0.1:
                    return True
        
        return False


if __name__ == "__main__":
    evaluator = TriStateEvaluator()
    
    # Test 1 : Contraintes normales
    checks = [
        evaluator.check_constraint("latency", 8.2, 20.0, "max"),
        evaluator.check_constraint("memory", 364.4, 512.0, "max"),
        evaluator.check_constraint("accuracy", 0.961, 0.95, "min"),
    ]
    
    result = evaluator.aggregate_feasibility(checks)
    print(json.dumps(result, indent=2))
    
    # Test 2 : Contrainte UNKNOWN (valeur manquante)
    checks2 = [
        evaluator.check_constraint("latency", 8.2, 20.0, "max"),
        evaluator.check_constraint("energy", None, 10.0, "max"),  # UNKNOWN
    ]
    
    result2 = evaluator.aggregate_feasibility(checks2)
    print(f"\nTest UNKNOWN: {result2['overall']} (doit être UNKNOWN, pas PASS)")
    print(f"Escalade nécessaire: {evaluator.should_escalate(checks2)}")
