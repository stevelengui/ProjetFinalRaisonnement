"""
EVI Calculator - Expected Value of Information
Exigence : "EVI unifié : EVI(a) = E[Q_decision^after - Q_decision^before] - λ_C·C(a) - λ_T·T(a)"
"""

from dataclasses import dataclass
from typing import Dict, List, Callable
import numpy as np


@dataclass
class EVIResult:
    """Résultat d'un calcul EVI"""
    action: str
    expected_quality_gain: float
    cost: float
    time_cost: float
    net_evi: float
    recommended: bool = False


class EVICalculator:
    """
    Calculateur d'EVI
    Détermine quelle action apporte le plus de valeur d'information
    """
    
    def __init__(self, lambda_cost: float = 1.0, lambda_time: float = 0.5):
        self.lambda_cost = lambda_cost
        self.lambda_time = lambda_time
    
    def compute_evi(self, action: str, 
                   quality_gain: float,
                   cost: float,
                   time: float) -> EVIResult:
        """
        Calcule l'EVI d'une action
        EVI(a) = quality_gain - λ_C × cost - λ_T × time
        """
        net = quality_gain - self.lambda_cost * cost - self.lambda_time * time
        
        return EVIResult(
            action=action,
            expected_quality_gain=quality_gain,
            cost=cost,
            time_cost=time,
            net_evi=net
        )
    
    def rank_actions(self, actions: List[Dict]) -> List[EVIResult]:
        """
        Classe plusieurs actions par EVI décroissant
        """
        results = []
        for a in actions:
            result = self.compute_evi(
                action=a['name'],
                quality_gain=a['quality_gain'],
                cost=a['cost'],
                time=a['time']
            )
            results.append(result)
        
        # Tri décroissant
        results.sort(key=lambda r: r.net_evi, reverse=True)
        
        # Marquer la meilleure
        if results:
            results[0].recommended = True
        
        return results
    
    def should_use_high_fidelity(self, current_uncertainty: float,
                                  constraint_margin: float,
                                  cost_hf: float = 10.0) -> bool:
        """
        Décide si une évaluation haute fidélité vaut le coût
        
        Args:
            current_uncertainty: Incertitude actuelle (0-1)
            constraint_margin: Marge par rapport au seuil (0-1, 0=limite)
            cost_hf: Coût relatif de l'évaluation HF
        """
        # Gain de qualité attendu
        # Si incertitude élevée → gain élevé
        # Si marge faible → gain élevé
        quality_gain = current_uncertainty * (1 - constraint_margin) * 2.0
        
        # Coût
        cost = cost_hf / 100.0  # Normalisé
        time = 1.0
        
        evi = self.compute_evi("high_fidelity", quality_gain, cost, time)
        
        return evi.net_evi > 0


if __name__ == "__main__":
    calc = EVICalculator()
    
    actions = [
        {"name": "low_fidelity", "quality_gain": 0.3, "cost": 0.01, "time": 0.1},
        {"name": "high_fidelity", "quality_gain": 0.8, "cost": 1.0, "time": 10.0},
        {"name": "fault_injection", "quality_gain": 0.6, "cost": 2.0, "time": 20.0},
    ]
    
    results = calc.rank_actions(actions)
    
    print("=== Classement EVI ===")
    for r in results:
        marker = "⭐" if r.recommended else "  "
        print(f"{marker} {r.action}: EVI={r.net_evi:.3f}")
