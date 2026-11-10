#!/usr/bin/env python3
"""
E6 — Design Decision Records (RQ4)
Script principal
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from decision_record import (
    DecisionRecord, Context, Contract, Action, Evidence,
    Uncertainty, ResidualRisk, Alternative, Decision,
    Counterfactual, create_sample_decision_record
)
from counterfactual_engine import CounterfactualEngine
from audit_metrics import AuditMetricsComputer
from explanation_generator import ExplanationGenerator


class E6Experiment:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.engine = CounterfactualEngine()
        self.metrics_computer = AuditMetricsComputer()
        self.generator = ExplanationGenerator()
    
    def create_test_records(self) -> List[DecisionRecord]:
        """Crée plusieurs DDRs pour tester"""
        records = []
        
        # Record 1 : Décision ACCEPT (medical)
        record1 = create_sample_decision_record()
        records.append(record1)
        
        # Record 2 : Décision REJECT (accuracy insuffisante)
        record2 = DecisionRecord(
            record_id="ddr_002",
            design_id="ecg_snn_2bit",
            timestamp=datetime.now().isoformat(),
            context=Context(
                context_id="ctx_medical_002",
                domain="medical",
                environment="hospital",
                safety_relevant=True,
                requirements={"latency_ms": 20.0, "accuracy": 0.95}
            ),
            contract=Contract(
                primary_objective="maximize_accuracy",
                hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.95}
            ),
            actions=[
                Action("act_003", "evidence", "eval_low_fidelity", "Évaluation initiale")
            ],
            evidence=[
                Evidence("ev_003", "accuracy", 0.920, "MEAS", 0.94, "test_set")
            ],
            uncertainty=Uncertainty(
                per_metric={"accuracy": 0.03},
                overall=0.03
            ),
            residual_risk=ResidualRisk(
                per_constraint={"accuracy_min": 0.03},
                overall=0.03,
                acceptable=False
            ),
            alternatives=[
                Alternative(
                    design_id="ecg_hybrid_8bit",
                    reason_rejected="Coût plus élevé",
                    metrics={"accuracy": 0.961}
                )
            ],
            decision=Decision(
                design_id="ecg_snn_2bit",
                decision="REJECT",
                justification="Accuracy 0.920 < 0.95 requis"
            )
        )
        # Contrefactuels pour record2
        record2.counterfactuals = [
            Counterfactual("cf_002a", "Si accuracy_min était 0.91",
                          "rejeté", "accepté", "accuracy_min: 0.95→0.91", True),
            Counterfactual("cf_002b", "Si design avait ECC",
                          "rejeté", "accepté", "has_protection: False→True", True),
            Counterfactual("cf_002c", "Si mémoire relâchée",
                          "rejeté", "toujours rejeté", "memory: 32→64", True),
        ]
        records.append(record2)
        
        # Record 3 : Décision DEFER (incertitude)
        record3 = DecisionRecord(
            record_id="ddr_003",
            design_id="vibration_hybrid_8bit",
            timestamp=datetime.now().isoformat(),
            context=Context(
                context_id="ctx_industrial_001",
                domain="industrial",
                environment="factory",
                safety_relevant=False
            ),
            contract=Contract(
                primary_objective="minimize_latency",
                hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.93}
            ),
            actions=[
                Action("act_004", "evidence", "eval_low_fidelity", "Évaluation rapide")
            ],
            evidence=[
                Evidence("ev_004", "latency", 6.8, "SUR", 0.75, "surrogate_model")
            ],
            uncertainty=Uncertainty(
                per_metric={"latency": 0.15},
                overall=0.15,
                unresolved_conflicts=["latency_conflict"]
            ),
            residual_risk=ResidualRisk(
                overall=0.10,
                acceptable=False
            ),
            decision=Decision(
                design_id="vibration_hybrid_8bit",
                decision="DEFER",
                justification="Incertitude élevée, escalade nécessaire"
            )
        )
        # Contrefactuels pour record3
        record3.counterfactuals = [
            Counterfactual("cf_003a", "Si incertitude faible",
                          "DEFER", "ACCEPT", "uncertainty: 0.15→0.03", True),
            Counterfactual("cf_003b", "Si évaluation HF dispo",
                          "DEFER", "ACCEPT", "hf: False→True", True),
            Counterfactual("cf_003c", "Si preuves contradictoires",
                          "DEFER", "Conflit", "contradictory: False→True", True),
        ]
        records.append(record3)
        
        return records
    
    def run(self) -> Dict:
        print("="*70)
        print("🚀 E6 — DESIGN DECISION RECORDS (RQ4)")
        print("="*70)
        print(f"Date: {datetime.now().isoformat()}")
        
        # 1. Créer les DDRs
        records = self.create_test_records()
        print(f"\n📋 {len(records)} DDRs créés")
        
        # 2. Analyser chaque record
        all_results = []
        
        for record in records:
            print(f"\n{'='*70}")
            print(f"📋 DDR: {record.record_id} ({record.design_id})")
            print(f"{'='*70}")
            
            # 2a. Complétude
            completeness = record.validate_completeness()
            print(f"\nComplétude: {completeness['completeness_score']:.0%}")
            print(f"Composants présents:")
            for comp, present in completeness['components_present'].items():
                status = "✅" if present else "❌"
                print(f"   {status} {comp}")
            
            # 2b. Tests contrefactuels
            cf_results = self.engine.run_all_tests(record)
            
            # 2c. Métriques d'audit
            metrics = self.metrics_computer.compute_all(record)
            metrics_dict = self.metrics_computer.to_dict(metrics)
            
            print(f"\n📊 Métriques d'audit:")
            for k, v in metrics_dict.items():
                if k != "record_id":
                    print(f"   {k}: {v:.3f}")
            
            # 2d. Explication
            explanation = self.generator.generate_concise_explanation(record)
            print(f"\n📝 Explication:")
            print(explanation)
            
            all_results.append({
                "record_id": record.record_id,
                "design_id": record.design_id,
                "completeness": completeness,
                "counterfactual_results": cf_results,
                "audit_metrics": metrics_dict
            })
        
        # 3. Résumé global
        print(f"\n{'='*70}")
        print("📊 RÉSUMÉ GLOBAL")
        print(f"{'='*70}")
        
        # Moyennes des métriques
        avg_metrics = {
            "EC": 0.0, "CT": 0.0, "DF": 0.0,
            "CF": 0.0, "AC": 0.0, "AV": 0.0, "overall": 0.0
        }
        
        for result in all_results:
            for k in avg_metrics.keys():
                avg_metrics[k] += result["audit_metrics"].get(k, 0)
        
        for k in avg_metrics.keys():
            avg_metrics[k] /= len(all_results)
        
        print("\nMétriques moyennes:")
        for k, v in avg_metrics.items():
            print(f"   {k}: {v:.3f}")
        
        # Tests contrefactuels
        total_tests = sum(r["counterfactual_results"]["tests_run"] for r in all_results)
        passed_tests = sum(r["counterfactual_results"]["tests_passed"] for r in all_results)
        
        print(f"\nTests contrefactuels: {passed_tests}/{total_tests} passés")
        
        # 4. Sauvegarder
        final = {
            "experiment": "E6", "rq": "RQ4",
            "timestamp": datetime.now().isoformat(),
            "records_count": len(records),
            "avg_metrics": {k: round(v, 3) for k, v in avg_metrics.items()},
            "counterfactual_summary": {
                "tests_run": total_tests,
                "tests_passed": passed_tests,
                "all_passed": passed_tests == total_tests
            },
            "records": all_results
        }
        
        output_path = os.path.join(self.output_dir, "e6_results.json")
        with open(output_path, 'w') as f:
            json.dump(final, f, indent=2)
        
        # Sauvegarder aussi les DDRs complets
        for record in records:
            ddr_path = os.path.join(self.output_dir, f"{record.record_id}.json")
            with open(ddr_path, 'w') as f:
                f.write(record.to_json())
        
        print(f"\n💾 Résultats: {output_path}")
        print(f"💾 DDRs: {self.output_dir}/*.json")
        
        # 5. Critères de succès
        print(f"\n{'='*70}")
        print("🎯 CRITÈRES DE SUCCÈS")
        print(f"{'='*70}")
        
        # Vérifier les critères
        has_complete_ddr = any(r["completeness"]["complete"] for r in all_results)
        cf_tests_pass = passed_tests >= 2  # Au moins 2 tests sur 3
        good_audit_score = avg_metrics["overall"] >= 0.70
        ec_high = avg_metrics["EC"] >= 0.80
        av_high = avg_metrics["AV"] >= 0.70
        
        criteria = {
            "Complete DDR exists": has_complete_ddr,
            "Counterfactual tests pass (≥2/3)": cf_tests_pass,
            "Overall audit score ≥ 0.70": good_audit_score,
            "EC (Explanation Completeness) ≥ 0.80": ec_high,
            "AV (Audit Verifiability) ≥ 0.70": av_high,
        }
        
        all_pass = all(criteria.values())
        for c, p in criteria.items():
            print(f"   {'✅ PASS' if p else '❌ FAIL'}: {c}")
        
        print(f"\n{'🎉 E6 RÉUSSI !' if all_pass else '⚠️ Certains critères échouent'}")
        
        return final


def main():
    return E6Experiment().run()


if __name__ == "__main__":
    main()
