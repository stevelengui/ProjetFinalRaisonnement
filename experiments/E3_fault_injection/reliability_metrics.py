"""
Reliability Metrics - Métriques de fiabilité E3
Exigence : "P_SDC, ΔA_f, sensibilité critique, couverture détection, 
pente de dégradation gracieuse"
"""

from typing import Dict, List
from dataclasses import dataclass
from fault_injector import InjectionResult


@dataclass
class ReliabilityMetrics:
    """Métriques de fiabilité pour un design"""
    design_id: str
    
    # P_SDC : Silent Data Corruption Probability
    p_sdc: float = 0.0
    
    # ΔA_f : Changement moyen d'accuracy après faute
    delta_a_f_mean: float = 0.0
    delta_a_f_std: float = 0.0
    delta_a_f_max: float = 0.0
    
    # Sensibilité critique
    critical_sensitivity: float = 0.0
    
    # Couverture détection
    detection_coverage: float = 0.0
    
    # Pente de dégradation gracieuse
    graceful_degradation_slope: float = 0.0
    
    # Statistiques
    total_injections: int = 0
    sdc_count: int = 0
    detected_count: int = 0
    recovered_count: int = 0


class ReliabilityMetricsComputer:
    """Calcule les métriques de fiabilité"""
    
    def compute(self, design_id: str, 
                results: List[InjectionResult]) -> ReliabilityMetrics:
        """Calcule toutes les métriques pour un design"""
        if not results:
            return ReliabilityMetrics(design_id=design_id)
        
        # P_SDC
        sdc_count = sum(1 for r in results if r.sdc)
        p_sdc = sdc_count / len(results)
        
        # ΔA_f
        drops = [r.accuracy_drop for r in results]
        delta_a_f_mean = sum(drops) / len(drops)
        delta_a_f_max = max(drops)
        
        # Écart-type
        if len(drops) > 1:
            variance = sum((d - delta_a_f_mean) ** 2 for d in drops) / (len(drops) - 1)
            delta_a_f_std = variance ** 0.5
        else:
            delta_a_f_std = 0.0
        
        # Sensibilité critique (impact maximal sur les cas safety-critical)
        critical_drops = [r.accuracy_drop for r in results 
                         if r.accuracy_before >= 0.95 and r.accuracy_drop > 0]
        critical_sensitivity = (
            max(critical_drops) if critical_drops else 0.0
        )
        
        # Couverture détection
        detected = sum(1 for r in results if r.detected)
        detection_coverage = detected / len(results)
        
        # Pente de dégradation gracieuse
        # Plus la pente est faible, plus la dégradation est gracieuse
        if delta_a_f_std > 0:
            graceful_slope = delta_a_f_mean / delta_a_f_std
        else:
            graceful_slope = 0.0
        
        return ReliabilityMetrics(
            design_id=design_id,
            p_sdc=p_sdc,
            delta_a_f_mean=delta_a_f_mean,
            delta_a_f_std=delta_a_f_std,
            delta_a_f_max=delta_a_f_max,
            critical_sensitivity=critical_sensitivity,
            detection_coverage=detection_coverage,
            graceful_degradation_slope=graceful_slope,
            total_injections=len(results),
            sdc_count=sdc_count,
            detected_count=detected,
            recovered_count=sum(1 for r in results if r.recovered)
        )
    
    def compare_designs(self, metrics_list: List[ReliabilityMetrics]) -> Dict:
        """Compare plusieurs designs"""
        comparison = {}
        
        for m in metrics_list:
            comparison[m.design_id] = {
                "p_sdc": round(m.p_sdc, 4),
                "delta_a_f_mean": round(m.delta_a_f_mean, 4),
                "delta_a_f_max": round(m.delta_a_f_max, 4),
                "critical_sensitivity": round(m.critical_sensitivity, 4),
                "detection_coverage": round(m.detection_coverage, 4),
                "graceful_degradation": round(m.graceful_degradation_slope, 4),
                "reliability_score": self._compute_reliability_score(m)
            }
        
        return comparison
    
    def _compute_reliability_score(self, m: ReliabilityMetrics) -> float:
        """
        Score de fiabilité composite (0-1)
        Higher = more reliable
        """
        # Poids
        w_sdc = 0.4       # SDC est critique
        w_delta = 0.2     # Impact moyen
        w_critical = 0.2  # Sensibilité critique
        w_detect = 0.2    # Détection
        
        score = (
            w_sdc * (1 - m.p_sdc) +
            w_delta * (1 - min(1, m.delta_a_f_mean * 10)) +
            w_critical * (1 - min(1, m.critical_sensitivity * 10)) +
            w_detect * m.detection_coverage
        )
        
        return round(score, 4)


if __name__ == "__main__":
    print("✅ ReliabilityMetricsComputer prêt")
