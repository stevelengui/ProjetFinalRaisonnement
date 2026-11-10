"""
Decision Consequence Validator - Validation de conséquence décisionnelle
Exigence : "Même workload sous criticité faible vs safety-relevant → la fiabilité 
passe de préférence à contrainte dure"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from scenarios import Context


@dataclass
class DecisionConsequence:
    """Conséquence d'une décision sur le contrat"""
    context_id: str
    factor_changed: str
    original_contract: Dict
    new_contract: Dict
    decision_changed: bool
    change_type: str  # "preference_to_hard", "hard_to_preference", "new_constraint", "removed_constraint"
    impact: str  # "high", "medium", "low"


class DecisionConsequenceValidator:
    """
    Valide que les changements de contexte ont des CONSÉQUENCES DÉCISIONNELLES
    Un vrai méta-raisonneur change ses décisions quand le contexte change
    """
    
    def __init__(self):
        self.consequences: List[DecisionConsequence] = []
    
    def compare_contexts(self, base_context: Context, 
                        perturbed_context: Context) -> DecisionConsequence:
        """
        Compare deux contextes et détermine si la décision change
        """
        # Simuler le contrat pour chaque contexte
        base_contract = self._simulate_contract(base_context)
        new_contract = self._simulate_contract(perturbed_context)
        
        # Détecter les changements
        decision_changed = self._decisions_differ(base_contract, new_contract)
        change_type, impact = self._classify_change(base_contract, new_contract)
        
        # Identififier le facteur changé
        factor = self._find_changed_factor(base_context, perturbed_context)
        
        consequence = DecisionConsequence(
            context_id=perturbed_context.context_id,
            factor_changed=factor,
            original_contract=base_contract,
            new_contract=new_contract,
            decision_changed=decision_changed,
            change_type=change_type,
            impact=impact
        )
        
        self.consequences.append(consequence)
        return consequence
    
    def validate_reliability_transition(self, low_risk: Context, 
                                       high_risk: Context) -> Dict:
        """
        Test spécifique : la fiabilité doit passer de PRÉFÉRENCE à CONTRAINTE DURE
        """
        low_contract = self._simulate_contract(low_risk)
        high_contract = self._simulate_contract(high_risk)
        
        reliability_in_low = (
            "reliability_min" in low_contract.get("hard_constraints", {})
        )
        reliability_in_high = (
            "reliability_min" in high_contract.get("hard_constraints", {})
        )
        
        transition_valid = (not reliability_in_low) and reliability_in_high
        
        return {
            "test": "reliability_preference_to_hard",
            "low_risk_context": low_risk.context_id,
            "high_risk_context": high_risk.context_id,
            "reliability_in_low_constraints": reliability_in_low,
            "reliability_in_high_constraints": reliability_in_high,
            "transition_valid": transition_valid,
            "expected": "False → True",
            "actual": f"{reliability_in_low} → {reliability_in_high}",
            "status": "PASS" if transition_valid else "FAIL"
        }
    
    def _simulate_contract(self, context: Context) -> Dict:
        """
        Simule la génération de contrat pour un contexte
        (Version simplifiée pour E0, utilise la même logique que le contrôleur)
        """
        hard_constraints = {}
        preferences = {}
        
        # Contraintes dures
        if context.max_latency_ms is not None:
            hard_constraints["latency_ms_max"] = context.max_latency_ms
        if context.max_memory_kb is not None:
            hard_constraints["memory_kib_max"] = context.max_memory_kb
        if context.max_power_mw is not None:
            hard_constraints["power_mw_max"] = context.max_power_mw
        if context.min_accuracy is not None:
            hard_constraints["accuracy_min"] = context.min_accuracy
        
        # Safety → reliability devient HARD
        if context.safety_relevant or context.reliability_required:
            hard_constraints["reliability_min"] = 0.95
        else:
            preferences["reliability_preference"] = 0.7
        
        # Security → security devient HARD
        if context.security_required and context.threat_context in ["medium", "high"]:
            hard_constraints["security_asr_max"] = 0.05
        
        # Objectif principal
        if context.safety_relevant:
            primary = "maximize_reliability"
        elif context.security_required and context.threat_context == "high":
            primary = "maximize_security"
        elif context.max_latency_ms and context.max_latency_ms < 15:
            primary = "minimize_latency"
        elif context.max_power_mw and context.max_power_mw < 30:
            primary = "minimize_energy"
        else:
            primary = "maximize_accuracy"
        
        return {
            "primary_objective": primary,
            "hard_constraints": hard_constraints,
            "preferences": preferences,
            "clarification_required": bool(context.missing_info)
        }
    
    def _decisions_differ(self, c1: Dict, c2: Dict) -> bool:
        """Détermine si les décisions diffèrent"""
        if c1["primary_objective"] != c2["primary_objective"]:
            return True
        if set(c1["hard_constraints"].keys()) != set(c2["hard_constraints"].keys()):
            return True
        return False
    
    def _classify_change(self, c1: Dict, c2: Dict) -> Tuple[str, str]:
        """Classifie le type de changement"""
        h1 = set(c1["hard_constraints"].keys())
        h2 = set(c2["hard_constraints"].keys())
        
        if h2 - h1:
            change_type = "new_constraint"
            impact = "high"
        elif h1 - h2:
            change_type = "removed_constraint"
            impact = "high"
        elif c1["primary_objective"] != c2["primary_objective"]:
            change_type = "objective_change"
            impact = "high"
        else:
            change_type = "no_change"
            impact = "none"
        
        # Détecter la transition preference → hard spécifiquement
        for constraint in (h2 - h1):
            if "reliability" in constraint:
                change_type = "preference_to_hard"
            if "security" in constraint:
                change_type = "preference_to_hard"
        
        return change_type, impact
    
    def _find_changed_factor(self, base: Context, perturbed: Context) -> str:
        """Trouve quel facteur a changé"""
        factors = [
            ("max_latency_ms", base.max_latency_ms, perturbed.max_latency_ms),
            ("max_memory_kb", base.max_memory_kb, perturbed.max_memory_kb),
            ("max_power_mw", base.max_power_mw, perturbed.max_power_mw),
            ("min_accuracy", base.min_accuracy, perturbed.min_accuracy),
            ("safety_relevant", base.safety_relevant, perturbed.safety_relevant),
            ("reliability_required", base.reliability_required, perturbed.reliability_required),
            ("security_required", base.security_required, perturbed.security_required),
            ("threat_context", base.threat_context, perturbed.threat_context),
            ("domain_shift_expected", base.domain_shift_expected, perturbed.domain_shift_expected),
        ]
        
        for name, v1, v2 in factors:
            if v1 != v2:
                return name
        
        return "unknown"
    
    def get_summary(self) -> Dict:
        """Résumé des conséquences"""
        if not self.consequences:
            return {"total": 0}
        
        changed = [c for c in self.consequences if c.decision_changed]
        by_type = {}
        for c in self.consequences:
            by_type[c.change_type] = by_type.get(c.change_type, 0) + 1
        
        return {
            "total_comparisons": len(self.consequences),
            "decision_changes": len(changed),
            "change_rate": len(changed) / len(self.consequences),
            "by_change_type": by_type,
            "high_impact": len([c for c in self.consequences if c.impact == "high"])
        }


