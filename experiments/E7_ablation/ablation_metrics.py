"""
Ablation Metrics - VERSION CORRIGÉE
Score composite mieux calibré
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AblationMetrics:
    ablation_id: str
    ablation_name: str
    dcr: float = 0.0
    cvr: float = 0.0
    regret: float = 0.0
    avg_cost: float = 0.0
    total_cost: float = 0.0
    hf_invocations: int = 0
    hf_rate: float = 0.0
    sufficiency_error: float = 0.0
    restoration_rate: float = 0.0
    auditability_score: float = 0.0
    overall_score: float = 0.0


class AblationMetricsComputer:
    """Calcule les métriques d'ablation avec un score composite amélioré"""
    
    def __init__(self):
        # Poids plus agressifs
        self.weights = {
            "dcr": 0.35,           # Décisions correctes (plus important)
            "cvr": -0.25,          # Violations (à minimiser)
            "regret": -0.15,       # Regret
            "cost": -0.05,         # Coût (moins important)
            "restoration": 0.10,   # Restauration
            "auditability": 0.10   # Auditabilité
        }
    
    def compute_metrics(self, ablation_config, 
                       scenario_results: List[Dict]) -> AblationMetrics:
        if not scenario_results:
            return AblationMetrics(
                ablation_id=ablation_config.ablation_id,
                ablation_name=ablation_config.name
            )
        
        # Métriques de base
        correct_decisions = sum(1 for r in scenario_results if r.get("decision_correct", False))
        dcr = correct_decisions / len(scenario_results)
        
        violations = sum(1 for r in scenario_results if r.get("constraint_violated", False))
        cvr = violations / len(scenario_results)
        
        regrets = [r.get("regret", 0.0) for r in scenario_results]
        regret = sum(regrets) / len(regrets)
        
        costs = [r.get("cost", 0.0) for r in scenario_results]
        total_cost = sum(costs)
        avg_cost = total_cost / len(scenario_results)
        
        hf_invocations = sum(1 for r in scenario_results if r.get("hf_invoked", False))
        hf_rate = hf_invocations / len(scenario_results)
        
        suff_errors = [r.get("sufficiency_error", 0.0) for r in scenario_results]
        sufficiency_error = sum(suff_errors) / len(suff_errors)
        
        restorations = [r.get("restoration", 0.0) for r in scenario_results]
        restoration_rate = sum(restorations) / len(restorations)
        
        audit_scores = [r.get("auditability", 0.0) for r in scenario_results]
        auditability_score = sum(audit_scores) / len(audit_scores)
        
        # SCORE COMPOSITE (nouveau calcul)
        # Base = DCR (le plus important)
        overall = dcr
        
        # Pénalités
        overall -= cvr * 0.8          # Violations pénalisent fort
        overall -= regret * 0.5       # Regret pénalise
        overall -= avg_cost * 0.05    # Coût pénalise légèrement
        overall -= sufficiency_error * 0.3  # Erreur de suffisance
        
        # Bonus
        overall += restoration_rate * 0.15
        overall += auditability_score * 0.10
        
        # Normaliser dans [0, 1]
        overall = max(0, min(1, overall))
        
        return AblationMetrics(
            ablation_id=ablation_config.ablation_id,
            ablation_name=ablation_config.name,
            dcr=round(dcr, 4),
            cvr=round(cvr, 4),
            regret=round(regret, 4),
            avg_cost=round(avg_cost, 4),
            total_cost=round(total_cost, 4),
            hf_invocations=hf_invocations,
            hf_rate=round(hf_rate, 4),
            sufficiency_error=round(sufficiency_error, 4),
            restoration_rate=round(restoration_rate, 4),
            auditability_score=round(auditability_score, 4),
            overall_score=round(overall, 4)
        )
    
    def to_dict(self, metrics: AblationMetrics) -> Dict:
        return {
            "ablation_id": metrics.ablation_id,
            "ablation_name": metrics.ablation_name,
            "DCR": metrics.dcr,
            "CVR": metrics.cvr,
            "Regret": metrics.regret,
            "AvgCost": metrics.avg_cost,
            "TotalCost": metrics.total_cost,
            "HFInvocations": metrics.hf_invocations,
            "HFRate": metrics.hf_rate,
            "SufficiencyError": metrics.sufficiency_error,
            "Restoration": metrics.restoration_rate,
            "Auditability": metrics.auditability_score,
            "Overall": metrics.overall_score
        }


if __name__ == "__main__":
    computer = AblationMetricsComputer()
    print("✅ AblationMetricsComputer CORRIGÉ")
