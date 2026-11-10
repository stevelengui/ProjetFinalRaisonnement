import json
"""
import json
Conflict Resolver - Gestion des conflits entre preuves
Exigence : "Gestion des conflits : applicabilité → fidélité → récence → incertitude 
(pas de moyenne naïve)"
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ResolutionPriority(Enum):
    APPLICABILITY = 1  # Le plus prioritaire
    FIDELITY = 2
    RECENCY = 3
    UNCERTAINTY = 4
    AVERAGE = 5        # Le moins prioritaire


@dataclass
class Evidence:
    """Preuve pour résolution de conflit"""
    source_id: str
    value: float
    applicability: float  # 0-1 : à quel point cette preuve s'applique au contexte
    fidelity: str         # "F0" (analytic) < "F1" (surrogate) < "F2" (sim) < "F3" (measured)
    timestamp: str        # ISO timestamp
    uncertainty: float    # ± valeur
    
    def fidelity_score(self) -> int:
        return {"F0": 0, "F1": 1, "F2": 2, "F3": 3}.get(self.fidelity, 0)


class ConflictResolver:
    """
    Résout les conflits entre preuves multiples
    RÈGLE : Ne JAMAIS faire de moyenne naïve
    Ordre : applicabilité > fidélité > récence > incertitude
    """
    
    def resolve(self, evidence_list: List[Evidence], 
                conflict_detected: bool = None) -> Dict:
        """
        Résout un conflit entre plusieurs preuves
        """
        if not evidence_list:
            return {"error": "Aucune preuve fournie"}
        
        # Détection automatique de conflit
        if conflict_detected is None:
            conflict_detected = self._detect_conflict(evidence_list)
        
        if not conflict_detected:
            # Pas de conflit → prendre la meilleure par priorité
            best = self._select_best(evidence_list)
            return {
                "conflict": False,
                "resolved_value": best.value,
                "selected_source": best.source_id,
                "method": "single_best_by_priority",
                "reasoning": f"Sélectionné: {best.source_id} (fidélité {best.fidelity})"
            }
        
        # Conflit détecté → résolution par priorité
        # 1. Applicabilité
        max_applicability = max(e.applicability for e in evidence_list)
        applicable = [e for e in evidence_list if e.applicability >= max_applicability - 0.05]
        
        if len(applicable) == 1:
            chosen = applicable[0]
            return {
                "conflict": True,
                "resolved_value": chosen.value,
                "selected_source": chosen.source_id,
                "method": "applicability",
                "reasoning": f"Applicabilité {chosen.applicability:.2f} strictement supérieure"
            }
        
        # 2. Fidélité (parmi les applicables)
        max_fidelity = max(e.fidelity_score() for e in applicable)
        high_fidelity = [e for e in applicable if e.fidelity_score() == max_fidelity]
        
        if len(high_fidelity) == 1:
            chosen = high_fidelity[0]
            return {
                "conflict": True,
                "resolved_value": chosen.value,
                "selected_source": chosen.source_id,
                "method": "fidelity",
                "reasoning": f"Fidélité {chosen.fidelity} strictement supérieure"
            }
        
        # 3. Récence
        sorted_by_time = sorted(high_fidelity, key=lambda e: e.timestamp, reverse=True)
        if sorted_by_time[0].timestamp != sorted_by_time[1].timestamp:
            chosen = sorted_by_time[0]
            return {
                "conflict": True,
                "resolved_value": chosen.value,
                "selected_source": chosen.source_id,
                "method": "recency",
                "reasoning": f"Preuve plus récente: {chosen.timestamp}"
            }
        
        # 4. Incertitude (la plus faible)
        chosen = min(sorted_by_time, key=lambda e: e.uncertainty)
        return {
            "conflict": True,
            "resolved_value": chosen.value,
            "selected_source": chosen.source_id,
            "method": "uncertainty",
            "reasoning": f"Incertitude la plus faible: ±{chosen.uncertainty}"
        }
    
    def _detect_conflict(self, evidence_list: List[Evidence], 
                        threshold: float = 0.15) -> bool:
        """
        Détecte un conflit : valeurs qui diffèrent de plus de 15%
        """
        if len(evidence_list) < 2:
            return False
        
        values = [e.value for e in evidence_list]
        mean = sum(values) / len(values)
        
        if mean == 0:
            return False
        
        max_deviation = max(abs(v - mean) / abs(mean) for v in values)
        return max_deviation > threshold
    
    def _select_best(self, evidence_list: List[Evidence]) -> Evidence:
        """Sélectionne la meilleure preuve par priorité"""
        # Trier par (applicabilité, fidélité, récence, incertitude)
        sorted_ev = sorted(
            evidence_list,
            key=lambda e: (
                -e.applicability,
                -e.fidelity_score(),
                e.timestamp,  # Plus récent = plus grand timestamp
                e.uncertainty
            ),
            reverse=False
        )
        
        # Prendre le meilleur
        return max(
            evidence_list,
            key=lambda e: (
                e.applicability,
                e.fidelity_score(),
                e.timestamp,
                -e.uncertainty
            )
        )


if __name__ == "__main__":
    # Test de détection de conflit
    resolver = ConflictResolver()
    
    evidence = [
        Evidence("surrogate_model", 5.3, 0.8, "F1", "2026-01-01T10:00:00", 1.1),
        Evidence("cycle_accurate_sim", 8.2, 0.8, "F2", "2026-01-01T10:05:00", 0.3),
        Evidence("physical_measurement", 8.4, 0.9, "F3", "2026-01-01T10:10:00", 0.1),
    ]
    
    result = resolver.resolve(evidence)
    print(json.dumps(result, indent=2))
