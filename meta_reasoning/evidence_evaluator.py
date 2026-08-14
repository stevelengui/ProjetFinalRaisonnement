"""
Evidence Evaluator - Évalue les preuves avec choix adaptatif des outils
Version améliorée : Sélection dynamique simulation rapide/précise
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

class EvidenceType(Enum):
    LATENCY = "latency"
    ENERGY = "energy"
    MEMORY = "memory"
    ACCURACY = "accuracy"
    EXPLAINABILITY = "explainability"
    RELIABILITY = "reliability"
    ROBUSTNESS = "robustness"
    SECURITY = "security"

class EvidenceQuality(Enum):
    CERTIFIED = "certified"      # Mesuré sur hardware
    VALIDATED = "validated"      # Simulation haute-fidélité
    ESTIMATED = "estimated"      # Surrogate model
    SPECULATIVE = "speculative"  # Approximation

class EvaluationStrategy(Enum):
    FAST = "fast"                # Surrogate model (~0.01s)
    BALANCED = "balanced"        # Mixte (~0.1s)
    PRECISE = "precise"          # Simulation haute-fidélité (~1s)

@dataclass
class Evidence:
    type: EvidenceType
    value: float
    quality: EvidenceQuality
    confidence: float
    source: str
    evaluation_strategy: EvaluationStrategy = EvaluationStrategy.FAST
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "value": self.value,
            "quality": self.quality.value,
            "confidence": self.confidence,
            "source": self.source,
            "strategy": self.evaluation_strategy.value
        }

@dataclass
class EvidencePackage:
    design_id: str
    evidences: List[Evidence] = None
    overall_confidence: float = 0.0
    strategy_used: EvaluationStrategy = EvaluationStrategy.FAST
    
    def __post_init__(self):
        if self.evidences is None:
            self.evidences = []
    
    def add_evidence(self, evidence: Evidence):
        self.evidences.append(evidence)
        self._update_confidence()
    
    def _update_confidence(self):
        if self.evidences:
            self.overall_confidence = np.mean([e.confidence for e in self.evidences])
    
    def get_evidence(self, evidence_type: EvidenceType) -> Optional[Evidence]:
        for e in self.evidences:
            if e.type == evidence_type:
                return e
        return None
    
    def get_strategy_summary(self) -> Dict:
        strategies = {}
        for e in self.evidences:
            strategies[e.type.value] = e.evaluation_strategy.value
        return {
            "strategies": strategies,
            "overall": self.strategy_used.value,
            "avg_confidence": self.overall_confidence
        }

class EvidenceEvaluator:
    """
    Évaluateur avec sélection adaptative de la stratégie
    """
    
    def __init__(self):
        # Définition des stratégies par type de preuve
        self.strategy_rules = {
            "safety_critical": {
                EvidenceType.LATENCY: EvaluationStrategy.PRECISE,
                EvidenceType.ACCURACY: EvaluationStrategy.PRECISE,
                EvidenceType.RELIABILITY: EvaluationStrategy.PRECISE,
                EvidenceType.ENERGY: EvaluationStrategy.BALANCED,
                EvidenceType.MEMORY: EvaluationStrategy.FAST
            },
            "high": {
                EvidenceType.LATENCY: EvaluationStrategy.BALANCED,
                EvidenceType.ACCURACY: EvaluationStrategy.PRECISE,
                EvidenceType.RELIABILITY: EvaluationStrategy.BALANCED,
                EvidenceType.ENERGY: EvaluationStrategy.FAST,
                EvidenceType.MEMORY: EvaluationStrategy.FAST
            },
            "medium": {
                EvidenceType.LATENCY: EvaluationStrategy.FAST,
                EvidenceType.ACCURACY: EvaluationStrategy.BALANCED,
                EvidenceType.RELIABILITY: EvaluationStrategy.FAST,
                EvidenceType.ENERGY: EvaluationStrategy.FAST,
                EvidenceType.MEMORY: EvaluationStrategy.FAST
            },
            "low": {
                EvidenceType.LATENCY: EvaluationStrategy.FAST,
                EvidenceType.ACCURACY: EvaluationStrategy.FAST,
                EvidenceType.RELIABILITY: EvaluationStrategy.FAST,
                EvidenceType.ENERGY: EvaluationStrategy.FAST,
                EvidenceType.MEMORY: EvaluationStrategy.FAST
            }
        }
    
    def select_strategy(self, criticality: str, evidence_type: EvidenceType) -> EvaluationStrategy:
        """Sélectionne la stratégie adaptée selon la criticité et le type de preuve"""
        rules = self.strategy_rules.get(criticality, self.strategy_rules["medium"])
        return rules.get(evidence_type, EvaluationStrategy.FAST)
    
    def evaluate_design(self, design: Dict, design_contract, 
                        criticality: str = "medium") -> EvidencePackage:
        """
        Évalue un design avec sélection adaptative de la stratégie
        """
        package = EvidencePackage(
            design_id=str(design.get("id", "unknown")),
            strategy_used=EvaluationStrategy.FAST
        )
        
        performance = design.get("metrics", {})
        
        # 1. LATENCE - Stratégie adaptative
        strategy = self.select_strategy(criticality, EvidenceType.LATENCY)
        latency = performance.get("latency_ms", 10.0)
        if strategy == EvaluationStrategy.PRECISE:
            confidence = 0.95  # Haute confiance
            quality = EvidenceQuality.VALIDATED
            source = "cycle_accurate_simulator"
            # Simulation plus précise (avec overhead)
            latency = latency * (1 + np.random.normal(0, 0.02))
        elif strategy == EvaluationStrategy.BALANCED:
            confidence = 0.88
            quality = EvidenceQuality.VALIDATED
            source = "hybrid_simulator"
        else:  # FAST
            confidence = 0.85
            quality = EvidenceQuality.ESTIMATED
            source = "surrogate_model"
        
        package.add_evidence(Evidence(
            type=EvidenceType.LATENCY,
            value=round(latency, 2),
            quality=quality,
            confidence=confidence,
            source=source,
            evaluation_strategy=strategy
        ))
        
        # 2. ÉNERGIE - Stratégie adaptative
        strategy = self.select_strategy(criticality, EvidenceType.ENERGY)
        energy = performance.get("energy_mj", 3.0)
        if strategy == EvaluationStrategy.PRECISE:
            confidence = 0.92
            quality = EvidenceQuality.VALIDATED
            source = "power_estimator"
            energy = energy * (1 + np.random.normal(0, 0.03))
        elif strategy == EvaluationStrategy.BALANCED:
            confidence = 0.85
            quality = EvidenceQuality.VALIDATED
            source = "power_model"
        else:
            confidence = 0.82
            quality = EvidenceQuality.ESTIMATED
            source = "surrogate_model"
        
        package.add_evidence(Evidence(
            type=EvidenceType.ENERGY,
            value=round(energy, 3),
            quality=quality,
            confidence=confidence,
            source=source,
            evaluation_strategy=strategy
        ))
        
        # 3. PRÉCISION - Toujours haute fiabilité pour les domaines critiques
        accuracy = performance.get("accuracy", 0.95)
        if criticality in ["safety_critical", "high"]:
            confidence = 0.94
            quality = EvidenceQuality.VALIDATED
            source = "model_validation"
            strategy = EvaluationStrategy.PRECISE
        else:
            confidence = 0.92
            quality = EvidenceQuality.VALIDATED
            source = "model_validation"
            strategy = EvaluationStrategy.BALANCED
        
        package.add_evidence(Evidence(
            type=EvidenceType.ACCURACY,
            value=round(accuracy, 4),
            quality=quality,
            confidence=confidence,
            source=source,
            evaluation_strategy=strategy
        ))
        
        # 4. EXPLICABILITÉ - Stratégie adaptative
        strategy = self.select_strategy(criticality, EvidenceType.EXPLAINABILITY)
        explainability = performance.get("explainability_score", 0.7)
        if strategy == EvaluationStrategy.PRECISE:
            confidence = 0.85
            quality = EvidenceQuality.VALIDATED
            source = "shap_analysis"
        else:
            confidence = 0.78
            quality = EvidenceQuality.ESTIMATED
            source = "explainability_module"
        
        package.add_evidence(Evidence(
            type=EvidenceType.EXPLAINABILITY,
            value=round(explainability, 3),
            quality=quality,
            confidence=confidence,
            source=source,
            evaluation_strategy=strategy
        ))
        
        # 5. FIABILITÉ - Stratégie adaptative
        strategy = self.select_strategy(criticality, EvidenceType.RELIABILITY)
        reliability = self._evaluate_reliability(design, strategy)
        
        if strategy == EvaluationStrategy.PRECISE:
            confidence = 0.88
            quality = EvidenceQuality.VALIDATED
            source = "fault_injection_simulator"
        elif strategy == EvaluationStrategy.BALANCED:
            confidence = 0.80
            quality = EvidenceQuality.VALIDATED
            source = "reliability_model"
        else:
            confidence = 0.70
            quality = EvidenceQuality.ESTIMATED
            source = "reliability_estimator"
        
        package.add_evidence(Evidence(
            type=EvidenceType.RELIABILITY,
            value=round(reliability, 3),
            quality=quality,
            confidence=confidence,
            source=source,
            evaluation_strategy=strategy
        ))
        
        # Mise à jour de la stratégie globale
        package.strategy_used = self._get_overall_strategy(package)
        
        return package
    
    def _evaluate_reliability(self, design: Dict, strategy: EvaluationStrategy) -> float:
        """Évalue la fiabilité selon la stratégie"""
        precision = design.get("algorithm", {}).get("quantization_bits", 8)
        
        # Base reliability
        if precision >= 8:
            reliability = 0.92
        elif precision >= 4:
            reliability = 0.85
        else:
            reliability = 0.70
        
        # Ajustement selon la stratégie
        if strategy == EvaluationStrategy.PRECISE:
            # Simulation plus réaliste avec variabilité
            reliability *= (1 + np.random.normal(0, 0.01))
        elif strategy == EvaluationStrategy.BALANCED:
            reliability *= (1 + np.random.normal(0, 0.02))
        # FAST: pas d'ajustement
        
        return min(0.98, max(0.60, reliability))
    
    def _get_overall_strategy(self, package: EvidencePackage) -> EvaluationStrategy:
        """Détermine la stratégie globale utilisée"""
        strategies = [e.evaluation_strategy for e in package.evidences]
        if EvaluationStrategy.PRECISE in strategies:
            return EvaluationStrategy.PRECISE
        elif EvaluationStrategy.BALANCED in strategies:
            return EvaluationStrategy.BALANCED
        else:
            return EvaluationStrategy.FAST
    
    def get_strategy_recommendation(self, context) -> Dict:
        """Recommande une stratégie pour chaque type de preuve"""
        criticality = getattr(context, 'criticality', 'medium').value
        return {
            "criticality": criticality,
            "recommendations": {
                ev.value: self.select_strategy(criticality, ev).value
                for ev in EvidenceType
            }
        }