if __name__ == "__main__":
    from scenarios import get_all_scenarios
    from perturbation_engine import PerturbationEngine
    
    scenarios = get_all_scenarios()
    validator = DecisionConsequenceValidator()
    engine = PerturbationEngine()
    
    # Test 1 : Comparaison contexte normal vs safety-relevant
    print("=" * 60)
    print("TEST 1 : Fiabilité préférence → contrainte dure")
    print("=" * 60)
    
    base = scenarios[0]  # C01 (normal)
    safety = scenarios[5]  # C06 (safety)
    
    result = validator.validate_reliability_transition(base, safety)
    print(f"\n{result['test']}")
    print(f"  {result['low_risk_context']}: reliability in hard constraints = {result['reliability_in_low_constraints']}")
    print(f"  {result['high_risk_context']}: reliability in hard constraints = {result['reliability_in_high_constraints']}")
    print(f"  Expected: {result['expected']}")
    print(f"  Actual: {result['actual']}")
    print(f"  Status: {result['status']}")
    
    # Test 2 : Comparaison contexte normal vs perturbé
    print("\n" + "=" * 60)
    print("TEST 2 : Conséquences décisionnelles de perturbations")
    print("=" * 60)
    
    for factor in ["max_latency_ms", "max_power_mw", "safety_relevant"]:
        pert = engine.perturb_single_factor(base, factor, "severe")
        consequence = validator.compare_contexts(base, pert)
        print(f"\n{consequence.context_id}")
        print(f"  Facteur: {consequence.factor_changed}")
        print(f"  Décision changée: {consequence.decision_changed}")
        print(f"  Type: {consequence.change_type}")
        print(f"  Impact: {consequence.impact}")
    
    print(f"\n📊 Résumé: {validator.get_summary()}")
