"""
Lifecycle Perturbations - VERSION CORRIGÉE
Avec impacts calibrés
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class PerturbationClass(Enum):
    C0_NOMINAL = "C0_nominal"
    C1_MINOR = "C1_minor"
    C2_MODERATE = "C2_moderate"
    C3_MAJOR = "C3_major"
    C4_STRUCTURAL = "C4_structural"


class InterventionType(Enum):
    CONTINUE = "continue"
    CALIBRATE = "calibrate"
    ADAPT = "adapt"
    REMAP = "remap"
    REDESIGN = "redesign"


@dataclass
class LifecyclePerturbation:
    perturbation_id: str
    perturbation_class: PerturbationClass
    name: str
    description: str
    accuracy_impact: float
    latency_impact: float
    memory_impact: float
    energy_impact: float
    reliability_impact: float
    duration_hours: float
    expected_intervention: str
    domain: str
    reversible: bool = True
    notes: str = ""


def get_all_perturbations() -> List[LifecyclePerturbation]:
    return [
        LifecyclePerturbation(
            perturbation_id="P0",
            perturbation_class=PerturbationClass.C0_NOMINAL,
            name="Nominal Operation",
            description="Aucune perturbation",
            accuracy_impact=0.0,
            latency_impact=0.0,
            memory_impact=0.0,
            energy_impact=0.0,
            reliability_impact=0.0,
            duration_hours=24.0,
            expected_intervention="continue",
            domain="medical"
        ),
        LifecyclePerturbation(
            perturbation_id="P1",
            perturbation_class=PerturbationClass.C1_MINOR,
            name="Minor Drift",
            description="Dérive mineure",
            accuracy_impact=0.03,
            latency_impact=0.08,
            memory_impact=0.02,
            energy_impact=0.05,
            reliability_impact=0.03,
            duration_hours=48.0,
            expected_intervention="calibrate",
            domain="medical"
        ),
        LifecyclePerturbation(
            perturbation_id="P2",
            perturbation_class=PerturbationClass.C2_MODERATE,
            name="Moderate Shift",
            description="Shift modéré",
            accuracy_impact=0.10,
            latency_impact=0.20,
            memory_impact=0.08,
            energy_impact=0.15,
            reliability_impact=0.08,
            duration_hours=72.0,
            expected_intervention="adapt",
            domain="medical"
        ),
        LifecyclePerturbation(
            perturbation_id="P3",
            perturbation_class=PerturbationClass.C3_MAJOR,
            name="Major Environmental Change",
            description="Changement majeur",
            accuracy_impact=0.20,
            latency_impact=0.40,
            memory_impact=0.25,
            energy_impact=0.30,
            reliability_impact=0.15,
            duration_hours=168.0,
            expected_intervention="remap",
            domain="medical"
        ),
        LifecyclePerturbation(
            perturbation_id="P4",
            perturbation_class=PerturbationClass.C4_STRUCTURAL,
            name="Structural Change",
            description="Changement structurel",
            accuracy_impact=0.35,
            latency_impact=0.70,
            memory_impact=0.50,
            energy_impact=0.60,
            reliability_impact=0.25,
            duration_hours=720.0,
            expected_intervention="redesign",
            domain="medical"
        ),
    ]


def apply_perturbation(base_metrics: Dict[str, float],
                      perturbation: LifecyclePerturbation) -> Dict[str, float]:
    perturbed = base_metrics.copy()
    
    if "accuracy" in perturbed:
        perturbed["accuracy"] *= (1 - perturbation.accuracy_impact)
    if "latency_ms" in perturbed:
        perturbed["latency_ms"] *= (1 + perturbation.latency_impact)
    if "memory_kb" in perturbed:
        perturbed["memory_kb"] *= (1 + perturbation.memory_impact)
    if "energy_mj" in perturbed:
        perturbed["energy_mj"] *= (1 + perturbation.energy_impact)
    if "reliability" in perturbed:
        perturbed["reliability"] *= (1 - perturbation.reliability_impact)
    
    return perturbed


class PerturbationRegistry:
    def __init__(self):
        self.perturbations = {p.perturbation_id: p for p in get_all_perturbations()}
    
    def get_by_id(self, perturbation_id: str) -> LifecyclePerturbation:
        return self.perturbations.get(perturbation_id)


if __name__ == "__main__":
    import json
    registry = PerturbationRegistry()
    print(f"✅ {len(registry.perturbations)} perturbations")
