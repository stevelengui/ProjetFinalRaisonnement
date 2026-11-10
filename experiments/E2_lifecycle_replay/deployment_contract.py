"""
Deployment Contract - Contrat de déploiement
Exigence : "Γ_dep = {D*, A_dep, V(D*), M, I}"
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
from datetime import datetime


@dataclass
class DeployedDesign:
    """D* - Design déployé"""
    design_id: str
    name: str
    quantization_bits: int
    model_type: str
    
    # Métriques de déploiement
    accuracy: float
    latency_ms: float
    memory_kb: float
    energy_mj: float
    
    # Protection
    has_protection: bool = False
    protection_type: str = "none"


@dataclass
class DeploymentAction:
    """A_dep - Action de déploiement"""
    action_id: str
    action_type: str  # "deploy", "configure", "calibrate"
    description: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ValidityCondition:
    """V(D*) - Condition de validité"""
    condition_id: str
    name: str
    description: str
    metric: str
    min_value: float = None
    max_value: float = None
    check_type: str = "range"  # "range", "threshold_min", "threshold_max"


@dataclass
class ExpectedMetrics:
    """M - Métriques attendues"""
    accuracy_min: float
    latency_max: float
    memory_max: float
    energy_max: float
    reliability_min: float = 0.85
    
    # Tolérance (avant dégradation)
    tolerance: Dict[str, float] = field(default_factory=dict)


@dataclass
class MissingInformation:
    """I - Informations manquantes"""
    field_name: str
    description: str
    impact: str  # "critical", "important", "minor"
    can_proceed_with_default: bool


@dataclass
class DeploymentContract:
    """
    Contrat de déploiement
    Γ_dep = {D*, A_dep, V(D*), M, I}
    """
    contract_id: str
    deployment_timestamp: str
    domain: str  # "medical", "industrial"
    
    # D* - Deployed design
    deployed_design: DeployedDesign
    
    # A_dep - Deployment actions
    deployment_actions: List[DeploymentAction] = field(default_factory=list)
    
    # V(D*) - Validity conditions
    validity_conditions: List[ValidityCondition] = field(default_factory=list)
    
    # M - Expected metrics
    expected_metrics: ExpectedMetrics = None
    
    # I - Missing information
    missing_information: List[MissingInformation] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "contract_id": self.contract_id,
            "deployment_timestamp": self.deployment_timestamp,
            "domain": self.domain,
            "D_star": asdict(self.deployed_design),
            "A_dep": [asdict(a) for a in self.deployment_actions],
            "V_D_star": [asdict(v) for v in self.validity_conditions],
            "M": asdict(self.expected_metrics) if self.expected_metrics else None,
            "I": [asdict(i) for i in self.missing_information]
        }
    
    def check_validity(self, current_metrics: Dict[str, float]) -> Dict:
        """
        Vérifie si le design est encore valide
        Retourne l'état de validité + violations
        """
        violations = []
        warnings = []
        
        for condition in self.validity_conditions:
            metric_value = current_metrics.get(condition.metric)
            
            if metric_value is None:
                warnings.append({
                    "condition": condition.condition_id,
                    "reason": f"Métrique {condition.metric} non disponible"
                })
                continue
            
            violated = False
            if condition.min_value is not None and metric_value < condition.min_value:
                violated = True
                violations.append({
                    "condition": condition.condition_id,
                    "name": condition.name,
                    "metric": condition.metric,
                    "expected": f">= {condition.min_value}",
                    "actual": metric_value
                })
            
            if condition.max_value is not None and metric_value > condition.max_value:
                violated = True
                violations.append({
                    "condition": condition.condition_id,
                    "name": condition.name,
                    "metric": condition.metric,
                    "expected": f"<= {condition.max_value}",
                    "actual": metric_value
                })
        
        is_valid = len(violations) == 0
        
        return {
            "is_valid": is_valid,
            "violations": violations,
            "warnings": warnings,
            "num_violations": len(violations)
        }


# ============================================================
# CRÉATION DE CONTRATS DE DÉPLOIEMENT
# ============================================================

def create_ecg_deployment_contract() -> DeploymentContract:
    """Crée un contrat de déploiement ECG"""
    return DeploymentContract(
        contract_id="dep_ecg_001",
        deployment_timestamp=datetime.now().isoformat(),
        domain="medical",
        deployed_design=DeployedDesign(
            design_id="ecg_hybrid_8bit",
            name="ECG Hybrid 8-bit",
            quantization_bits=8,
            model_type="hybrid",
            accuracy=0.961,
            latency_ms=8.2,
            memory_kb=24.0,
            energy_mj=2.8,
            has_protection=False,
            protection_type="none"
        ),
        deployment_actions=[
            DeploymentAction("dep_a1", "deploy", "Déploiement initial sur RV32X"),
            DeploymentAction("dep_a2", "configure", "Configuration des seuils")
        ],
        validity_conditions=[
            ValidityCondition(
                "V1", "Accuracy minimale", "L'accuracy doit rester ≥ 0.93",
                "accuracy", min_value=0.93
            ),
            ValidityCondition(
                "V2", "Latence maximale", "La latence doit rester ≤ 20ms",
                "latency_ms", max_value=20.0
            ),
            ValidityCondition(
                "V3", "Mémoire maximale", "La mémoire doit rester ≤ 32KB",
                "memory_kb", max_value=32.0
            ),
            ValidityCondition(
                "V4", "Énergie maximale", "L'énergie doit rester ≤ 4mJ",
                "energy_mj", max_value=4.0
            ),
            ValidityCondition(
                "V5", "Fiabilité minimale", "La fiabilité doit rester ≥ 0.85",
                "reliability", min_value=0.85
            )
        ],
        expected_metrics=ExpectedMetrics(
            accuracy_min=0.93,
            latency_max=20.0,
            memory_max=32.0,
            energy_max=4.0,
            reliability_min=0.85,
            tolerance={"accuracy": 0.03, "latency": 0.20, "memory": 0.10}
        ),
        missing_information=[]
    )


def create_vibration_deployment_contract() -> DeploymentContract:
    """Crée un contrat de déploiement Vibration"""
    return DeploymentContract(
        contract_id="dep_vibration_001",
        deployment_timestamp=datetime.now().isoformat(),
        domain="industrial",
        deployed_design=DeployedDesign(
            design_id="vibration_hybrid_8bit",
            name="Vibration Hybrid 8-bit",
            quantization_bits=8,
            model_type="hybrid",
            accuracy=0.958,
            latency_ms=6.8,
            memory_kb=32.0,
            energy_mj=2.2,
            has_protection=False,
            protection_type="none"
        ),
        deployment_actions=[
            DeploymentAction("dep_b1", "deploy", "Déploiement sur capteur industriel"),
            DeploymentAction("dep_b2", "configure", "Configuration des alarmes")
        ],
        validity_conditions=[
            ValidityCondition(
                "V1", "Accuracy minimale", "L'accuracy doit rester ≥ 0.92",
                "accuracy", min_value=0.92
            ),
            ValidityCondition(
                "V2", "Latence maximale", "La latence doit rester ≤ 30ms",
                "latency_ms", max_value=30.0
            ),
            ValidityCondition(
                "V3", "Mémoire maximale", "La mémoire doit rester ≤ 48KB",
                "memory_kb", max_value=48.0
            ),
            ValidityCondition(
                "V4", "Fiabilité minimale", "La fiabilité doit rester ≥ 0.88",
                "reliability", min_value=0.88
            )
        ],
        expected_metrics=ExpectedMetrics(
            accuracy_min=0.92,
            latency_max=30.0,
            memory_max=48.0,
            energy_max=4.0,
            reliability_min=0.88
        ),
        missing_information=[]
    )


if __name__ == "__main__":
    import json
    
    contract = create_ecg_deployment_contract()
    print("✅ DeploymentContract créé")
    print(f"   Contract ID: {contract.contract_id}")
    print(f"   Design: {contract.deployed_design.design_id}")
    print(f"   Conditions: {len(contract.validity_conditions)}")
    
    # Tester la validité
    current_metrics = {
        "accuracy": 0.961,
        "latency_ms": 8.2,
        "memory_kb": 24.0,
        "energy_mj": 2.8,
        "reliability": 0.92
    }
    
    validity = contract.check_validity(current_metrics)
    print(f"\n   Validité: {validity['is_valid']}")
    print(f"   Violations: {validity['num_violations']}")
