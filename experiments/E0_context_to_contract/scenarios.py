"""
Scenarios - 30 contextes contrôlés pour E0
Chaque contexte est un cas d'usage réel avec des contraintes spécifiques

Structure : 
- C = contexte applicatif
- Le contexte doit être transformé en contrat Γ = {O, H, P, A, R, V}
  O = Objectives (objectif principal)
  H = Hard constraints (contraintes dures)
  P = Preferences (préférences)
  A = Assumptions (hypothèses)
  R = Risk (risques identifiés)
  V = Validity conditions (conditions de validité)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class Context:
    """Un contexte applicatif contrôlé"""
    context_id: str
    description: str
    domain: str  # "medical" ou "industrial"
    
    # Contraintes
    max_latency_ms: Optional[float] = None
    max_memory_kb: Optional[float] = None
    max_power_mw: Optional[float] = None
    min_accuracy: Optional[float] = None
    
    # Criticité
    safety_relevant: bool = False
    reliability_required: bool = False
    security_required: bool = False
    
    # Environnement
    environment: str = "production"
    domain_shift_expected: bool = False
    threat_context: str = "none"  # none, low, medium, high
    
    # Information manquante
    missing_info: List[str] = field(default_factory=list)
    
    # Métadonnées
    expected_decision_change: bool = False
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "context_id": self.context_id,
            "description": self.description,
            "domain": self.domain,
            "max_latency_ms": self.max_latency_ms,
            "max_memory_kb": self.max_memory_kb,
            "max_power_mw": self.max_power_mw,
            "min_accuracy": self.min_accuracy,
            "safety_relevant": self.safety_relevant,
            "reliability_required": self.reliability_required,
            "security_required": self.security_required,
            "environment": self.environment,
            "domain_shift_expected": self.domain_shift_expected,
            "threat_context": self.threat_context,
            "missing_info": self.missing_info,
            "notes": self.notes
        }


# ============================================================
# 30 SCÉNARIOS CONTRÔLÉS
# ============================================================

def get_all_scenarios() -> List[Context]:
    """Retourne les 30 scénarios contrôlés"""
    
    scenarios = [
        # ========== GROUPE 1 : ECG — Contraintes normales (C01-C05) ==========
        Context(
            context_id="C01",
            description="ECG standard monitoring — contraintes normales",
            domain="medical",
            max_latency_ms=20.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.95,
            safety_relevant=False,
            reliability_required=False,
            environment="hospital",
            notes="Cas de référence"
        ),
        Context(
            context_id="C02",
            description="ECG standard monitoring — latence stricte",
            domain="medical",
            max_latency_ms=10.0,  # ← Perturbation latence
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.95,
            safety_relevant=False,
            environment="hospital",
            notes="Test : latence critique"
        ),
        Context(
            context_id="C03",
            description="ECG standard monitoring — mémoire stricte",
            domain="medical",
            max_latency_ms=20.0,
            max_memory_kb=128.0,  # ← Perturbation mémoire
            max_power_mw=50.0,
            min_accuracy=0.95,
            safety_relevant=False,
            environment="hospital",
            notes="Test : mémoire critique"
        ),
        Context(
            context_id="C04",
            description="ECG standard monitoring — puissance stricte",
            domain="medical",
            max_latency_ms=20.0,
            max_memory_kb=512.0,
            max_power_mw=20.0,  # ← Perturbation puissance
            min_accuracy=0.95,
            safety_relevant=False,
            environment="hospital",
            notes="Test : puissance critique"
        ),
        Context(
            context_id="C05",
            description="ECG standard monitoring — précision stricte",
            domain="medical",
            max_latency_ms=20.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.98,  # ← Perturbation précision
            safety_relevant=False,
            environment="hospital",
            notes="Test : précision critique"
        ),
        
        # ========== GROUPE 2 : ECG — Safety-relevant (C06-C10) ==========
        Context(
            context_id="C06",
            description="ECG unité de soins intensifs — safety-relevant",
            domain="medical",
            max_latency_ms=10.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.97,
            safety_relevant=True,  # ← Fiabilité devient contrainte dure
            reliability_required=True,
            environment="ICU",
            notes="Cas critique : fiabilité contrainte dure"
        ),
        Context(
            context_id="C07",
            description="ECG chirurgie — safety-relevant + latence ultra-stricte",
            domain="medical",
            max_latency_ms=5.0,  # ← Très stricte
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.97,
            safety_relevant=True,
            reliability_required=True,
            environment="operating_room",
            notes="Cas critique : temps réel strict"
        ),
        Context(
            context_id="C08",
            description="ECG néonatal — safety-relevant + précision extrême",
            domain="medical",
            max_latency_ms=15.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.99,  # ← Très stricte
            safety_relevant=True,
            reliability_required=True,
            environment="NICU",
            notes="Cas critique : précision vitale"
        ),
        Context(
            context_id="C09",
            description="ECG ambulatoire — safety-relevant + puissance limitée",
            domain="medical",
            max_latency_ms=30.0,
            max_memory_kb=256.0,
            max_power_mw=10.0,  # ← Très stricte
            min_accuracy=0.96,
            safety_relevant=True,
            reliability_required=True,
            environment="wearable",
            notes="Cas critique : batterie limitée"
        ),
        Context(
            context_id="C10",
            description="ECG télémédecine — safety-relevant + sécurité requise",
            domain="medical",
            max_latency_ms=50.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.96,
            safety_relevant=True,
            reliability_required=True,
            security_required=True,  # ← Sécurité requise
            environment="telemedicine",
            threat_context="medium",
            notes="Cas critique : transmission sécurisée"
        ),
        
        # ========== GROUPE 3 : Vibration — Contraintes normales (C11-C15) ==========
        Context(
            context_id="C11",
            description="Vibration maintenance prédictive — contraintes normales",
            domain="industrial",
            max_latency_ms=50.0,
            max_memory_kb=512.0,
            max_power_mw=100.0,
            min_accuracy=0.93,
            safety_relevant=False,
            environment="factory",
            notes="Cas de référence industriel"
        ),
        Context(
            context_id="C12",
            description="Vibration maintenance prédictive — latence stricte",
            domain="industrial",
            max_latency_ms=20.0,  # ← Perturbation latence
            max_memory_kb=512.0,
            max_power_mw=100.0,
            min_accuracy=0.93,
            safety_relevant=False,
            environment="factory",
            notes="Test : latence critique industrielle"
        ),
        Context(
            context_id="C13",
            description="Vibration maintenance prédictive — mémoire stricte",
            domain="industrial",
            max_latency_ms=50.0,
            max_memory_kb=128.0,  # ← Perturbation mémoire
            max_power_mw=100.0,
            min_accuracy=0.93,
            safety_relevant=False,
            environment="factory",
            notes="Test : mémoire critique"
        ),
        Context(
            context_id="C14",
            description="Vibration maintenance prédictive — puissance stricte",
            domain="industrial",
            max_latency_ms=50.0,
            max_memory_kb=512.0,
            max_power_mw=30.0,  # ← Perturbation puissance
            min_accuracy=0.93,
            safety_relevant=False,
            environment="factory",
            notes="Test : puissance critique"
        ),
        Context(
            context_id="C15",
            description="Vibration maintenance prédictive — précision stricte",
            domain="industrial",
            max_latency_ms=50.0,
            max_memory_kb=512.0,
            max_power_mw=100.0,
            min_accuracy=0.96,  # ← Perturbation précision
            safety_relevant=False,
            environment="factory",
            notes="Test : précision critique"
        ),
        
        # ========== GROUPE 4 : Vibration — Safety-relevant (C16-C20) ==========
        Context(
            context_id="C16",
            description="Vibration turbine — safety-relevant",
            domain="industrial",
            max_latency_ms=30.0,
            max_memory_kb=512.0,
            max_power_mw=100.0,
            min_accuracy=0.95,
            safety_relevant=True,
            reliability_required=True,
            environment="power_plant",
            notes="Cas critique : turbine haute énergie"
        ),
        Context(
            context_id="C17",
            description="Vibration pipeline — safety-relevant + environnement hostile",
            domain="industrial",
            max_latency_ms=40.0,
            max_memory_kb=256.0,
            max_power_mw=80.0,
            min_accuracy=0.95,
            safety_relevant=True,
            reliability_required=True,
            environment="harsh",
            notes="Cas critique : environnement extrême"
        ),
        Context(
            context_id="C18",
            description="Vibration aérospatiale — safety-relevant + précision extrême",
            domain="industrial",
            max_latency_ms=20.0,
            max_memory_kb=512.0,
            max_power_mw=100.0,
            min_accuracy=0.98,
            safety_relevant=True,
            reliability_required=True,
            environment="aerospace",
            notes="Cas critique : certification requise"
        ),
        Context(
            context_id="C19",
            description="Vibration site isolé — safety-relevant + puissance limitée",
            domain="industrial",
            max_latency_ms=60.0,
            max_memory_kb=256.0,
            max_power_mw=20.0,
            min_accuracy=0.94,
            safety_relevant=True,
            reliability_required=True,
            environment="remote",
            notes="Cas critique : énergie solaire"
        ),
        Context(
            context_id="C20",
            description="Vibration SCADA — safety-relevant + sécurité requise",
            domain="industrial",
            max_latency_ms=40.0,
            max_memory_kb=512.0,
            max_power_mw=100.0,
            min_accuracy=0.95,
            safety_relevant=True,
            reliability_required=True,
            security_required=True,
            environment="SCADA",
            threat_context="high",
            notes="Cas critique : infrastructure critique"
        ),
        
        # ========== GROUPE 5 : Domain shift (C21-C25) ==========
        Context(
            context_id="C21",
            description="ECG — nouveau patient, domain shift attendu",
            domain="medical",
            max_latency_ms=20.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.95,
            safety_relevant=True,
            reliability_required=True,
            environment="hospital_new",
            domain_shift_expected=True,
            notes="Test : domain shift médical"
        ),
        Context(
            context_id="C22",
            description="Vibration — nouvelle machine, domain shift attendu",
            domain="industrial",
            max_latency_ms=40.0,
            max_memory_kb=512.0,
            max_power_mw=100.0,
            min_accuracy=0.94,
            safety_relevant=True,
            reliability_required=True,
            environment="factory_new_machine",
            domain_shift_expected=True,
            notes="Test : domain shift industriel"
        ),
        Context(
            context_id="C23",
            description="ECG — conditions environnementales changeantes",
            domain="medical",
            max_latency_ms=20.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.96,
            safety_relevant=True,
            reliability_required=True,
            environment="field_hospital",
            domain_shift_expected=True,
            notes="Test : drift environnemental"
        ),
        Context(
            context_id="C24",
            description="Vibration — saisonnalité industrielle",
            domain="industrial",
            max_latency_ms=50.0,
            max_memory_kb=512.0,
            max_power_mw=100.0,
            min_accuracy=0.93,
            safety_relevant=True,
            reliability_required=True,
            environment="factory_seasonal",
            domain_shift_expected=True,
            notes="Test : drift saisonnier"
        ),
        Context(
            context_id="C25",
            description="ECG — changement de capteur",
            domain="medical",
            max_latency_ms=25.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.95,
            safety_relevant=True,
            reliability_required=True,
            environment="hospital",
            domain_shift_expected=True,
            notes="Test : drift capteur"
        ),
        
        # ========== GROUPE 6 : Information manquante (C26-C30) ==========
        Context(
            context_id="C26",
            description="ECG — budget latence non spécifié",
            domain="medical",
            max_latency_ms=None,  # ← MANQUANT
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.95,
            safety_relevant=True,
            reliability_required=True,
            environment="hospital",
            missing_info=["max_latency_ms"],
            notes="Test : REQUEST CLARIFICATION attendu"
        ),
        Context(
            context_id="C27",
            description="Vibration — budget puissance non spécifié",
            domain="industrial",
            max_latency_ms=50.0,
            max_memory_kb=512.0,
            max_power_mw=None,  # ← MANQUANT
            min_accuracy=0.93,
            safety_relevant=False,
            environment="factory",
            missing_info=["max_power_mw"],
            notes="Test : REQUEST CLARIFICATION attendu"
        ),
        Context(
            context_id="C28",
            description="ECG — précision minimale non spécifiée",
            domain="medical",
            max_latency_ms=20.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=None,  # ← MANQUANT
            safety_relevant=True,
            reliability_required=True,
            environment="hospital",
            missing_info=["min_accuracy"],
            notes="Test : critique, doit demander clarification"
        ),
        Context(
            context_id="C29",
            description="Vibration — mémoire et puissance non spécifiés",
            domain="industrial",
            max_latency_ms=50.0,
            max_memory_kb=None,  # ← MANQUANT
            max_power_mw=None,   # ← MANQUANT
            min_accuracy=0.93,
            safety_relevant=False,
            environment="factory",
            missing_info=["max_memory_kb", "max_power_mw"],
            notes="Test : 2 informations manquantes"
        ),
        Context(
            context_id="C30",
            description="ECG — contexte de menace non spécifié",
            domain="medical",
            max_latency_ms=20.0,
            max_memory_kb=512.0,
            max_power_mw=50.0,
            min_accuracy=0.95,
            safety_relevant=True,
            reliability_required=True,
            security_required=True,
            environment="telemedicine",
            threat_context="unknown",  # ← Non spécifié
            missing_info=["threat_context"],
            notes="Test : clarification sécurité"
        ),
    ]
    
    return scenarios


def get_scenarios_by_group() -> Dict[str, List[Context]]:
    """Retourne les scénarios groupés"""
    all_scenarios = get_all_scenarios()
    
    groups = {
        "ecg_normal": [s for s in all_scenarios if s.domain == "medical" and not s.safety_relevant],
        "ecg_safety": [s for s in all_scenarios if s.domain == "medical" and s.safety_relevant and not s.domain_shift_expected],
        "vibration_normal": [s for s in all_scenarios if s.domain == "industrial" and not s.safety_relevant],
        "vibration_safety": [s for s in all_scenarios if s.domain == "industrial" and s.safety_relevant and not s.domain_shift_expected],
        "domain_shift": [s for s in all_scenarios if s.domain_shift_expected],
        "missing_info": [s for s in all_scenarios if s.missing_info],
    }
    
    return groups


if __name__ == "__main__":
    scenarios = get_all_scenarios()
    print(f"✅ {len(scenarios)} scénarios chargés")
    
    groups = get_scenarios_by_group()
    print("\n📊 Répartition par groupe:")
    for group_name, group_scenarios in groups.items():
        print(f"   {group_name}: {len(group_scenarios)} scénarios")
    
    print("\n📋 IDs des scénarios:")
    for s in scenarios:
        print(f"   {s.context_id}: {s.description}")
