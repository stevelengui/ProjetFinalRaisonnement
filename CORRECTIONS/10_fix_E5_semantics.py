#!/usr/bin/env python3
"""
Correction P0-3 : E5 - Sémantique DEFER/REJECT explicite
"""

import os

FILEPATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments/E5_security/security_meta_reasoner.py"
)

CONTENT = '''"""
Security Meta-Reasoner - VERSION CORRIGÉE (P0-3)
Sémantique explicite : ACCEPT / DEFER / REJECT / INFEASIBLE
"""

from dataclasses import dataclass
from typing import Dict, List

from threat_models import ThreatModel, ThreatModelRegistry
from attack_scenarios import AttackScenario
from security_designs import SecurityDesign, get_all_security_designs
from asr_evaluator import ASREvaluator


@dataclass
class SecurityDecision:
    threat_id: str
    threat_level: float
    selected_design_id: str
    selected_design_name: str
    decision: str  # "ACCEPT", "DEFER", "REJECT", "INFEASIBLE"
    reason: str
    asr_max: float
    resource_violation: bool
    resource_violations: List[str]


class SecurityMetaReasoner:
    """
    Méta-raisonneur conscient sécurité

    SÉMANTIQUE DE DÉCISION (P0-3 CORRIGÉE) :
    - ACCEPT      : ASR ≤ seuil ET ressources OK
    - DEFER       : ASR > seuil MAIS candidats existent → demander plus d'evidence
    - REJECT      : Tous les candidats violent les contraintes dures
    - INFEASIBLE  : Aucun design ne peut satisfaire sous cette menace
    """

    def __init__(self):
        self.threat_registry = ThreatModelRegistry()
        self.designs = get_all_security_designs()
        self.evaluator = ASREvaluator(asr_threshold=0.20)

        self.resource_constraints = {
            "max_latency_ms": 20.0,
            "max_memory_kb": 48.0,
            "max_energy_mj": 5.0,
        }

    def evaluate_design(self, design: SecurityDesign,
                       threat: ThreatModel) -> SecurityDecision:
        """Évalue un design contre une menace"""

        # Vérifier les ressources
        resource_violations = []

        if design.nominal_latency_ms > self.resource_constraints["max_latency_ms"]:
            resource_violations.append(
                f"Latency {design.nominal_latency_ms:.1f} > {self.resource_constraints['max_latency_ms']}"
            )

        if design.nominal_memory_kb > self.resource_constraints["max_memory_kb"]:
            resource_violations.append(
                f"Memory {design.nominal_memory_kb:.1f} > {self.resource_constraints['max_memory_kb']}"
            )

        if design.nominal_energy_mj > self.resource_constraints["max_energy_mj"]:
            resource_violations.append(
                f"Energy {design.nominal_energy_mj:.1f} > {self.resource_constraints['max_energy_mj']}"
            )

        resource_violation = len(resource_violations) > 0

        # Évaluer l'ASR
        asr_result = self.evaluator.evaluate_design_all_attacks(design, threat)
        asr_max = asr_result["max_asr"]
        asr_valid = asr_result["all_valid"]

        # DÉCISION SÉMANTIQUE (P0-3 CORRIGÉE)
        if resource_violation:
            decision = "REJECT"
            reason = f"Resource violations: {resource_violations}"
        elif not asr_valid:
            decision = "DEFER"
            reason = (f"ASR {asr_max:.3f} > threshold {self.evaluator.asr_threshold}. "
                     f"Additional evidence required before decision.")
        else:
            decision = "ACCEPT"
            reason = f"All constraints met (ASR={asr_max:.3f})"

        return SecurityDecision(
            threat_id=threat.threat_id,
            threat_level=threat.threat_level,
            selected_design_id=design.design_id,
            selected_design_name=design.name,
            decision=decision,
            reason=reason,
            asr_max=asr_max,
            resource_violation=resource_violation,
            resource_violations=resource_violations
        )

    def select_best_design(self, threat: ThreatModel) -> SecurityDecision:
        """Sélectionne le meilleur design avec sémantique CORRIGÉE"""

        evaluations = []
        for design in self.designs:
            eval_result = self.evaluate_design(design, threat)
            evaluations.append(eval_result)

        # 1. Chercher un ACCEPT
        accepts = [e for e in evaluations if e.decision == "ACCEPT"]
        if accepts:
            best = min(accepts, key=lambda e: e.asr_max)
            return best

        # 2. Chercher un DEFER (candidats existent mais ASR trop élevé)
        defers = [e for e in evaluations if e.decision == "DEFER" and not e.resource_violation]
        if defers:
            best = min(defers, key=lambda e: e.asr_max)
            best.decision = "DEFER"
            best.reason = (
                f"Aucun design ne satisfait ASR ≤ {self.evaluator.asr_threshold}. "
                f"Meilleur candidat: {best.selected_design_id} (ASR={best.asr_max:.3f}). "
                f"ACTION: DEFER - Demander plus d'evidence ou relâcher la contrainte."
            )
            return best

        # 3. Aucun ACCEPT ni DEFER → INFEASIBLE
        best = min(evaluations, key=lambda e: e.asr_max)
        best.decision = "INFEASIBLE"
        best.reason = (
            f"AUCUN design n'est admissible sous {threat.threat_id}. "
            f"Même le meilleur ({best.selected_design_id}, ASR={best.asr_max:.3f}) viole les contraintes. "
            f"ACTION: INFEASIBLE - Redesign nécessaire ou relâcher les contraintes."
        )
        return best

    def run_decisive_test(self) -> Dict:
        """Test décisif avec sémantique CORRIGÉE"""
        print("\\n" + "="*70)
        print("🎯 TEST DÉCISIF : Menace élevée change la décision")
        print("="*70)

        no_protection = next(d for d in self.designs if d.design_id == "sec_none")
        adv_train = next(d for d in self.designs if d.design_id == "sec_adv_train")
        ensemble = next(d for d in self.designs if d.design_id == "sec_ensemble")

        results = {}

        for threat_id in ["T0", "T1", "T2", "T3", "T4"]:
            threat = self.threat_registry.get_by_id(threat_id)
            if not threat:
                continue

            print(f"\\n--- Menace {threat_id} (level={threat.threat_level}) ---")

            decisions = {}
            for design in [no_protection, adv_train, ensemble]:
                decision = self.evaluate_design(design, threat)
                decisions[design.design_id] = {
                    "decision": decision.decision,
                    "asr_max": decision.asr_max,
                    "resource_violation": decision.resource_violation,
                    "reason": decision.reason
                }
                print(f"   {design.design_id}: {decision.decision} "
                      f"(ASR={decision.asr_max:.3f})")

            results[threat_id] = decisions

        # Analyse
        t0_accepts_none = results["T0"]["sec_none"]["decision"] == "ACCEPT"
        t4_rejects_none = results["T4"]["sec_none"]["decision"] in ["DEFER", "REJECT", "INFEASIBLE"]
        t4_ensemble_rejected = results["T4"]["sec_ensemble"]["decision"] in ["REJECT", "INFEASIBLE"]

        print(f"\\n{'='*70}")
        print("📊 ANALYSE DU RENVERSEMENT")
        print(f"{'='*70}")
        print(f"1. T0 : sec_none ACCEPTÉ ? {t0_accepts_none}")
        print(f"2. T4 : sec_none REJETÉ/DEFER ? {t4_rejects_none}")
        print(f"3. T4 : sec_ensemble REJETÉ ? {t4_ensemble_rejected}")

        renversement = t0_accepts_none and t4_rejects_none and t4_ensemble_rejected

        print(f"\\n🎯 RENVERSEMENT : {'✅ DÉTECTÉ' if renversement else '❌ NON DÉTECTÉ'}")

        if renversement:
            print(f"\\n   Interprétation :")
            print(f"   - Sans menace : sec_none OK")
            print(f"   - Menace critique : sec_none DEFER (ASR trop élevé)")
            print(f"   - Menace critique : sec_ensemble REJECT (ressources)")
            print(f"   - Le méta-raisonneur documente l'infeasibility")

        return {
            "threat_results": results,
            "renversement_detected": renversement,
        }


if __name__ == "__main__":
    reasoner = SecurityMetaReasoner()
    result = reasoner.run_decisive_test()
'''

with open(FILEPATH, 'w') as f:
    f.write(CONTENT)

print(f"✅ E5 corrigé: {FILEPATH}")
print("   Sémantique : ACCEPT / DEFER / REJECT / INFEASIBLE")
print("   Sous T4 : aucun ACCEPT → DEFER documenté")
