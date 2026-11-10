"""
Renversement Test - Test du renversement décisif
Version corrigée : détecte le renversement STRICT et le renversement de RANG
"""

from typing import Dict, List
from dataclasses import dataclass

from candidate_designs import CandidateDesign, get_all_candidates, get_candidate_by_id
from fault_injector import FaultInjector
from reliability_metrics import ReliabilityMetricsComputer, ReliabilityMetrics


@dataclass
class DesignDecision:
    design_id: str
    feasible_before: bool
    feasible_after: bool
    reason: str
    nominal_accuracy: float
    fault_tolerant_accuracy: float


class RenversementTest:
    """
    Teste le renversement décisif :
    
    Type 1 (STRICT) : Un design était feasible et devient infeasible
    Type 2 (RANG) : Le design "optimal" change après injection
    """
    
    def __init__(self):
        self.injector = FaultInjector()
        self.metrics_computer = ReliabilityMetricsComputer()
    
    def evaluate_design(self, design: CandidateDesign, 
                       reliability_requirement: float = 0.90) -> DesignDecision:
        """Évalue un design AVANT et APRÈS injection"""
        nominal_accuracy = design.nominal_accuracy
        nominal_feasible = nominal_accuracy >= 0.94
        
        results = self.injector.inject_n_faults(design, n_faults=200)
        metrics = self.metrics_computer.compute(design.design_id, results)
        
        fault_tolerant_accuracy = nominal_accuracy - metrics.delta_a_f_mean
        reliability_met = fault_tolerant_accuracy >= reliability_requirement
        
        feasible_after = nominal_feasible and reliability_met
        
        if not nominal_feasible:
            reason = "Nominal accuracy below threshold"
        elif not reliability_met:
            reason = f"Reliability violated: {fault_tolerant_accuracy:.3f} < {reliability_requirement}"
        else:
            reason = "All constraints met"
        
        return DesignDecision(
            design_id=design.design_id,
            feasible_before=nominal_feasible,
            feasible_after=feasible_after,
            reason=reason,
            nominal_accuracy=nominal_accuracy,
            fault_tolerant_accuracy=fault_tolerant_accuracy
        )
    
    def run_renversement(self, reliability_requirement: float = 0.90) -> Dict:
        """
        Exécute le test de renversement COMPLET
        Détecte :
        1. Renversement STRICT (feasibility change)
        2. Renversement de RANG (best design change)
        """
        print("\n" + "="*70)
        print("🎯 TEST DE RENVERSEMENT DÉCISIF")
        print("="*70)
        print(f"Contrainte de fiabilité : accuracy ≥ {reliability_requirement}")
        
        candidates = get_all_candidates()
        decisions = []
        
        for design in candidates:
            decision = self.evaluate_design(design, reliability_requirement)
            decisions.append(decision)
            
            print(f"\n📋 {design.design_id}:")
            print(f"   Accuracy nominale: {decision.nominal_accuracy:.3f}")
            print(f"   Accuracy sous fautes: {decision.fault_tolerant_accuracy:.3f}")
            print(f"   Feasible AVANT: {'✅' if decision.feasible_before else '❌'}")
            print(f"   Feasible APRÈS: {'✅' if decision.feasible_after else '❌'}")
            print(f"   Raison: {decision.reason}")
        
        # ============================================================
        # TYPE 1 : Renversement STRICT (feasibility change)
        # ============================================================
        reversed_designs = [
            d for d in decisions 
            if d.feasible_before and not d.feasible_after
        ]
        
        rescued_designs = [
            d for d in decisions 
            if not d.feasible_before and d.feasible_after
        ]
        
        strict_reversal = len(reversed_designs) > 0
        
        # ============================================================
        # TYPE 2 : Renversement de RANG (best design change)
        # ============================================================
        # Meilleur design AVANT (par accuracy nominale)
        best_before = max(decisions, key=lambda d: d.nominal_accuracy)
        
        # Meilleur design APRÈS (par accuracy sous fautes)
        best_after = max(decisions, key=lambda d: d.fault_tolerant_accuracy)
        
        rank_reversal = (best_before.design_id != best_after.design_id)
        
        # ============================================================
        # RÉSULTAT
        # ============================================================
        renversement_occurs = strict_reversal or rank_reversal
        
        # Analyse
        analysis = self._analyze_renversement(decisions, best_before, best_after,
                                              strict_reversal, rank_reversal)
        
        return {
            "reliability_requirement": reliability_requirement,
            "renversement_occurs": renversement_occurs,
            "strict_reversal": strict_reversal,
            "rank_reversal": rank_reversal,
            "reversed_designs": [d.design_id for d in reversed_designs],
            "rescued_designs": [d.design_id for d in rescued_designs],
            "best_before": best_before.design_id,
            "best_after": best_after.design_id,
            "analysis": analysis,
            "decisions": [
                {
                    "design_id": d.design_id,
                    "feasible_before": d.feasible_before,
                    "feasible_after": d.feasible_after,
                    "nominal_accuracy": d.nominal_accuracy,
                    "fault_tolerant_accuracy": d.fault_tolerant_accuracy,
                    "reason": d.reason
                }
                for d in decisions
            ]
        }
    
    def _analyze_renversement(self, decisions, best_before, best_after,
                              strict_reversal, rank_reversal) -> str:
        """Analyse textuelle du renversement"""
        lines = []
        
        lines.append("=" * 60)
        lines.append("ANALYSE DU RENVERSEMENT")
        lines.append("=" * 60)
        
        lines.append("")
        lines.append("📊 Meilleurs designs :")
        lines.append(f"   AVANT injection : {best_before.design_id} (accuracy={best_before.nominal_accuracy:.3f})")
        lines.append(f"   APRÈS injection : {best_after.design_id} (accuracy={best_after.fault_tolerant_accuracy:.3f})")
        
        lines.append("")
        if strict_reversal:
            lines.append("✅ RENVERSEMENT STRICT DÉTECTÉ")
            lines.append("   Certains designs sont devenus infeasibles après injection")
        elif rank_reversal:
            lines.append("✅ RENVERSEMENT DE RANG DÉTECTÉ")
            lines.append("   Le design optimal a CHANGÉ après injection")
            lines.append("   C'est un RENVERSEMENT DÉCISIF car :")
            lines.append(f"     - {best_before.design_id} est meilleur NOMINALEMENT")
            lines.append(f"     - {best_after.design_id} est meilleur SOUS FAUTES")
            lines.append(f"     - La décision DÉPEND du contexte de fiabilité")
        else:
            lines.append("ℹ️ Pas de renversement")
            lines.append("   Le meilleur design nominal reste le meilleur sous fautes")
        
        lines.append("")
        lines.append("🎯 IMPLICATION POUR LE MÉTA-RAISONNEUR :")
        if rank_reversal:
            lines.append(
                f"   Sans analyse de fiabilité → choisit {best_before.design_id}"
            )
            lines.append(
                f"   Avec analyse de fiabilité → choisit {best_after.design_id}"
            )
            lines.append(
                "   → La couche méta-raisonnement CHANGE la décision"
            )
        
        return "\n".join(lines)


if __name__ == "__main__":
    test = RenversementTest()
    result = test.run_renversement(reliability_requirement=0.90)
    print("\n" + "="*70)
    print("📊 RÉSULTAT")
    print("="*70)
    print(f"Renversement détecté : {result['renversement_occurs']}")
    print(f"  - Strict : {result['strict_reversal']}")
    print(f"  - Rang : {result['rank_reversal']}")
    print(f"  - Best before : {result['best_before']}")
    print(f"  - Best after : {result['best_after']}")
