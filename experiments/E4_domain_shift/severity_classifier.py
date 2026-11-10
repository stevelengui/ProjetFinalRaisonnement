"""
Severity Classifier - Classification du domain shift D0-D3
"""

from dataclasses import dataclass
from typing import Dict
from domain_shift_scenarios import DomainShiftScenario, ShiftSeverity


@dataclass
class SeverityClassification:
    """Résultat de la classification"""
    scenario_id: str
    severity: ShiftSeverity
    severity_score: float  # 0-1
    confidence: float
    reasoning: str


class SeverityClassifier:
    """
    Classifie la sévérité du domain shift
    
    D0 : score < 0.05
    D1 : 0.05 ≤ score < 0.25
    D2 : 0.25 ≤ score < 0.50
    D3 : score ≥ 0.50
    """
    
    def __init__(self):
        self.thresholds = {
            ShiftSeverity.D0_NOMINAL: (0.0, 0.05),
            ShiftSeverity.D1_LIGHT: (0.05, 0.25),
            ShiftSeverity.D2_MODERATE: (0.25, 0.50),
            ShiftSeverity.D3_SEVERE: (0.50, 1.0),
        }
    
    def classify(self, scenario: DomainShiftScenario) -> SeverityClassification:
        """Classifie un scénario"""
        # Score composite (moyenne pondérée)
        score = (
            scenario.data_distribution_change * 0.4 +
            scenario.noise_level_increase * 0.2 +
            scenario.sensor_drift * 0.2 +
            scenario.environmental_change * 0.2
        )
        
        # Déterminer la sévérité
        severity = self._score_to_severity(score)
        
        # Confiance (basée sur la distance aux seuils)
        min_thresh, max_thresh = self.thresholds[severity]
        if score < min_thresh + 0.05 or score > max_thresh - 0.05:
            confidence = 0.6  # Proche d'un seuil
        else:
            confidence = 0.9
        
        # Raisonnement
        reasoning = self._generate_reasoning(scenario, score, severity)
        
        return SeverityClassification(
            scenario_id=scenario.scenario_id,
            severity=severity,
            severity_score=score,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _score_to_severity(self, score: float) -> ShiftSeverity:
        """Convertit un score en sévérité"""
        for severity, (min_thresh, max_thresh) in self.thresholds.items():
            if min_thresh <= score < max_thresh:
                return severity
        return ShiftSeverity.D3_SEVERE
    
    def _generate_reasoning(self, scenario: DomainShiftScenario, 
                           score: float, severity: ShiftSeverity) -> str:
        """Génère un raisonnement textuel"""
        lines = [
            f"Score de sévérité: {score:.3f}",
            f"Sévérité classifiée: {severity.value}",
            "",
            "Facteurs contributifs:",
            f"  - Distribution: {scenario.data_distribution_change:.2f}",
            f"  - Bruit: {scenario.noise_level_increase:.2f}",
            f"  - Dérive capteur: {scenario.sensor_drift:.2f}",
            f"  - Environnement: {scenario.environmental_change:.2f}",
            "",
            f"Action recommandée: {scenario.recommended_method}"
        ]
        return "\n".join(lines)
    
    def should_act(self, classification: SeverityClassification) -> bool:
        """Détermine si une action est nécessaire"""
        return classification.severity != ShiftSeverity.D0_NOMINAL


if __name__ == "__main__":
    from domain_shift_scenarios import get_all_scenarios
    
    classifier = SeverityClassifier()
    scenarios = get_all_scenarios()
    
    print("✅ SeverityClassifier prêt\n")
    for s in scenarios:
        c = classifier.classify(s)
        print(f"{c.scenario_id}: {c.severity.value} (score={c.severity_score:.3f}, conf={c.confidence:.0%})")
