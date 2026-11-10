"""
Ablation Analyzer - Analyse comparative des ablations
"""

from dataclasses import dataclass
from typing import Dict, List

from ablation_configs import AblationConfig, get_all_ablation_configs
from ablation_metrics import AblationMetrics, AblationMetricsComputer
from ablation_runner import AblationRunner, ScenarioResult


@dataclass
class AblationComparison:
    """Résultat d'une comparaison"""
    baseline: str
    ablated: str
    baseline_score: float
    ablated_score: float
    degradation: float
    degradation_pct: float
    is_significant: bool


class AblationAnalyzer:
    """
    Analyse les résultats d'ablation
    Identifie les mécanismes critiques
    """
    
    def __init__(self):
        self.metrics_computer = AblationMetricsComputer()
    
    def analyze_all(self, results: Dict[str, List[ScenarioResult]]) -> Dict:
        """
        Analyse toutes les ablations
        """
        configs = {c.ablation_id: c for c in get_all_ablation_configs()}
        
        # 1. Calculer les métriques pour chaque ablation
        all_metrics = {}
        for ablation_id, scenario_results in results.items():
            config = configs.get(ablation_id)
            if not config:
                continue
            
            # Convertir les résultats en dicts
            results_dicts = [
                {
                    "decision_correct": r.decision_correct,
                    "constraint_violated": r.constraint_violated,
                    "regret": r.regret,
                    "cost": r.cost,
                    "hf_invoked": r.hf_invoked,
                    "sufficiency_error": r.sufficiency_error,
                    "restoration": r.restoration,
                    "auditability": r.auditability
                }
                for r in scenario_results
            ]
            
            metrics = self.metrics_computer.compute_metrics(config, results_dicts)
            all_metrics[ablation_id] = metrics
        
        # 2. Comparer avec le baseline (FULL)
        baseline_metrics = all_metrics.get("A0_FULL")
        comparisons = []
        
        if baseline_metrics:
            for ablation_id, metrics in all_metrics.items():
                if ablation_id == "A0_FULL":
                    continue
                
                degradation = baseline_metrics.overall_score - metrics.overall_score
                degradation_pct = (degradation / baseline_metrics.overall_score 
                                 if baseline_metrics.overall_score > 0 else 0)
                
                comparisons.append(AblationComparison(
                    baseline="A0_FULL",
                    ablated=ablation_id,
                    baseline_score=baseline_metrics.overall_score,
                    ablated_score=metrics.overall_score,
                    degradation=round(degradation, 4),
                    degradation_pct=round(degradation_pct, 4),
                    is_significant=degradation > 0.05
                ))
        
        # Trier par dégradation décroissante
        comparisons.sort(key=lambda c: c.degradation, reverse=True)
        
        # 3. Identifier les mécanismes critiques
        critical_mechanisms = [c for c in comparisons if c.degradation > 0.15]
        important_mechanisms = [c for c in comparisons if 0.05 < c.degradation <= 0.15]
        minor_mechanisms = [c for c in comparisons if c.degradation <= 0.05]
        
        return {
            "all_metrics": {
                aid: self.metrics_computer.to_dict(m)
                for aid, m in all_metrics.items()
            },
            "comparisons": [
                {
                    "ablated": c.ablated,
                    "baseline_score": c.baseline_score,
                    "ablated_score": c.ablated_score,
                    "degradation": c.degradation,
                    "degradation_pct": c.degradation_pct,
                    "is_significant": c.is_significant
                }
                for c in comparisons
            ],
            "critical_mechanisms": [c.ablated for c in critical_mechanisms],
            "important_mechanisms": [c.ablated for c in important_mechanisms],
            "minor_mechanisms": [c.ablated for c in minor_mechanisms],
            "summary": {
                "baseline_score": baseline_metrics.overall_score if baseline_metrics else 0,
                "num_ablations": len(comparisons),
                "num_significant": sum(1 for c in comparisons if c.is_significant),
                "max_degradation": max((c.degradation for c in comparisons), default=0),
                "max_degradation_ablation": comparisons[0].ablated if comparisons else None
            }
        }
    
    def generate_report(self, analysis: Dict) -> str:
        """Génère un rapport textuel"""
        lines = [
            "=" * 70,
            "ABLATION STUDY REPORT",
            "=" * 70,
            ""
        ]
        
        summary = analysis["summary"]
        lines.extend([
            f"Baseline Score (FULL): {summary['baseline_score']:.4f}",
            f"Number of ablations: {summary['num_ablations']}",
            f"Significant degradations: {summary['num_significant']}",
            f"Max degradation: {summary['max_degradation']:.4f} "
            f"({summary['max_degradation_ablation']})",
            "",
            "-" * 70,
            "MECHANISM IMPORTANCE RANKING",
            "-" * 70,
        ])
        
        for i, comp in enumerate(analysis["comparisons"], 1):
            marker = "🔴" if comp["degradation"] > 0.15 else ("🟡" if comp["degradation"] > 0.05 else "🟢")
            lines.append(
                f"{marker} {i}. {comp['ablated']}: "
                f"degradation = {comp['degradation']:.4f} "
                f"({comp['degradation_pct']:.1%})"
            )
        
        lines.extend([
            "",
            "-" * 70,
            "CRITICAL MECHANISMS (>15% degradation)",
            "-" * 70,
        ])
        for m in analysis["critical_mechanisms"]:
            lines.append(f"   - {m}")
        
        lines.extend([
            "",
            "-" * 70,
            "IMPORTANT MECHANISMS (5-15% degradation)",
            "-" * 70,
        ])
        for m in analysis["important_mechanisms"]:
            lines.append(f"   - {m}")
        
        lines.extend([
            "",
            "-" * 70,
            "MINOR MECHANISMS (<5% degradation)",
            "-" * 70,
        ])
        for m in analysis["minor_mechanisms"]:
            lines.append(f"   - {m}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)


if __name__ == "__main__":
    runner = AblationRunner()
    analyzer = AblationAnalyzer()
    
    print("Exécution des ablations...")
    results = runner.run_all_ablations()
    
    analysis = analyzer.analyze_all(results)
    print(analyzer.generate_report(analysis))
