#!/usr/bin/env python3
"""
E2 — Lifecycle Replay (RQ5)
Script principal
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deployment_contract import (
    create_ecg_deployment_contract,
    create_vibration_deployment_contract,
    DeploymentContract
)
from lifecycle_perturbations import get_all_perturbations
from intervention_selector import InterventionSelector
from lifecycle_monitor import LifecycleMonitor
from replay_engine import ControlledLifecycleReplay


class E2Experiment:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.contracts = [
            create_ecg_deployment_contract(),
            create_vibration_deployment_contract()
        ]
        self.perturbations = get_all_perturbations()
        self.selector = InterventionSelector()
    
    def run(self) -> Dict:
        print("="*70)
        print("🚀 E2 — LIFECYCLE REPLAY (RQ5)")
        print("="*70)
        print(f"Date: {datetime.now().isoformat()}")
        print(f"Contrats: {len(self.contracts)}")
        print(f"Perturbations: {len(self.perturbations)}")
        
        all_results = []
        
        # 1. Replay pour chaque contrat
        for contract in self.contracts:
            print(f"\n{'='*70}")
            print(f"📋 Contrat: {contract.contract_id}")
            print(f"   Design: {contract.deployed_design.design_id}")
            print(f"   Domaine: {contract.domain}")
            print(f"{'='*70}")
            
            replay = ControlledLifecycleReplay(contract)
            result = replay.run_full_replay()
            
            # Enveloppe de validité
            envelope = replay.get_validity_envelope()
            
            all_results.append({
                "contract_id": contract.contract_id,
                "design_id": contract.deployed_design.design_id,
                "domain": contract.domain,
                "replay_result": result,
                "validity_envelope": envelope
            })
        
        # 2. Analyse comparative
        print(f"\n{'='*70}")
        print("📊 ANALYSE COMPARATIVE")
        print(f"{'='*70}")
        
        # Statistiques globales
        total_events = sum(r["replay_result"]["total_events"] for r in all_results)
        total_matches = sum(r["replay_result"]["matches_count"] for r in all_results)
        
        print(f"\nTotal événements: {total_events}")
        print(f"Interventions correctes: {total_matches}/{total_events}")
        print(f"Taux de correspondance: {total_matches/total_events:.0%}")
        
        # Par perturbation
        perturbation_analysis = {}
        for p in self.perturbations:
            p_results = []
            for r in all_results:
                for event in r["replay_result"]["events"]:
                    if event["perturbation_id"] == p.perturbation_id:
                        p_results.append(event)
            
            if p_results:
                matches = sum(1 for e in p_results if e["matches_expected"])
                perturbation_analysis[p.perturbation_id] = {
                    "class": p.perturbation_class.value,
                    "expected": p.expected_intervention,
                    "matches": matches,
                    "total": len(p_results),
                    "match_rate": matches / len(p_results)
                }
        
        print("\n📊 Par perturbation:")
        for pid, analysis in perturbation_analysis.items():
            status = "✅" if analysis["match_rate"] == 1.0 else "⚠️"
            print(f"   {status} {pid} ({analysis['class']}): "
                  f"{analysis['matches']}/{analysis['total']} "
                  f"(expected: {analysis['expected']})")
        
        # 3. Enveloppes de validité
        print(f"\n{'='*70}")
        print("📊 ENVELOPPES DE VALIDITÉ")
        print(f"{'='*70}")
        
        for r in all_results:
            envelope = r["validity_envelope"]
            print(f"\n{r['contract_id']} ({r['domain']}):")
            print(f"   Perturbations valides: {envelope['validity_envelope_size']}/{envelope['total_perturbations']}")
            print(f"   Perturbations cassant la validité: {envelope['invalid_perturbations']}")
        
        # 4. Résultats finaux
        final = {
            "experiment": "E2", "rq": "RQ5",
            "timestamp": datetime.now().isoformat(),
            "contracts_count": len(self.contracts),
            "perturbations_count": len(self.perturbations),
            "total_events": total_events,
            "total_matches": total_matches,
            "overall_match_rate": total_matches / total_events if total_events > 0 else 0,
            "perturbation_analysis": perturbation_analysis,
            "contract_results": all_results
        }
        
        output_path = os.path.join(self.output_dir, "e2_results.json")
        with open(output_path, 'w') as f:
            json.dump(final, f, indent=2)
        
        print(f"\n💾 Résultats: {output_path}")
        
        # 5. Critères de succès
        print(f"\n{'='*70}")
        print("🎯 CRITÈRES DE SUCCÈS")
        print(f"{'='*70}")
        
        # Vérifier les critères
        has_contract = len(self.contracts) >= 2  # ECG + Vibration
        has_c0_to_c4 = len(self.perturbations) == 5  # C0-C4
        
        # Vérifier que C0 → CONTINUE
        c0_result = perturbation_analysis.get("P0", {})
        c0_correct = c0_result.get("match_rate", 0) == 1.0
        
        # Vérifier que C4 → REDESIGN
        c4_result = perturbation_analysis.get("P4", {})
        c4_correct = c4_result.get("match_rate", 0) == 1.0
        
        # Vérifier que le taux global est élevé
        global_match_high = (total_matches / total_events) >= 0.8 if total_events > 0 else False
        
        criteria = {
            "2+ deployment contracts": has_contract,
            "5 perturbations (C0-C4)": has_c0_to_c4,
            "C0 uses CONTINUE": c0_correct,
            "C4 uses REDESIGN": c4_correct,
            "Overall match rate ≥ 0.80": global_match_high,
        }
        
        all_pass = all(criteria.values())
        for c, p in criteria.items():
            print(f"   {'✅ PASS' if p else '❌ FAIL'}: {c}")
        
        print(f"\n{'🎉 E2 RÉUSSI !' if all_pass else '⚠️ Certains critères échouent'}")
        
        # Note importante
        print(f"\n📝 NOTE : Ceci est un 'CONTROLLED LIFECYCLE REPLAY'")
        print(f"   PAS une 'runtime adaptation' en conditions réelles.")
        print(f"   Les perturbations sont simulées et contrôlées.")
        
        return final


def main():
    return E2Experiment().run()


if __name__ == "__main__":
    main()
