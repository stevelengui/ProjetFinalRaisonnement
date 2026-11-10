"""
Ground Truth Contracts - Contrats de référence vérifiés manuellement
VERSION CORRIGÉE - Alignée avec la logique hiérarchique
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class ObjectiveType(Enum):
    MAXIMIZE_ACCURACY = "maximize_accuracy"
    MINIMIZE_LATENCY = "minimize_latency"
    MINIMIZE_ENERGY = "minimize_energy"
    MAXIMIZE_RELIABILITY = "maximize_reliability"
    MAXIMIZE_SECURITY = "maximize_security"
    MAXIMIZE_ROBUSTNESS = "maximize_robustness"
    REQUEST_CLARIFICATION = "request_clarification"


@dataclass
class ReferenceContract:
    context_id: str
    primary_objective: ObjectiveType
    hard_constraints: Dict[str, float] = field(default_factory=dict)
    manual_verification: str = ""
    expected_feasibility: str = "PASS"
    
    def to_dict(self) -> Dict:
        """Convertit le contrat en dictionnaire"""
        return {
            "context_id": self.context_id,
            "primary_objective": self.primary_objective.value,
            "hard_constraints": self.hard_constraints,
            "manual_verification": self.manual_verification,
            "expected_feasibility": self.expected_feasibility
        }


# ============================================================
# CONTRATS DE RÉFÉRENCE CORRIGÉS (30 CONTEXTES)
# ============================================================

REFERENCE_CONTRACTS = {
    # G1 : ECG normal
    "C01": ("maximize_accuracy", {"latency_ms_max": 20.0, "accuracy_min": 0.95}),
    "C02": ("minimize_latency",  {"latency_ms_max": 10.0, "accuracy_min": 0.95}),
    "C03": ("maximize_accuracy", {"memory_kib_max": 128.0, "accuracy_min": 0.95}),
    "C04": ("minimize_energy",   {"power_mw_max": 20.0, "accuracy_min": 0.95}),
    "C05": ("maximize_accuracy", {"accuracy_min": 0.98}),
    
    # G2 : ECG safety-relevant
    "C06": ("maximize_accuracy", {"latency_ms_max": 10.0, "accuracy_min": 0.97, "reliability_min": 0.95}),
    "C07": ("minimize_latency",  {"latency_ms_max": 5.0, "accuracy_min": 0.97, "reliability_min": 0.98}),
    "C08": ("maximize_accuracy", {"latency_ms_max": 15.0, "accuracy_min": 0.99, "reliability_min": 0.98}),
    "C09": ("minimize_energy",   {"power_mw_max": 10.0, "accuracy_min": 0.96, "reliability_min": 0.95}),
    "C10": ("maximize_security", {"accuracy_min": 0.96, "reliability_min": 0.95, "security_asr_max": 0.05}),
    
    # G3 : Vibration normal
    "C11": ("minimize_latency",  {"latency_ms_max": 50.0, "accuracy_min": 0.93}),
    "C12": ("minimize_latency",  {"latency_ms_max": 20.0, "accuracy_min": 0.93}),
    "C13": ("maximize_accuracy", {"memory_kib_max": 128.0, "accuracy_min": 0.93}),
    "C14": ("minimize_energy",   {"power_mw_max": 30.0, "accuracy_min": 0.93}),
    "C15": ("maximize_accuracy", {"accuracy_min": 0.96}),
    
    # G4 : Vibration safety-relevant
    "C16": ("maximize_accuracy", {"latency_ms_max": 30.0, "accuracy_min": 0.95, "reliability_min": 0.95}),
    "C17": ("maximize_reliability", {"latency_ms_max": 40.0, "accuracy_min": 0.95, "reliability_min": 0.95}),
    "C18": ("maximize_accuracy", {"latency_ms_max": 20.0, "accuracy_min": 0.98, "reliability_min": 0.95}),
    "C19": ("minimize_energy",   {"power_mw_max": 20.0, "accuracy_min": 0.94, "reliability_min": 0.95}),
    "C20": ("maximize_security", {"accuracy_min": 0.95, "reliability_min": 0.95, "security_asr_max": 0.05}),
    
    # G5 : Domain shift
    "C21": ("maximize_robustness", {"latency_ms_max": 20.0, "accuracy_min": 0.95, "reliability_min": 0.95}),
    "C22": ("maximize_robustness", {"latency_ms_max": 40.0, "accuracy_min": 0.94, "reliability_min": 0.95}),
    "C23": ("maximize_robustness", {"latency_ms_max": 20.0, "accuracy_min": 0.96, "reliability_min": 0.95}),
    "C24": ("maximize_robustness", {"latency_ms_max": 50.0, "accuracy_min": 0.93, "reliability_min": 0.95}),
    "C25": ("maximize_robustness", {"latency_ms_max": 25.0, "accuracy_min": 0.95, "reliability_min": 0.95}),
    
    # G6 : Information manquante
    "C26": ("request_clarification", {}),
    "C27": ("maximize_accuracy", {"latency_ms_max": 50.0, "accuracy_min": 0.93}),
    "C28": ("request_clarification", {}),
    "C29": ("maximize_accuracy", {"latency_ms_max": 50.0, "accuracy_min": 0.93}),
    "C30": ("request_clarification", {}),
}


def get_reference_contract(context_id: str) -> ReferenceContract:
    """Retourne le contrat de référence"""
    if context_id not in REFERENCE_CONTRACTS:
        return ReferenceContract(
            context_id=context_id,
            primary_objective=ObjectiveType.MAXIMIZE_ACCURACY,
            hard_constraints={},
            manual_verification=f"Défaut pour {context_id}"
        )
    
    obj_str, constraints = REFERENCE_CONTRACTS[context_id]
    return ReferenceContract(
        context_id=context_id,
        primary_objective=ObjectiveType(obj_str),
        hard_constraints=constraints,
        manual_verification=f"Vérifié manuellement pour {context_id}"
    )


def get_all_reference_contracts() -> Dict[str, ReferenceContract]:
    return {f"C{i:02d}": get_reference_contract(f"C{i:02d}") for i in range(1, 31)}


if __name__ == "__main__":
    contracts = get_all_reference_contracts()
    print(f"✅ {len(contracts)} contrats de référence")
    for ctx_id, c in contracts.items():
        print(f"   {ctx_id}: {c.primary_objective.value}")
