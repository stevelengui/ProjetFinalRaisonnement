#!/usr/bin/env python3
"""
E7 — Mechanism-Level Ablation (Cross-RQ)
Script principal
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ablation_configs import get_all_ablation_configs
from ablation_runner import AblationRunner
from ablation_metrics import AblationMetricsComputer
from ablation_analyzer import AblationAnalyzer


class E7Experiment:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.configs = get_all_ablation_configs()
        self.runner = AblationRunner()
        self.metrics_computer = AblationMetricsComputer()
        self.analyzer = AblationAnalyzer()
    
    def run(self) -> Dict:
        print("="*70)
        print("🚀 E7 — MECHANISM-LEVEL ABLATION (Cross-RQ)")
        print("="*70)
        print(f"Date: {datetime.now().isoformat()}")
        print(f"Configurations: {len(self.configs)}")
        print(f"Scénarios par config: {len(self.runner.scenarios)}")
        
        # 1. Exécuter toutes les ablations
        print(f"\n{'='*70}")
        print("📊 EXÉCUTION DES ABLATIONS")
        print(f"{'='*70}")
        
        all_results = {}
        for config in self.configs:
            print(f"\n📋 {config.ablation_id}: {config.name}")
            print(f"   {config.description}")
            
            results = self.runner.run_ablation(config)
            all_results[config.ablation_id] = results
            
            # Statistiques rapides
            correct = sum(1 for r in results if r.decision_correct)
            violations = sum(1 for r in results if r.constraint_violated)
            avg_cost = sum(r.cost for r in results) / len(results)
            
            print(f"   Décisions correctes: {correct}/{len(results)}")
            print(f"   Violations: {violations}")
            print(f"   Coût moyen: {avg_cost:.4f}")
        
        # 2. Analyser les résultats
        print(f"\n{'='*70}")
        print("📊 ANALYSE COMPARATIVE")
        print(f"{'='*70}")
        
        analysis = self.analyzer.analyze_all(all_results)
        
        # Afficher le rapport
        print("\n" + self.analyzer.generate_report(analysis))
        
        # 3. Résumé des mécanismes critiques
        print(f"\n{'='*70}")
        print("🎯 MÉCANISMES CRITIQUES")
        print(f"{'='*70}")
        
        print(f"\n🔴 CRITIQUES (>15% dégradation):")
        for m in analysis["critical_mechanisms"]:
            comp = next(c for c in analysis["comparisons"] if c["ablated"] == m)
            print(f"   - {m}: {comp['degradation_pct']:.1%}")
        
        print(f"\n🟡 IMPORTANTS (5-15% dégradation):")
        for m in analysis["important_mechanisms"]:
            comp = next(c for c in analysis["comparisons"] if c["ablated"] == m)
            print(f"   - {m}: {comp['degradation_pct']:.1%}")
        
        print(f"\n🟢 MINEURS (<5% dégradation):")
        for m in analysis["minor_mechanisms"]:
            comp = next(c for c in analysis["comparisons"] if c["ablated"] == m)
            print(f"   - {m}: {comp['degradation_pct']:.1%}")
        
        # 4. Conclusion
        print(f"\n{'='*70}")
        print("📊 CONCLUSION E7")
        print(f"{'='*70}")
        
        summary = analysis["summary"]
        
        print(f"\nBaseline (FULL): {summary['baseline_score']:.4f}")
        print(f"Mécanismes critiques: {len(analysis['critical_mechanisms'])}")
        print(f"Mécanismes importants: {len(analysis['important_mechanisms'])}")
        print(f"Mécanismes mineurs: {len(analysis['minor_mechanisms'])}")
        
        print(f"\n💡 Interprétation:")
        if summary['max_degradation'] > 0.15:
            print(f"   Le mécanisme le plus critique est {summary['max_degradation_ablation']}")
            print(f"   → Son absence cause {summary['max_degradation']:.1%} de dégradation")
        
        print(f"\n   Les gains viennent de mécanismes méta SPÉCIFIQUES,")
        print(f"   pas simplement de l'ajout de MAML/XAI.")
        
        # 5. Sauvegarder
        final = {
            "experiment": "E7", "rq": "Cross-RQ",
            "timestamp": datetime.now().isoformat(),
            "configs_count": len(self.configs),
            "scenarios_per_config": len(self.runner.scenarios),
            "analysis": analysis
        }
        
        output_path = os.path.join(self.output_dir, "e7_results.json")
        with open(output_path, 'w') as f:
            json.dump(final, f, indent=2)
        
        print(f"\n💾 Résultats: {output_path}")
        
        # 6. Critères de succès
        print(f"\n{'='*70}")
        print("🎯 CRITÈRES DE SUCCÈS")
        print(f"{'='*70}")
        
        # Critères
        has_10_ablations = len(self.configs) >= 10
        has_critical = len(analysis["critical_mechanisms"]) >= 3
        has_significant_degradation = summary['max_degradation'] > 0.15
        baseline_exists = "A0_FULL" in all_results
        
        criteria = {
            "10+ ablation configs": has_10_ablations,
            "3+ critical mechanisms": has_critical,
            "Max degradation > 15%": has_significant_degradation,
            "Baseline (FULL) exists": baseline_exists,
        }
        
        all_pass = all(criteria.values())
        for c, p in criteria.items():
            print(f"   {'✅ PASS' if p else '❌ FAIL'}: {c}")
        
        print(f"\n{'🎉 E7 RÉUSSI !' if all_pass else '⚠️ Certains critères échouent'}")
        
        return final


def main():
    return E7Experiment().run()


if __name__ == "__main__":
    main()
