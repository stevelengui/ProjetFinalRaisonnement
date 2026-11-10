"""
Action Engine - Actions partitionnées du méta-raisonneur
Exigence : "Actions partitionnées : Evidence, Decision, Lifecycle"
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class ActionCategory(Enum):
    EVIDENCE = "evidence"
    DECISION = "decision"
    LIFECYCLE = "lifecycle"


class EvidenceAction(Enum):
    EVAL_LOW_FIDELITY = "eval_low_fidelity"
    EVAL_HIGH_FIDELITY = "eval_high_fidelity"
    FAULT_INJECTION = "fault_injection"
    DOMAIN_SHIFT_TEST = "domain_shift_test"
    SECURITY_ANALYSIS = "security_analysis"
    CROSS_VALIDATION = "cross_validation"


class DecisionAction(Enum):
    ACCEPT = "accept"
    CONDITIONAL_ACCEPT = "conditional_accept"
    REJECT = "reject"
    DEFER = "defer"


class LifecycleAction(Enum):
    MONITOR = "monitor"
    CALIBRATE = "calibrate"
    ADAPT = "adapt"
    REMAP = "remap"
    REDESIGN = "redesign"


@dataclass
class Action:
    """Une action du méta-raisonneur"""
    category: ActionCategory
    name: str
    params: Dict[str, Any]
    rationale: str
    expected_cost: float = 0.0
    expected_time_s: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "category": self.category.value,
            "name": self.name,
            "params": self.params,
            "rationale": self.rationale,
            "expected_cost": self.expected_cost,
            "expected_time_s": self.expected_time_s,
            "timestamp": self.timestamp
        }


class ActionEngine:
    """
    Moteur d'actions partitionnées
    """
    
    def __init__(self):
        self.action_log: List[Action] = []
    
    # ============================================================
    # ACTIONS EVIDENCE
    # ============================================================
    
    def eval_low_fidelity(self, design_id: str, reason: str) -> Action:
        """Évaluation rapide (surrogate)"""
        action = Action(
            category=ActionCategory.EVIDENCE,
            name=EvidenceAction.EVAL_LOW_FIDELITY.value,
            params={"design_id": design_id, "fidelity": "F1"},
            rationale=reason,
            expected_cost=0.01,
            expected_time_s=0.1
        )
        self.action_log.append(action)
        return action
    
    def eval_high_fidelity(self, design_id: str, reason: str) -> Action:
        """Évaluation haute fidélité (cycle-accurate)"""
        action = Action(
            category=ActionCategory.EVIDENCE,
            name=EvidenceAction.EVAL_HIGH_FIDELITY.value,
            params={"design_id": design_id, "fidelity": "F2"},
            rationale=reason,
            expected_cost=1.0,
            expected_time_s=10.0
        )
        self.action_log.append(action)
        return action
    
    def fault_injection(self, design_id: str, fault_model: str) -> Action:
        """Injection de fautes"""
        action = Action(
            category=ActionCategory.EVIDENCE,
            name=EvidenceAction.FAULT_INJECTION.value,
            params={"design_id": design_id, "fault_model": fault_model},
            rationale=f"Test de fiabilité: {fault_model}",
            expected_cost=2.0,
            expected_time_s=30.0
        )
        self.action_log.append(action)
        return action
    
    # ============================================================
    # ACTIONS DECISION
    # ============================================================
    
    def decide(self, decision: DecisionAction, design_id: str, 
              rationale: str, conditions: List[str] = None) -> Action:
        """Décision finale"""
        action = Action(
            category=ActionCategory.DECISION,
            name=decision.value,
            params={
                "design_id": design_id,
                "conditions": conditions or []
            },
            rationale=rationale,
            expected_cost=0.0,
            expected_time_s=0.0
        )
        self.action_log.append(action)
        return action
    
    # ============================================================
    # ACTIONS LIFECYCLE
    # ============================================================
    
    def lifecycle_action(self, action_type: LifecycleAction, 
                        deployment_id: str, rationale: str) -> Action:
        """Action de cycle de vie"""
        action = Action(
            category=ActionCategory.LIFECYCLE,
            name=action_type.value,
            params={"deployment_id": deployment_id},
            rationale=rationale
        )
        self.action_log.append(action)
        return action
    
    def get_action_history(self) -> List[Dict]:
        return [a.to_dict() for a in self.action_log]
    
    def get_summary(self) -> Dict:
        """Résumé des actions par catégorie"""
        summary = {"evidence": 0, "decision": 0, "lifecycle": 0}
        for a in self.action_log:
            summary[a.category.value] += 1
        return {
            "total_actions": len(self.action_log),
            "by_category": summary
        }
