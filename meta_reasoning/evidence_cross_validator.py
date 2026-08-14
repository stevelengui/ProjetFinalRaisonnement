"""
Evidence Cross-Validator - Validation croisée des preuves
Vérifie la cohérence entre différentes sources d'évidence
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

class ValidationStatus(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

@dataclass
class CrossValidationResult:
    evidence_type: str
    sources: List[str]
    values: List[float]
    consistency_score: float  # 0.0 à 1.0
    status: ValidationStatus
    message: str

class EvidenceCrossValidator:
    """
    Valide la cohérence des preuves entre différentes sources
    """
    
    def __init__(self):
        self.tolerance_thresholds = {
            "latency": 0.15,      # 15% de tolérance
            "energy": 0.20,       # 20% de tolérance
            "accuracy": 0.02,     # 2% de tolérance
            "memory": 0.15,       # 15% de tolérance
            "explainability": 0.10,
            "reliability": 0.10
        }
    
    def cross_validate(self, evidence_package, alternative_sources: Dict = None) -> List[CrossValidationResult]:
        """
        Valide les preuves en les confrontant à des sources alternatives
        """
        results = []
        
        for evidence in evidence_package.evidences:
            evidence_type = evidence.type.value
            main_value = evidence.value
            main_source = evidence.source
            
            # Sources alternatives
            sources = [main_source]
            values = [main_value]
            
            # Ajouter les sources alternatives si disponibles
            if alternative_sources and evidence_type in alternative_sources:
                for alt_source, alt_value in alternative_sources[evidence_type].items():
                    sources.append(alt_source)
                    values.append(alt_value)
            
            # Calculer la cohérence
            if len(values) > 1:
                consistency = self._compute_consistency(values, evidence_type)
                status, message = self._evaluate_consistency(consistency, evidence_type)
            else:
                consistency = 1.0
                status = ValidationStatus.WARNING
                message = "Source unique - validation croisée limitée"
            
            results.append(CrossValidationResult(
                evidence_type=evidence_type,
                sources=sources,
                values=values,
                consistency_score=round(consistency, 3),
                status=status,
                message=message
            ))
        
        return results
    
    def _compute_consistency(self, values: List[float], evidence_type: str) -> float:
        """Calcule un score de cohérence entre les valeurs"""
        if len(values) <= 1:
            return 1.0
        
        # Coefficient de variation
        mean_val = np.mean(values)
        if mean_val == 0:
            return 1.0
        
        std_val = np.std(values)
        cv = std_val / mean_val
        
        # Normalisation
        consistency = max(0, 1 - cv)
        
        return consistency
    
    def _evaluate_consistency(self, consistency: float, evidence_type: str) -> tuple:
        """Évalue le score de cohérence"""
        threshold = self.tolerance_thresholds.get(evidence_type, 0.15)
        
        if consistency >= (1 - threshold):
            return ValidationStatus.PASS, "Cohérence élevée entre les sources"
        elif consistency >= (1 - 2 * threshold):
            return ValidationStatus.WARNING, "Cohérence modérée - attention"
        else:
            return ValidationStatus.FAIL, "Incohérence détectée - nécessite investigation"
    
    def generate_cross_validation_report(self, results: List[CrossValidationResult]) -> str:
        """Génère un rapport de validation croisée"""
        lines = [
            "=" * 60,
            "RAPPORT DE VALIDATION CROISÉE DES PREUVES",
            "=" * 60,
            ""
        ]
        
        for result in results:
            lines.append(f"Type: {result.evidence_type}")
            lines.append(f"  Sources: {', '.join(result.sources)}")
            lines.append(f"  Valeurs: {', '.join([str(round(v, 3)) for v in result.values])}")
            lines.append(f"  Score: {result.consistency_score:.2%}")
            lines.append(f"  Status: {result.status.value.upper()}")
            lines.append(f"  Message: {result.message}")
            lines.append("")
        
        # Synthèse
        passed = sum(1 for r in results if r.status == ValidationStatus.PASS)
        warnings = sum(1 for r in results if r.status == ValidationStatus.WARNING)
        failed = sum(1 for r in results if r.status == ValidationStatus.FAIL)
        
        lines.extend([
            "-" * 60,
            f"SYNTHÈSE: {passed} PASS, {warnings} WARNING, {failed} FAIL",
            "=" * 60
        ])
        
        return "\n".join(lines)
    
    def get_confidence_adjustment(self, results: List[CrossValidationResult]) -> float:
        """
        Calcule un ajustement de confiance basé sur la validation croisée
        """
        if not results:
            return 1.0
        
        scores = [r.consistency_score for r in results]
        avg_consistency = np.mean(scores)
        
        # Plus la cohérence est faible, plus l'ajustement est fort
        adjustment = 0.5 + 0.5 * avg_consistency
        
        return round(adjustment, 3)
