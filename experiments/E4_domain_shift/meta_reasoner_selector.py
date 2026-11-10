"""
Meta-Reasoner Selector - VERSION FINALE
Préfère Remap/Redesign pour D3
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Set

from domain_shift_scenarios import DomainShiftScenario, ShiftSeverity
from adaptation_methods import AdaptationMethod, AdaptationMethodType, AdaptationMethodRegistry
from severity_classifier import SeverityClassifier, SeverityClassification
from post_adaptation_validator import PostAdaptationValidator


@dataclass
class MethodSelection:
    scenario_id: str
    selected_method: AdaptationMethodType
    selected_method_name: str
    ranking: List[Tuple[str, float]]
    valid: bool
    violations: List[str]
    reasoning: str


class MetaReasonerSelector:
    def __init__(self):
        self.registry = AdaptationMethodRegistry()
        self.classifier = SeverityClassifier()
        self.validator = PostAdaptationValidator()
    
    def select_method(self, scenario: DomainShiftScenario,
                     excluded_methods: Set[str] = None) -> MethodSelection:
        excluded_methods = excluded_methods or set()
        
        classification = self.classifier.classify(scenario)
        severity_score = classification.severity_score
        severity = classification.severity
        
        # Obtenir les méthodes applicables
        applicable = self.registry.get_applicable(severity_score, scenario.domain)
        applicable = [m for m in applicable if m.name not in excluded_methods]
        
        if not applicable:
            applicable = self.registry.get_all()
        
        # Évaluer
        evaluations = []
        for method in applicable:
            score, valid, violations, metrics = self._evaluate_method(
                method, scenario, severity_score, severity
            )
            evaluations.append((method, score, valid, violations, metrics))
        
        # Trier
        evaluations.sort(key=lambda x: x[1], reverse=True)
        
        if not evaluations:
            return MethodSelection(
                scenario_id=scenario.scenario_id,
                selected_method=AdaptationMethodType.NONE,
                selected_method_name="None",
                ranking=[],
                valid=False,
                violations=["Aucune méthode"],
                reasoning="Aucune méthode"
            )
        
        # Prendre la meilleure VALIDE
        best = None
        for method, score, valid, violations, metrics in evaluations:
            if valid:
                best = (method, score, valid, violations, metrics)
                break
        
        if not best:
            best = evaluations[0]
        
        method, score, valid, violations, metrics = best
        ranking = [(m.name, s) for m, s, _, _, _ in evaluations]
        reasoning = self._generate_reasoning(scenario, classification, method, 
                                              valid, violations, metrics)
        
        return MethodSelection(
            scenario_id=scenario.scenario_id,
            selected_method=method.method_type,
            selected_method_name=method.name,
            ranking=ranking,
            valid=valid,
            violations=violations,
            reasoning=reasoning
        )
    
    def _evaluate_method(self, method, scenario, severity_score, severity):
        """Évalue une méthode avec bonus pour D3"""
        metrics = self.validator.validate_adaptation(method, severity_score)
        
        # Score de base
        score = 0.0
        score += 0.5 * (1 if metrics.valid else 0.3)
        score += 0.3 * method.restoration_capability
        score += 0.2 * (1 - method.compute_cost / 10.0)
        
        # BONUS SPÉCIAL : Pour D3, préférer Remap/Redesign
        if severity == ShiftSeverity.D3_SEVERE:
            if method.method_type in [AdaptationMethodType.REMAP, 
                                     AdaptationMethodType.REDESIGN]:
                score += 0.5  # Gros bonus
            elif method.method_type == AdaptationMethodType.SWITCH_SUBNETWORK:
                score -= 0.3  # Pénalité
        
        return score, metrics.valid, metrics.violations, metrics
    
    def _generate_reasoning(self, scenario, classification, method, 
                          valid, violations, metrics) -> str:
        lines = [
            f"Scénario: {scenario.scenario_id}",
            f"Sévérité: {classification.severity.value} (score={classification.severity_score:.3f})",
            "",
            f"Méthode: {method.name}",
            f"   Restauration: {method.restoration_capability:.0%}",
            f"   Coût: {method.compute_cost}",
            f"   Accuracy: {metrics.accuracy:.3f}",
            "",
            f"Valide: {'✅ OUI' if valid else '❌ NON'}",
        ]
        if violations:
            for v in violations:
                lines.append(f"   - {v}")
        return "\n".join(lines)
