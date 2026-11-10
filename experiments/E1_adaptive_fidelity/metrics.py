"""
Metrics - Métriques E1
Exigence : accord décisionnel, coût, réduction coût, taux HF, regret, précision/rappel
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PolicyMetrics:
    """Métriques pour une politique"""
    policy_name: str
    total_cases: int = 0
    correct_decisions: int = 0
    agreement_rate: float = 0.0
    total_cost: float = 0.0
    avg_cost: float = 0.0
    total_time_s: float = 0.0
    avg_time_s: float = 0.0
    hf_invocations: int = 0
    hf_rate: float = 0.0
    regret: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    cost_reduction_vs_exhaustive: float = 0.0


class MetricsComputer:
    """Calcule les métriques E1"""
    
    def compute_policy_metrics(self, results: List) -> PolicyMetrics:
        """Calcule les métriques pour une politique"""
        if not results:
            return PolicyMetrics(policy_name="unknown")
        
        policy_name = results[0].policy.value
        total = len(results)
        
        correct = sum(1 for r in results if r.correct)
        total_cost = sum(r.total_cost for r in results)
        total_time = sum(r.total_time_s for r in results)
        
        # Invocations haute fidélité (F2+)
        hf_invocations = sum(
            1 for r in results 
            for s in r.steps 
            if s.fidelity.value >= 2  # F2 ou F3
        )
        
        # Précision / Rappel (PASS correct)
        true_pos = sum(1 for r in results if r.final_verdict == "PASS" and r.correct)
        false_pos = sum(1 for r in results if r.final_verdict == "PASS" and not r.correct)
        false_neg = sum(1 for r in results if r.final_verdict == "FAIL" and not r.correct)
        
        precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0.0
        recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0.0
        
        return PolicyMetrics(
            policy_name=policy_name,
            total_cases=total,
            correct_decisions=correct,
            agreement_rate=correct / total,
            total_cost=total_cost,
            avg_cost=total_cost / total,
            total_time_s=total_time,
            avg_time_s=total_time / total,
            hf_invocations=hf_invocations,
            hf_rate=hf_invocations / total,
            precision=precision,
            recall=recall
        )
    
    def compute_regret(self, policy_results: List, 
                      ground_truth_verdicts: Dict[str, str]) -> float:
        """
        Calcule le regret : combien de décisions incorrectes
        """
        if not policy_results:
            return 0.0
        
        incorrect = sum(
            1 for r in policy_results 
            if r.final_verdict != ground_truth_verdicts.get(r.case_id, "UNKNOWN")
        )
        
        return incorrect / len(policy_results)
    
    def compare_policies(self, all_metrics: List[PolicyMetrics]) -> Dict:
        """
        Compare les politiques et calcule la réduction de coût
        """
        # Trouver la politique exhaustive comme référence
        exhaustive = next(
            (m for m in all_metrics if m.policy_name == "exhaustive"),
            None
        )
        
        if not exhaustive:
            return {}
        
        comparison = {}
        for m in all_metrics:
            if exhaustive.avg_cost > 0:
                cost_reduction = (exhaustive.avg_cost - m.avg_cost) / exhaustive.avg_cost
            else:
                cost_reduction = 0.0
            
            comparison[m.policy_name] = {
                "agreement_rate": round(m.agreement_rate, 3),
                "avg_cost": round(m.avg_cost, 3),
                "avg_time_s": round(m.avg_time_s, 3),
                "hf_rate": round(m.hf_rate, 3),
                "precision": round(m.precision, 3),
                "recall": round(m.recall, 3),
                "cost_reduction_vs_exhaustive": round(cost_reduction, 3)
            }
        
        return comparison


if __name__ == "__main__":
    import json
    computer = MetricsComputer()
    print("✅ MetricsComputer prêt")
