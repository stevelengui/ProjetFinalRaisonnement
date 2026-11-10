"""
Decision Record - Design Decision Record (DDR)
VERSION CORRIGÉE - Sans récursion infinie
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import hashlib


@dataclass
class Context:
    context_id: str
    domain: str
    environment: str
    safety_relevant: bool
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Contract:
    primary_objective: str
    hard_constraints: Dict[str, float] = field(default_factory=dict)
    soft_constraints: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Action:
    action_id: str
    action_type: str
    name: str
    rationale: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Evidence:
    evidence_id: str
    evidence_type: str
    value: float
    provenance: str
    confidence: float
    source: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Uncertainty:
    per_metric: Dict[str, float] = field(default_factory=dict)
    overall: float = 0.0
    unresolved_conflicts: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ResidualRisk:
    per_constraint: Dict[str, float] = field(default_factory=dict)
    overall: float = 0.0
    acceptable: bool = False
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Alternative:
    design_id: str
    reason_rejected: str
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Decision:
    design_id: str
    decision: str
    justification: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Counterfactual:
    counterfactual_id: str
    description: str
    original_outcome: str
    counterfactual_outcome: str
    changed_condition: str
    valid: bool
    
    def to_dict(self):
        return asdict(self)


@dataclass
class DecisionRecord:
    """
    Design Decision Record (DDR)
    J(D) = {C, Γ, A, E, U, R, Alt, Dec, CF}
    """
    record_id: str
    design_id: str
    timestamp: str
    
    context: Context
    contract: Contract
    actions: List[Action] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    uncertainty: Uncertainty = field(default_factory=Uncertainty)
    residual_risk: ResidualRisk = field(default_factory=ResidualRisk)
    alternatives: List[Alternative] = field(default_factory=list)
    decision: Decision = None
    counterfactuals: List[Counterfactual] = field(default_factory=list)
    
    git_commit: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.git_commit:
            self.git_commit = self._get_git_commit()
    
    def _get_git_commit(self) -> str:
        import subprocess
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=2
            )
            return result.stdout.strip()[:8]
        except:
            return "unknown"
    
    def _get_content_for_hash(self) -> Dict:
        """Contenu SANS le hash (pour éviter la récursion)"""
        return {
            "record_id": self.record_id,
            "design_id": self.design_id,
            "timestamp": self.timestamp,
            "C": self.context.to_dict() if self.context else None,
            "Gamma": self.contract.to_dict() if self.contract else None,
            "A": [a.to_dict() for a in self.actions],
            "E": [e.to_dict() for e in self.evidence],
            "U": self.uncertainty.to_dict(),
            "R": self.residual_risk.to_dict(),
            "Alt": [a.to_dict() for a in self.alternatives],
            "Dec": self.decision.to_dict() if self.decision else None,
            "CF": [c.to_dict() for c in self.counterfactuals],
            "git_commit": self.git_commit
        }
    
    def compute_hash(self) -> str:
        """Hash unique du record SANS récursion"""
        content = json.dumps(self._get_content_for_hash(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        """Version avec hash (utilise _get_content_for_hash)"""
        result = self._get_content_for_hash()
        result["hash"] = self.compute_hash()
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def validate_completeness(self) -> Dict:
        """Vérifie la complétude du DDR"""
        missing = []
        
        if not self.context:
            missing.append("C (Context)")
        if not self.contract:
            missing.append("Gamma (Contract)")
        if not self.actions:
            missing.append("A (Actions)")
        if not self.evidence:
            missing.append("E (Evidence)")
        if not self.uncertainty:
            missing.append("U (Uncertainty)")
        if not self.residual_risk:
            missing.append("R (Residual Risk)")
        if not self.decision:
            missing.append("Dec (Decision)")
        
        total_components = 9
        present = total_components - len(missing)
        
        return {
            "complete": len(missing) == 0,
            "completeness_score": present / total_components,
            "missing_components": missing,
            "components_present": {
                "C": bool(self.context),
                "Gamma": bool(self.contract),
                "A": len(self.actions) > 0,
                "E": len(self.evidence) > 0,
                "U": bool(self.uncertainty),
                "R": bool(self.residual_risk),
                "Alt": len(self.alternatives) > 0,
                "Dec": bool(self.decision),
                "CF": len(self.counterfactuals) > 0
            }
        }


def create_sample_decision_record() -> DecisionRecord:
    """Crée un DDR d'exemple pour tests"""
    record = DecisionRecord(
        record_id="ddr_001",
        design_id="ecg_hybrid_8bit",
        timestamp=datetime.now().isoformat(),
        context=Context(
            context_id="ctx_medical_001",
            domain="medical",
            environment="hospital",
            safety_relevant=True,
            requirements={"latency_ms": 20.0, "accuracy": 0.95}
        ),
        contract=Contract(
            primary_objective="maximize_accuracy",
            hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.95},
            soft_constraints={"energy_mj_max": 3.0}
        ),
        actions=[
            Action("act_001", "evidence", "eval_low_fidelity", "Évaluation initiale rapide"),
            Action("act_002", "evidence", "eval_high_fidelity", "Évaluation précise")
        ],
        evidence=[
            Evidence("ev_001", "latency", 8.2, "SIM", 0.92, "cycle_accurate_simulator"),
            Evidence("ev_002", "accuracy", 0.961, "MEAS", 0.95, "test_set_evaluation")
        ],
        uncertainty=Uncertainty(
            per_metric={"latency": 0.05, "accuracy": 0.01},
            overall=0.03
        ),
        residual_risk=ResidualRisk(
            per_constraint={"latency_ms_max": 0.02, "accuracy_min": 0.01},
            overall=0.015,
            acceptable=True
        ),
        alternatives=[
            Alternative(
                design_id="ecg_hybrid_4bit",
                reason_rejected="Latence OK mais accuracy 0.948 < 0.95",
                metrics={"latency_ms": 6.2, "accuracy": 0.948}
            ),
            Alternative(
                design_id="ecg_snn_2bit",
                reason_rejected="Accuracy 0.920 < 0.95",
                metrics={"latency_ms": 12.4, "accuracy": 0.920}
            )
        ],
        decision=Decision(
            design_id="ecg_hybrid_8bit",
            decision="ACCEPT",
            justification="Meilleur compromis: accuracy 0.961 ≥ 0.95, latency 8.2ms ≤ 20ms"
        )
    )
    
    record.counterfactuals.append(Counterfactual(
        counterfactual_id="cf_001",
        description="Si accuracy_min était 0.94",
        original_outcome="ecg_hybrid_4bit rejeté",
        counterfactual_outcome="ecg_hybrid_4bit accepté",
        changed_condition="accuracy_min: 0.95 → 0.94",
        valid=True
    ))
    
    return record


if __name__ == "__main__":
    record = create_sample_decision_record()
    print("✅ DecisionRecord créé")
    print(f"   Record ID: {record.record_id}")
    print(f"   Hash: {record.compute_hash()}")
    
    completeness = record.validate_completeness()
    print(f"\n   Completeness: {completeness['completeness_score']:.0%}")
    print(f"   Complete: {completeness['complete']}")
    
    print(f"\n{record.to_json()}")
