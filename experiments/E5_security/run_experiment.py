#!/usr/bin/env python3
"""
E5 — Security Meta-Reasoning (RQ3)
Version CORRIGÉE
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from threat_models import ThreatModelRegistry
from attack_scenarios import AttackScenarioRegistry
from security_designs import get_all_security_designs
from asr_evaluator import ASREvaluator
from security_meta_reasoner import SecurityMetaReasoner


class E5Experiment:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.threat_registry = ThreatModelRegistry()
        self.attack_registry = AttackScenarioRegistry()
        self.designs = get_all_security_designs()
        self.evaluator = ASREvaluator(asr_threshold=0.20)
        self.reasoner = SecurityMetaReasoner()
    
    def run(self) -> Dict:
        print("="*70)
        print("🚀 E5 — SECURITY META-REASONING (RQ3)")
        print("="*70)
        print(f"Date: {datetime.now().isoformat()}")
        print(f"Menaces: {len(self.threat_registry.models)}")
        print(f"Attaques: {len(self.attack_registry.scenarios)}")
        print(f"Designs: {len(self.designs)}")
        
        # 1. ASR par design
        print(f"\n{'='*70}")
        print("📊 ASR PAR DESIGN SOUS DIFFÉRENTES MENACES")
        print(f"{'='*70}")
        
        asr_results = {}
        for threat_id in ["T0", "T1", "T2", "T3", "T4"]:
            threat = self.threat_registry.get_by_id(threat_id)
            if not threat:
                continue
            
            print(f"\n--- Menace {threat_id}: {threat.name} (level={threat.threat_level}) ---")
            
            comparison = self.evaluator.compare_designs(self.designs, threat)
            asr_results[threat_id] = comparison
            
            for design_id, metrics in comparison.items():
                status = "✅" if metrics['all_valid'] else "❌"
                print(f"   {status} {design_id}: max_asr={metrics['max_asr']:.3f}")
        
        # 2. Test décisif
        print(f"\n{'='*70}")
        print("🎯 TEST DÉCISIF")
        print(f"{'='*70}")
        
        decisive_result = self.reasoner.run_decisive_test()
        
        # 3. Sélection par menace
        print(f"\n{'='*70}")
        print("🎯 SÉLECTION DE DESIGN PAR MENACE")
        print(f"{'='*70}")
        
        selections = {}
        for threat_id in ["T0", "T1", "T2", "T3", "T4"]:
            threat = self.threat_registry.get_by_id(threat_id)
            if not threat:
                continue
            
            decision = self.reasoner.select_best_design(threat)
            selections[threat_id] = {
                "threat_name": threat.name,
                "threat_level": threat.threat_level,
                "selected_design": decision.selected_design_id,
                "decision": decision.decision,
                "reason": decision.reason,
                "asr_max": decision.asr_max,
                "resource_violation": decision.resource_violation
            }
            
            print(f"\n{threat_id} (level={threat.threat_level}):")
            print(f"   Design: {decision.selected_design_id}")
            print(f"   Décision: {decision.decision}")
            print(f"   ASR max: {decision.asr_max:.3f}")
        
        # 4. Résultats finaux
        final = {
            "experiment": "E5", "rq": "RQ3",
            "timestamp": datetime.now().isoformat(),
            "threats_count": len(self.threat_registry.models),
            "attacks_count": len(self.attack_registry.scenarios),
            "designs_count": len(self.designs),
            "asr_results": asr_results,
            "selections": selections,
            "decisive_test": decisive_result
        }
        
        output_path = os.path.join(self.output_dir, "e5_results.json")
        with open(output_path, 'w') as f:
            json.dump(final, f, indent=2)
        
        print(f"\n💾 Résultats: {output_path}")
        
        # 5. Critères
        print(f"\n{'='*70}")
        print("🎯 CRITÈRES DE SUCCÈS")
        print(f"{'='*70}")
        
        # Sémantique corrigée : DEFER/REJECT/INFEASIBLE au lieu de REJECT uniquement
        t4_none_decision = decisive_result.get("threat_results", {}).get("T4", {}).get("sec_none", {}).get("decision", "")
        t4_ensemble_decision = decisive_result.get("threat_results", {}).get("T4", {}).get("sec_ensemble", {}).get("decision", "")
        
        criteria = {
            "5 threat models (T_sec)": len(self.threat_registry.models) == 5,
            "5+ attack scenarios": len(self.attack_registry.scenarios) >= 5,
            "5 security designs": len(self.designs) == 5,
            "Renversement detected": decisive_result.get("renversement_detected", False),
            "T4 defers/rejects unprotected": t4_none_decision in ["DEFER", "REJECT", "INFEASIBLE"],
            "T4 rejects over-protected": t4_ensemble_decision in ["REJECT", "INFEASIBLE"],
        }
        
        all_pass = all(criteria.values())
        for c, p in criteria.items():
            print(f"   {'✅ PASS' if p else '❌ FAIL'}: {c}")
        
        print(f"\n{'🎉 E5 RÉUSSI !' if all_pass else '⚠️ Certains critères échouent'}")
        
        return final


def main():
    return E5Experiment().run()


if __name__ == "__main__":
    main()
