"""
Ablation Configs - 10 configurations d'ablation
Exigence : "10 ablations : pas de sélection adaptive, pas d'incertitude, 
pas de provenance, contrat fixe, pas de fiabilité, pas de domain-shift, 
pas de sécurité, pas d'assurance trace, pas de validity-envelope monitoring, 
optionnel : pas d'EVI"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class AblationType(Enum):
    """Types d'ablation"""
    FULL = "full"                          # Système complet (référence)
    NO_ADAPTIVE_SELECTION = "no_adaptive"  # Pas de sélection adaptive
    NO_UNCERTAINTY = "no_uncertainty"      # Pas d'incertitude
    NO_PROVENANCE = "no_provenance"        # Pas de provenance
    FIXED_CONTRACT = "fixed_contract"      # Contrat fixe
    NO_RELIABILITY = "no_reliability"      # Pas de fiabilité
    NO_DOMAIN_SHIFT = "no_domain_shift"    # Pas de domain-shift
    NO_SECURITY = "no_security"            # Pas de sécurité
    NO_ASSURANCE_TRACE = "no_assurance"    # Pas d'assurance trace
    NO_VALIDITY_MONITORING = "no_validity" # Pas de validity-envelope
    NO_EVI = "no_evi"                      # Pas d'EVI


@dataclass
class AblationConfig:
    """Configuration d'une ablation"""
    ablation_id: str
    ablation_type: AblationType
    name: str
    description: str
    
    # Mécanismes activés
    adaptive_selection: bool = True
    uncertainty_handling: bool = True
    provenance_tracking: bool = True
    dynamic_contract: bool = True
    reliability_reasoning: bool = True
    domain_shift_reasoning: bool = True
    security_reasoning: bool = True
    assurance_trace: bool = True
    validity_monitoring: bool = True
    evi_calculation: bool = True
    
    # Impact attendu
    expected_impact: str = "none"
    expected_degradation: float = 0.0  # 0-1
    

# ============================================================
# 11 CONFIGURATIONS (FULL + 10 ABLATIONS)
# ============================================================

def get_all_ablation_configs() -> List[AblationConfig]:
    return [
        # 0. FULL (référence)
        AblationConfig(
            ablation_id="A0_FULL",
            ablation_type=AblationType.FULL,
            name="Full System",
            description="Système complet avec tous les mécanismes méta",
            expected_impact="baseline",
            expected_degradation=0.0
        ),
        
        # 1. Pas de sélection adaptive
        AblationConfig(
            ablation_id="A1_NO_ADAPTIVE",
            ablation_type=AblationType.NO_ADAPTIVE_SELECTION,
            name="No Adaptive Selection",
            description="Utilise F1 (surrogate) uniquement, jamais d'escalade",
            adaptive_selection=False,
            expected_impact="high",
            expected_degradation=0.35
        ),
        
        # 2. Pas d'incertitude
        AblationConfig(
            ablation_id="A2_NO_UNCERTAINTY",
            ablation_type=AblationType.NO_UNCERTAINTY,
            name="No Uncertainty Handling",
            description="Ignore l'incertitude des preuves",
            uncertainty_handling=False,
            expected_impact="high",
            expected_degradation=0.30
        ),
        
        # 3. Pas de provenance
        AblationConfig(
            ablation_id="A3_NO_PROVENANCE",
            ablation_type=AblationType.NO_PROVENANCE,
            name="No Provenance Tracking",
            description="Ne traque pas la provenance des preuves",
            provenance_tracking=False,
            expected_impact="medium",
            expected_degradation=0.20
        ),
        
        # 4. Contrat fixe
        AblationConfig(
            ablation_id="A4_FIXED_CONTRACT",
            ablation_type=AblationType.FIXED_CONTRACT,
            name="Fixed Contract",
            description="Utilise un contrat statique (pas d'adaptation)",
            dynamic_contract=False,
            expected_impact="high",
            expected_degradation=0.40
        ),
        
        # 5. Pas de fiabilité
        AblationConfig(
            ablation_id="A5_NO_RELIABILITY",
            ablation_type=AblationType.NO_RELIABILITY,
            name="No Reliability Reasoning",
            description="Ignore les considérations de fiabilité",
            reliability_reasoning=False,
            expected_impact="high",
            expected_degradation=0.35
        ),
        
        # 6. Pas de domain-shift
        AblationConfig(
            ablation_id="A6_NO_DOMAIN_SHIFT",
            ablation_type=AblationType.NO_DOMAIN_SHIFT,
            name="No Domain-Shift Reasoning",
            description="Ignore les changements de domaine",
            domain_shift_reasoning=False,
            expected_impact="high",
            expected_degradation=0.30
        ),
        
        # 7. Pas de sécurité
        AblationConfig(
            ablation_id="A7_NO_SECURITY",
            ablation_type=AblationType.NO_SECURITY,
            name="No Security Reasoning",
            description="Ignore les menaces de sécurité",
            security_reasoning=False,
            expected_impact="high",
            expected_degradation=0.35
        ),
        
        # 8. Pas d'assurance trace
        AblationConfig(
            ablation_id="A8_NO_ASSURANCE",
            ablation_type=AblationType.NO_ASSURANCE_TRACE,
            name="No Assurance Trace",
            description="Pas de trace d'assurance pour audit",
            assurance_trace=False,
            expected_impact="medium",
            expected_degradation=0.25
        ),
        
        # 9. Pas de validity-envelope monitoring
        AblationConfig(
            ablation_id="A9_NO_VALIDITY",
            ablation_type=AblationType.NO_VALIDITY_MONITORING,
            name="No Validity Monitoring",
            description="Pas de surveillance de l'enveloppe de validité",
            validity_monitoring=False,
            expected_impact="medium",
            expected_degradation=0.20
        ),
        
        # 10. Pas d'EVI
        AblationConfig(
            ablation_id="A10_NO_EVI",
            ablation_type=AblationType.NO_EVI,
            name="No EVI Calculation",
            description="Pas de calcul d'EVI pour l'escalade",
            evi_calculation=False,
            expected_impact="medium",
            expected_degradation=0.15
        ),
    ]


def get_ablation_by_id(ablation_id: str) -> AblationConfig:
    for config in get_all_ablation_configs():
        if config.ablation_id == ablation_id:
            return config
    return None


if __name__ == "__main__":
    configs = get_all_ablation_configs()
    print(f"✅ {len(configs)} configurations d'ablation")
    for c in configs:
        print(f"\n{c.ablation_id}: {c.name}")
        print(f"   {c.description}")
        print(f"   Impact attendu: {c.expected_impact} "
              f"(dégradation: {c.expected_degradation:.0%})")
