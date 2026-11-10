"""
State Space - Définit l'état complet du méta-raisonneur
s_t = {Γ_t, D_t, E_t, U_t, R_t, B_t, H_t}
Exigence : "État : s_t = {Γ_t, D_t, E_t, U_t, R_t, B_t, H_t}"
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

@dataclass
class DesignContract:
    """Γ_t - Contrat de conception actif"""
    context_id: str
    primary_objective: str
    hard_constraints: Dict[str, float]
    soft_constraints: Dict[str, float]
    feasibility_status: str = "UNKNOWN"  # PASS/FAIL/UNKNOWN
    version: int = 1


@dataclass
class DesignCandidate:
    """D_t - Un candidat design"""
    design_id: str
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    feasibility: str = "UNKNOWN"  # PASS/FAIL/UNKNOWN
    selected: bool = False


@dataclass
class EvidenceSet:
    """E_t - Ensemble des preuves collectées"""
    evidence_ids: List[str] = field(default_factory=list)
    by_type: Dict[str, List[str]] = field(default_factory=dict)
    coverage_score: float = 0.0  # 0-1
    
    def add(self, evidence_id: str, evidence_type: str):
        self.evidence_ids.append(evidence_id)
        if evidence_type not in self.by_type:
            self.by_type[evidence_type] = []
        self.by_type[evidence_type].append(evidence_id)
        self._update_coverage()
    
    def _update_coverage(self):
        """Met à jour le score de couverture"""
        required_types = {"latency", "memory", "accuracy"}
        if required_types.issubset(self.by_type.keys()):
            self.coverage_score = 1.0
        else:
            self.coverage_score = len(required_types & set(self.by_type.keys())) / len(required_types)


@dataclass
class UncertaintyState:
    """U_t - État d'incertitude"""
    per_metric: Dict[str, float] = field(default_factory=dict)
    overall: float = 0.0
    escalation_level: str = "none"  # none/low/medium/high
    unresolved_conflicts: List[str] = field(default_factory=list)


@dataclass
class ResidualRisk:
    """R_t - Risque résiduel"""
    per_constraint: Dict[str, float] = field(default_factory=dict)
    overall: float = 0.0
    acceptable: bool = False
    threshold: float = 0.1


@dataclass
class BudgetState:
    """B_t - Budget restant"""
    compute_budget: float = 1.0      # 0-1
    time_budget_s: float = 3600.0
    eval_budget: int = 100           # Nombre max d'évaluations
    evals_used: int = 0
    
    @property
    def evals_remaining(self) -> int:
        return self.eval_budget - self.evals_used


@dataclass
class HistoryEntry:
    """Une entrée d'historique"""
    timestamp: str
    state_hash: str
    action: str
    outcome: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaReasonerState:
    """
    État complet du méta-raisonneur
    s_t = {Γ_t, D_t, E_t, U_t, R_t, B_t, H_t}
    """
    state_id: str
    timestamp: str
    
    # Γ_t - Contract
    contract: DesignContract
    
    # D_t - Candidates
    candidates: List[DesignCandidate] = field(default_factory=list)
    
    # E_t - Evidence
    evidence: EvidenceSet = field(default_factory=EvidenceSet)
    
    # U_t - Uncertainty
    uncertainty: UncertaintyState = field(default_factory=UncertaintyState)
    
    # R_t - Residual risk
    residual_risk: ResidualRisk = field(default_factory=ResidualRisk)
    
    # B_t - Budget
    budget: BudgetState = field(default_factory=BudgetState)
    
    # H_t - History
    history: List[HistoryEntry] = field(default_factory=list)
    
    # État global
    phase: str = "INITIALIZED"  # INITIALIZED, EVIDENCE_COLLECTED, DECIDED, DEPLOYED
    decision: Optional[str] = None  # ACCEPT, CONDITIONAL_ACCEPT, REJECT, DEFER
    
    def to_dict(self) -> Dict:
        return {
            "state_id": self.state_id,
            "timestamp": self.timestamp,
            "contract": asdict(self.contract),
            "candidates": [asdict(c) for c in self.candidates],
            "evidence": asdict(self.evidence),
            "uncertainty": asdict(self.uncertainty),
            "residual_risk": asdict(self.residual_risk),
            "budget": {
                **asdict(self.budget),
                "evals_remaining": self.budget.evals_remaining
            },
            "history": [asdict(h) for h in self.history[-10:]],
            "phase": self.phase,
            "decision": self.decision
        }
    
    def add_history(self, action: str, outcome: str, details: Dict = None):
        """Ajoute une entrée d'historique"""
        import hashlib
        state_str = json.dumps(self.to_dict(), sort_keys=True)
        state_hash = hashlib.md5(state_str.encode()).hexdigest()[:8]
        
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            state_hash=state_hash,
            action=action,
            outcome=outcome,
            details=details or {}
        )
        self.history.append(entry)
