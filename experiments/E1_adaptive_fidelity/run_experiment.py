#!/usr/bin/env python3
"""
E1 — Adaptive Evaluation-Fidelity (RQ2)
Script principal - Version FINALE
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fidelity_hierarchy import FidelityHierarchy, Fidelity
from test_cases import get_all_test_cases, get_cases_by_category
from policies import get_all_policies, PolicyType
from metrics import MetricsComputer, PolicyMetrics
from claim_65_test import ClaimValidator


class E1Experiment:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.hierarchy = FidelityHierarchy()
        self.cases = get_all_test_cases()
        self.policies = get_all_policies(self.hierarchy)
        self.metrics_computer = MetricsComputer()
        self.claim_validator = ClaimValidator()
        
        self.all_results: Dict[str, List] = {}
    
    def run(self) -> Dict:
        print("="*70)
        print("🚀 E1 — ADAPTIVE EVALUATION-FIDELITY (RQ2)")
        print("="*70)
        print(f"Date: {datetime.now().isoformat()}")
        print(f"Cas: {len(self.cases)}")
        print(f"Politiques: {len(self.policies)}")
        
        # 1. Exécuter chaque politique
        for policy in self.policies:
            print(f"\n{'='*70}")
            print(f"📋 Politique: {policy.type.value}")
            print(f"{'='*70}")
            
            results = []
            for case in self.cases:
                result = policy.evaluate(case)
                results.append(result)
            
            self.all_results[policy.type.value] = results
            
            correct = sum(1 for r in results if r.correct)
            print(f"   ✅ {correct}/{len(results)} corrects ({correct/len(results):.1%})")
        
        # 2. Métriques par politique
        print(f"\n{'='*70}")
        print("📊 MÉTRIQUES PAR POLITIQUE")
        print(f"{'='*70}")
        
        policy_metrics = {}
        for policy_name, results in self.all_results.items():
            m = self.metrics_computer.compute_policy_metrics(results)
            policy_metrics[policy_name] = m
            
            print(f"\n{policy_name}:")
            print(f"   Accord: {m.agreement_rate:.1%}")
            print(f"   Coût moyen: {m.avg_cost:.3f}")
            print(f"   Temps moyen: {m.avg_time_s:.3f}s")
            print(f"   Taux HF: {m.hf_rate:.1%}")
            print(f"   Précision: {m.precision:.1%}")
            print(f"   Rappel: {m.recall:.1%}")
        
        # 3. Comparaison
        print(f"\n{'='*70}")
        print("🔍 COMPARAISON DES POLITIQUES")
        print(f"{'='*70}")
        
        comparison = self.metrics_computer.compare_policies(list(policy_metrics.values()))
        for policy_name, metrics in comparison.items():
            print(f"\n{policy_name}:")
            for key, value in metrics.items():
                print(f"   {key}: {value}")
        
        # 4. Test du claim
        print(f"\n{'='*70}")
        print("🎯 TEST DU CLAIM")
        print(f"{'='*70}")
        
        adaptive = policy_metrics.get("adaptive")
        exhaustive = policy_metrics.get("exhaustive")
        
        claim_result = None
        if adaptive and exhaustive:
            claim_result = self.claim_validator.validate(adaptive, exhaustive)
            
            # Claim original
            orig = claim_result['original_claim']
            print(f"\n   === CLAIM ORIGINAL (65%) ===")
            print(f"   Cible: {orig['target']:.0%}")
            print(f"   Atteint: {orig['achieved']}")
            print(f"   Verdict: {orig['verdict']}")
            
            # Claim reformulé
            ref = claim_result['reformulated_claim']
            print(f"\n   === CLAIM REFORMULÉ ===")
            print(f"   Énoncé: {ref['statement']}")
            print(f"   Cible réduction: {ref['target_reduction']:.0%}")
            print(f"   Réel: {ref['actual_reduction']:.1%}")
            print(f"   Accord: {ref['actual_agreement']:.1%}")
            print(f"   Verdict: {ref['verdict']}")
            
            print(f"\n   {claim_result['explanation']}")
        
        # 5. Métriques par catégorie
        print(f"\n{'='*70}")
        print("📊 MÉTRIQUES PAR CATÉGORIE")
        print(f"{'='*70}")
        
        categories = get_cases_by_category()
        category_metrics = {}
        
        for cat_name, cat_cases in categories.items():
            cat_ids = {c.case_id for c in cat_cases}
            category_metrics[cat_name] = {}
            
            for policy_name, results in self.all_results.items():
                cat_results = [r for r in results if r.case_id in cat_ids]
                if cat_results:
                    correct = sum(1 for r in cat_results if r.correct)
                    avg_cost = sum(r.total_cost for r in cat_results) / len(cat_results)
                    
                    category_metrics[cat_name][policy_name] = {
                        "cases": len(cat_results),
                        "correct": correct,
                        "accuracy": correct / len(cat_results),
                        "avg_cost": avg_cost
                    }
            
            print(f"\n{cat_name}:")
            for policy_name, m in category_metrics[cat_name].items():
                print(f"   {policy_name}: {m['correct']}/{m['cases']} ({m['accuracy']:.0%}), coût={m['avg_cost']:.3f}")
        
        # 6. Résultats finaux
        final = {
            "experiment": "E1", "rq": "RQ2",
            "timestamp": datetime.now().isoformat(),
            "cases_count": len(self.cases),
            "policies_count": len(self.policies),
            "policy_metrics": {
                name: {
                    "agreement_rate": m.agreement_rate,
                    "avg_cost": m.avg_cost,
                    "avg_time_s": m.avg_time_s,
                    "hf_rate": m.hf_rate,
                    "precision": m.precision,
                    "recall": m.recall
                }
                for name, m in policy_metrics.items()
            },
            "comparison": comparison,
            "claim_test": claim_result,
            "category_metrics": category_metrics
        }
        
        # Sauvegarder
        output_path = os.path.join(self.output_dir, "e1_results.json")
        with open(output_path, 'w') as f:
            json.dump(final, f, indent=2)
        
        print(f"\n💾 Résultats: {output_path}")
        
        # 7. Critères de succès
        print(f"\n{'='*70}")
        print("🎯 CRITÈRES DE SUCCÈS")
        print(f"{'='*70}")
        
        criteria = {
            "Adaptive agreement > 0.90": adaptive and adaptive.agreement_rate > 0.90,
            "Adaptive agreement >= exhaustive - 0.05": 
                adaptive and exhaustive and (adaptive.agreement_rate >= exhaustive.agreement_rate - 0.05),
            "Adaptive cost < exhaustive cost": 
                adaptive and exhaustive and (adaptive.avg_cost < exhaustive.avg_cost),
            "Claim ORIGINAL 65% = PROVE": 
                claim_result and claim_result['original_claim']['verdict'] == "PROVE",
            "Claim REFORMULÉ = PROVE": 
                claim_result and claim_result['reformulated_claim']['verdict'] == "PROVE",
        }
        
        all_pass = all(criteria.values())
        for c, p in criteria.items():
            print(f"   {'✅ PASS' if p else '❌ FAIL'}: {c}")
        
        print(f"\n{'🎉 E1 RÉUSSI !' if all_pass else '⚠️ Certains critères échouent'}")
        
        return final


def main():
    return E1Experiment().run()


if __name__ == "__main__":
    main()
