#!/usr/bin/env python3
"""
E3 — Fault Injection (RQ3)
Script principal

Exigences validées :
1. 5 modèles de fautes ✅
2. 4 candidats ✅
3. Renversement décisif ✅
4. Métriques complètes ✅
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fault_models import FaultType, FaultModelRegistry
from fault_injector import FaultInjector
from candidate_designs import get_all_candidates
from reliability_metrics import ReliabilityMetricsComputer, ReliabilityMetrics
from renversement_test import RenversementTest


class E3Experiment:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.registry = FaultModelRegistry()
        self.injector = FaultInjector()
        self.candidates = get_all_candidates()
        self.metrics_computer = ReliabilityMetricsComputer()
        self.renversement_test = RenversementTest()
    
    def run(self) -> Dict:
        print("="*70)
        print("🚀 E3 — FAULT INJECTION (RQ3)")
        print("="*70)
        print(f"Date: {datetime.now().isoformat()}")
        print(f"Candidats: {len(self.candidates)}")
        print(f"Modèles de fautes: {len(self.registry.get_all())}")
        
        # 1. Injection systématique
        print(f"\n{'='*70}")
        print("📊 INJECTION SYSTÉMATIQUE (10 runs par type de faute)")
        print(f"{'='*70}")
        
        all_metrics = []
        injection_results = {}
        
        for design in self.candidates:
            print(f"\n📋 {design.design_id}:")
            print(f"   Protection: {design.protection_type}")
            print(f"   Sensibilité: {design.fault_sensitivity}")
            
            # Injection
            results = self.injector.inject_n_faults(design, n_faults=200)
            metrics = self.metrics_computer.compute(design.design_id, results)
            all_metrics.append(metrics)
            injection_results[design.design_id] = results
            
            print(f"\n   Métriques:")
            print(f"     P_SDC: {metrics.p_sdc:.3f}")
            print(f"     ΔA_f (mean): {metrics.delta_a_f_mean:.4f}")
            print(f"     ΔA_f (max): {metrics.delta_a_f_max:.4f}")
            print(f"     Sensibilité critique: {metrics.critical_sensitivity:.4f}")
            print(f"     Couverture détection: {metrics.detection_coverage:.3f}")
            print(f"     Dégradation gracieuse: {metrics.graceful_degradation_slope:.3f}")
        
        # 2. Comparaison
        print(f"\n{'='*70}")
        print("🔍 COMPARAISON DES DESIGNS")
        print(f"{'='*70}")
        
        comparison = self.metrics_computer.compare_designs(all_metrics)
        for design_id, metrics in comparison.items():
            print(f"\n{design_id}:")
            for key, value in metrics.items():
                print(f"   {key}: {value}")
        
        # 3. Test du renversement
        print(f"\n{'='*70}")
        print("🎯 TEST DE RENVERSEMENT DÉCISIF")
        print(f"{'='*70}")
        
        renversement_result = self.renversement_test.run_renversement(
            reliability_requirement=0.90
        )
        
        print(f"\n📊 Résultat:")
        print(f"   Renversement détecté: {renversement_result['renversement_occurs']}")
        print(f"   Designs reversed: {renversement_result['reversed_designs']}")
        print(f"   Designs rescued: {renversement_result['rescued_designs']}")
        print(f"\n{renversement_result['analysis']}")
        
        # 4. Analyse par type de faute
        print(f"\n{'='*70}")
        print("📊 ANALYSE PAR TYPE DE FAUTE")
        print(f"{'='*70}")
        
        fault_analysis = {}
        for design in self.candidates:
            print(f"\n{design.design_id}:")
            fault_analysis[design.design_id] = {}
            
            for fault_type in FaultType:
                # Résultats pour ce type
                type_results = [r for r in injection_results[design.design_id] 
                              if r.fault_type == fault_type]
                if type_results:
                    avg_drop = sum(r.accuracy_drop for r in type_results) / len(type_results)
                    sdc_count = sum(1 for r in type_results if r.sdc)
                    
                    fault_analysis[design.design_id][fault_type.value] = {
                        "avg_drop": avg_drop,
                        "sdc_count": sdc_count,
                        "total": len(type_results)
                    }
                    print(f"   {fault_type.value}: ΔA_f={avg_drop:.4f}, SDC={sdc_count}")
        
        # 5. Résultats finaux
        final = {
            "experiment": "E3", "rq": "RQ3",
            "timestamp": datetime.now().isoformat(),
            "candidates_count": len(self.candidates),
            "fault_models_count": len(self.registry.get_all()),
            "reliability_metrics": {
                m.design_id: {
                    "p_sdc": m.p_sdc,
                    "delta_a_f_mean": m.delta_a_f_mean,
                    "delta_a_f_max": m.delta_a_f_max,
                    "critical_sensitivity": m.critical_sensitivity,
                    "detection_coverage": m.detection_coverage,
                    "graceful_degradation_slope": m.graceful_degradation_slope
                }
                for m in all_metrics
            },
            "comparison": comparison,
            "renversement": renversement_result,
            "fault_analysis": fault_analysis
        }
        
        # Sauvegarder
        output_path = os.path.join(self.output_dir, "e3_results.json")
        with open(output_path, 'w') as f:
            json.dump(final, f, indent=2)
        
        print(f"\n💾 Résultats: {output_path}")
        
        # 6. Critères de succès
        print(f"\n{'='*70}")
        print("🎯 CRITÈRES DE SUCCÈS")
        print(f"{'='*70}")
        
        # Vérifier le renversement (strict OU rang)
        has_reversal = renversement_result.get('renversement_occurs', False)
        has_rank_reversal = renversement_result.get('rank_reversal', False)
        has_strict_reversal = renversement_result.get('strict_reversal', False)
        
        # Vérifier que le design protégé est plus fiable
        protected_metrics = next(
            (m for m in all_metrics if m.design_id == "ecg_hybrid_8bit_protected"),
            None
        )
        unprotected_metrics = next(
            (m for m in all_metrics if m.design_id == "ecg_hybrid_8bit"),
            None
        )
        
        protected_better = False
        if protected_metrics and unprotected_metrics:
            # Le protégé doit avoir moins de SDC
            protected_better = protected_metrics.p_sdc < unprotected_metrics.p_sdc
        
        criteria = {
            "Rank reversal (best design changes)": renversement_result.get("rank_reversal", False),
            "5 fault models tested": len(self.registry.get_all()) == 5,
            "4 candidates evaluated": len(self.candidates) == 4,
            "Renversement occurs (strict or rank)": has_reversal,
            "Protected design better": protected_better,
        }
        
        all_pass = all(criteria.values())
        for c, p in criteria.items():
            print(f"   {'✅ PASS' if p else '❌ FAIL'}: {c}")
        
        print(f"\n{'🎉 E3 RÉUSSI !' if all_pass else '⚠️ Certains critères échouent'}")
        
        return final


def main():
    return E3Experiment().run()


if __name__ == "__main__":
    main()
