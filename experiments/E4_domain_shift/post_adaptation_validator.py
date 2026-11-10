"""
Post-Adaptation Validator - VERSION CORRIGÉE
"""

from dataclasses import dataclass
from typing import Dict, List

from adaptation_methods import AdaptationMethod, AdaptationMethodType


@dataclass
class PostAdaptationMetrics:
    method: str
    accuracy: float
    latency_ms: float
    memory_kb: float
    energy_mj: float
    reliability: float
    security: float
    valid: bool
    violations: List[str]


class PostAdaptationValidator:
    def __init__(self):
        self.original_constraints = {
            "max_latency_ms": 20.0,
            "max_memory_kb": 32.0,
            "max_energy_mj": 3.5,
            "min_accuracy": 0.93,
            "min_reliability": 0.85,
            "min_security": 0.70,
        }
        
        self.original_metrics = {
            "accuracy": 0.961,
            "latency_ms": 8.2,
            "memory_kb": 24.0,
            "energy_mj": 2.8,
            "reliability": 0.92,
            "security": 0.75,
        }
    
    def validate_adaptation(self, method: AdaptationMethod,
                           severity_score: float,
                           restoration_achieved: float = None) -> PostAdaptationMetrics:
        """
        Valide une adaptation
        
        NOUVELLE FORMULE :
        - accuracy_before = original - (severity * max_drop)
        - accuracy_after = accuracy_before + (original - accuracy_before) * restoration
        """
        # 1. Calculer la performance DANS le nouveau domaine (avant adaptation)
        # Plus la sévérité est élevée, plus la chute est grande
        max_accuracy_drop = 0.25  # 25% max de chute
        accuracy_before = self.original_metrics["accuracy"] * (1 - severity_score * max_accuracy_drop)
        
        # 2. Appliquer la restauration
        # La restauration ramène vers l'accuracy originale
        if restoration_achieved is None:
            restoration_achieved = method.restoration_capability
        
        accuracy_after = accuracy_before + (self.original_metrics["accuracy"] - accuracy_before) * restoration_achieved
        
        # 3. Appliquer les coûts
        latency_ms = self.original_metrics["latency_ms"] * (1 + severity_score * 0.5)
        memory_kb = self.original_metrics["memory_kb"] * (1 + method.memory_overhead)
        energy_mj = self.original_metrics["energy_mj"] * (1 + severity_score * 0.3)
        reliability = self.original_metrics["reliability"] * (1 - severity_score * 0.2)
        security = self.original_metrics["security"]
        
        # Ajuster selon la méthode
        if method.method_type == AdaptationMethodType.PRECISION_CHANGE:
            memory_kb *= 0.6
            accuracy_after *= 0.95
        
        # 4. Vérifier les violations
        violations = []
        
        if latency_ms > self.original_constraints["max_latency_ms"]:
            violations.append(f"Latency {latency_ms:.1f} > {self.original_constraints['max_latency_ms']}")
        
        if memory_kb > self.original_constraints["max_memory_kb"]:
            violations.append(f"Memory {memory_kb:.1f} > {self.original_constraints['max_memory_kb']}")
        
        if energy_mj > self.original_constraints["max_energy_mj"]:
            violations.append(f"Energy {energy_mj:.1f} > {self.original_constraints['max_energy_mj']}")
        
        if accuracy_after < self.original_constraints["min_accuracy"]:
            violations.append(f"Accuracy {accuracy_after:.3f} < {self.original_constraints['min_accuracy']}")
        
        if reliability < self.original_constraints["min_reliability"]:
            violations.append(f"Reliability {reliability:.2f} < {self.original_constraints['min_reliability']}")
        
        return PostAdaptationMetrics(
            method=method.name,
            accuracy=accuracy_after,
            latency_ms=latency_ms,
            memory_kb=memory_kb,
            energy_mj=energy_mj,
            reliability=reliability,
            security=security,
            valid=len(violations) == 0,
            violations=violations
        )


if __name__ == "__main__":
    from adaptation_methods import AdaptationMethodRegistry, AdaptationMethodType
    
    validator = PostAdaptationValidator()
    registry = AdaptationMethodRegistry()
    
    print("✅ PostAdaptationValidator CORRIGÉ\n")
    
    # Tester avec différentes sévérités
    for severity in [0.0, 0.10, 0.30, 0.60]:
        print(f"\n=== Sévérité {severity} ===")
        for method_type in [AdaptationMethodType.NONE, 
                           AdaptationMethodType.RECALIBRATE,
                           AdaptationMethodType.MAML,
                           AdaptationMethodType.REMAP,
                           AdaptationMethodType.REDESIGN]:
            method = registry.get_by_type(method_type)
            result = validator.validate_adaptation(method, severity)
            print(f"   {method.name}: accuracy={result.accuracy:.3f}, valid={result.valid}")
