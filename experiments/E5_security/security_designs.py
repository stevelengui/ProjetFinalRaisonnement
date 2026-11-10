"""
Security Designs - VERSION CORRIGÉE (ASR DIFFÉRENTS)
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class ProtectionType(Enum):
    NONE = "none"
    INPUT_VALIDATION = "input_validation"
    ADVERSARIAL_TRAINING = "adversarial_training"
    RANDOMIZED_SMOOTHING = "randomized_smoothing"
    ENSEMBLE = "ensemble"


@dataclass
class SecurityDesign:
    design_id: str
    name: str
    description: str
    model_type: str
    quantization_bits: int
    protection_type: ProtectionType
    has_protection: bool
    nominal_accuracy: float
    nominal_latency_ms: float
    nominal_memory_kb: float
    nominal_energy_mj: float
    asr_by_attack: Dict[str, float] = field(default_factory=dict)
    protection_overhead_latency: float = 0.0
    protection_overhead_memory: float = 0.0
    protection_overhead_energy: float = 0.0
    notes: str = ""


ASR_DATA = {
    "none": {
        "A1_fgsm": 0.85, "A2_pgd": 0.92, "A3_cw": 0.95,
        "A4_backdoor": 0.98, "A5_extraction": 0.95, "A6_membership": 0.65
    },
    "input_validation": {
        "A1_fgsm": 0.75, "A2_pgd": 0.85, "A3_cw": 0.90,
        "A4_backdoor": 0.95, "A5_extraction": 0.92, "A6_membership": 0.60
    },
    "adversarial_training": {
        "A1_fgsm": 0.35, "A2_pgd": 0.55, "A3_cw": 0.65,
        "A4_backdoor": 0.85, "A5_extraction": 0.80, "A6_membership": 0.45
    },
    "randomized_smoothing": {
        "A1_fgsm": 0.15, "A2_pgd": 0.25, "A3_cw": 0.35,
        "A4_backdoor": 0.65, "A5_extraction": 0.60, "A6_membership": 0.30
    },
    "ensemble": {
        "A1_fgsm": 0.08, "A2_pgd": 0.15, "A3_cw": 0.20,
        "A4_backdoor": 0.40, "A5_extraction": 0.35, "A6_membership": 0.15
    },
}


def get_all_security_designs() -> List[SecurityDesign]:
    return [
        SecurityDesign(
            design_id="sec_none", name="No Protection",
            description="Design de base", model_type="hybrid", quantization_bits=8,
            protection_type=ProtectionType.NONE, has_protection=False,
            nominal_accuracy=0.961, nominal_latency_ms=8.2,
            nominal_memory_kb=24.0, nominal_energy_mj=2.8,
            asr_by_attack=ASR_DATA["none"],
            notes="VULNÉRABLE"
        ),
        SecurityDesign(
            design_id="sec_input_val", name="Input Validation",
            description="Validation des entrées", model_type="hybrid", quantization_bits=8,
            protection_type=ProtectionType.INPUT_VALIDATION, has_protection=True,
            nominal_accuracy=0.960, nominal_latency_ms=8.8,
            nominal_memory_kb=25.0, nominal_energy_mj=2.9,
            asr_by_attack=ASR_DATA["input_validation"],
            protection_overhead_latency=7.3,
            protection_overhead_memory=4.2,
            protection_overhead_energy=3.6,
            notes="Protection légère"
        ),
        SecurityDesign(
            design_id="sec_adv_train", name="Adversarial Training",
            description="Entraînement adversarial", model_type="hybrid", quantization_bits=8,
            protection_type=ProtectionType.ADVERSARIAL_TRAINING, has_protection=True,
            nominal_accuracy=0.955, nominal_latency_ms=9.5,
            nominal_memory_kb=27.0, nominal_energy_mj=3.1,
            asr_by_attack=ASR_DATA["adversarial_training"],
            protection_overhead_latency=15.9,
            protection_overhead_memory=12.5,
            protection_overhead_energy=10.7,
            notes="Bonne protection"
        ),
        SecurityDesign(
            design_id="sec_rand_smooth", name="Randomized Smoothing",
            description="Lissage stochastique", model_type="hybrid", quantization_bits=8,
            protection_type=ProtectionType.RANDOMIZED_SMOOTHING, has_protection=True,
            nominal_accuracy=0.948, nominal_latency_ms=12.5,
            nominal_memory_kb=32.0, nominal_energy_mj=4.2,
            asr_by_attack=ASR_DATA["randomized_smoothing"],
            protection_overhead_latency=52.4,
            protection_overhead_memory=33.3,
            protection_overhead_energy=50.0,
            notes="Protection forte"
        ),
        SecurityDesign(
            design_id="sec_ensemble", name="Ensemble",
            description="Ensemble de modèles", model_type="ensemble", quantization_bits=8,
            protection_type=ProtectionType.ENSEMBLE, has_protection=True,
            nominal_accuracy=0.965, nominal_latency_ms=25.0,
            nominal_memory_kb=72.0, nominal_energy_mj=8.5,
            asr_by_attack=ASR_DATA["ensemble"],
            protection_overhead_latency=204.9,
            protection_overhead_memory=200.0,
            protection_overhead_energy=203.6,
            notes="VIOLE ressources"
        ),
    ]


def get_design_by_id(design_id: str):
    for d in get_all_security_designs():
        if d.design_id == design_id:
            return d
    return None
