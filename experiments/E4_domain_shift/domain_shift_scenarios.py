"""
Domain Shift Scenarios - VERSION FINALE
DS06 calibré pour être D3_severe
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class ShiftSeverity(Enum):
    D0_NOMINAL = "D0_nominal"
    D1_LIGHT = "D1_light"
    D2_MODERATE = "D2_moderate"
    D3_SEVERE = "D3_severe"


@dataclass
class DomainShiftScenario:
    scenario_id: str
    severity: ShiftSeverity
    description: str
    data_distribution_change: float
    noise_level_increase: float
    sensor_drift: float
    environmental_change: float
    expected_accuracy_drop: float
    expected_latency_increase: float
    recommended_method: str
    design_id: str
    domain: str
    notes: str = ""


def get_all_scenarios() -> List[DomainShiftScenario]:
    return [
        # D0 : Nominal
        DomainShiftScenario(
            scenario_id="DS01", severity=ShiftSeverity.D0_NOMINAL,
            description="Aucun domain shift",
            data_distribution_change=0.0, noise_level_increase=0.0,
            sensor_drift=0.0, environmental_change=0.0,
            expected_accuracy_drop=0.0, expected_latency_increase=0.0,
            recommended_method="none",
            design_id="ecg_hybrid_8bit", domain="medical"
        ),
        
        # D1 : Léger
        DomainShiftScenario(
            scenario_id="DS02", severity=ShiftSeverity.D1_LIGHT,
            description="Dérive capteur mineure",
            data_distribution_change=0.10, noise_level_increase=0.05,
            sensor_drift=0.15, environmental_change=0.05,
            expected_accuracy_drop=0.02, expected_latency_increase=0.0,
            recommended_method="recalibrate",
            design_id="ecg_hybrid_8bit", domain="medical"
        ),
        
        # D1 : Léger (nouveau patient)
        DomainShiftScenario(
            scenario_id="DS03", severity=ShiftSeverity.D1_LIGHT,
            description="Nouveau patient léger",
            data_distribution_change=0.15, noise_level_increase=0.10,
            sensor_drift=0.10, environmental_change=0.10,
            expected_accuracy_drop=0.03, expected_latency_increase=0.0,
            recommended_method="recalibrate",
            design_id="ecg_hybrid_8bit", domain="medical"
        ),
        
        # D2 : Modéré (fine-tuning)
        DomainShiftScenario(
            scenario_id="DS04", severity=ShiftSeverity.D2_MODERATE,
            description="Nouvelle machine industrielle",
            data_distribution_change=0.30, noise_level_increase=0.20,
            sensor_drift=0.15, environmental_change=0.20,
            expected_accuracy_drop=0.06, expected_latency_increase=0.0,
            recommended_method="fine_tune",
            design_id="vibration_hybrid_8bit", domain="industrial"
        ),
        
        # D2 : Modéré (MAML)
        DomainShiftScenario(
            scenario_id="DS05", severity=ShiftSeverity.D2_MODERATE,
            description="Shift modéré nécessitant adaptation",
            data_distribution_change=0.35, noise_level_increase=0.25,
            sensor_drift=0.20, environmental_change=0.25,
            expected_accuracy_drop=0.08, expected_latency_increase=10.0,
            recommended_method="maml",
            design_id="ecg_hybrid_8bit", domain="medical"
        ),
        
        # D3 : SÉVÈRE - CORRIGÉ avec valeurs plus élevées
        DomainShiftScenario(
            scenario_id="DS06", severity=ShiftSeverity.D3_SEVERE,
            description="Shift sévère - changement structurel complet",
            # Augmenter pour atteindre score ≥ 0.50
            data_distribution_change=0.75,   # 0.75 × 0.4 = 0.30
            noise_level_increase=0.50,       # 0.50 × 0.2 = 0.10
            sensor_drift=0.40,               # 0.40 × 0.2 = 0.08
            environmental_change=0.50,       # 0.50 × 0.2 = 0.10
            # Score total = 0.58 → D3 ✅
            expected_accuracy_drop=0.20,
            expected_latency_increase=30.0,
            recommended_method="remap",
            design_id="ecg_hybrid_8bit", domain="medical",
            notes="Changement structurel nécessitant remapping"
        ),
    ]


def get_scenarios_by_severity(severity):
    return [s for s in get_all_scenarios() if s.severity == severity]


if __name__ == "__main__":
    scenarios = get_all_scenarios()
    print(f"✅ {len(scenarios)} scénarios")
    for s in scenarios:
        # Calculer le score
        score = (s.data_distribution_change * 0.4 + 
                s.noise_level_increase * 0.2 +
                s.sensor_drift * 0.2 + 
                s.environmental_change * 0.2)
        print(f"   {s.scenario_id}: {s.severity.value} (score={score:.3f})")
