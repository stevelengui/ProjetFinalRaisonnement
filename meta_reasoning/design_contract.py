"""
Design Contract - Définit les objectifs de conception
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

class DesignObjective(Enum):
    MINIMIZE_LATENCY = "minimize_latency"
    MINIMIZE_ENERGY = "minimize_energy"
    MINIMIZE_MEMORY = "minimize_memory"
    MAXIMIZE_ACCURACY = "maximize_accuracy"
    MAXIMIZE_EXPLAINABILITY = "maximize_explainability"
    MAXIMIZE_ROBUSTNESS = "maximize_robustness"

class ConstraintType(Enum):
    HARD = "hard"
    SOFT = "soft"

@dataclass
class DesignConstraint:
    objective: DesignObjective
    constraint_type: ConstraintType
    target_value: float
    weight: float = 1.0

@dataclass
class DesignContract:
    context_id: str
    primary_objective: DesignObjective
    constraints: List[DesignConstraint] = field(default_factory=list)
    exploration_parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    version: int = 1
    
    def add_constraint(self, objective: DesignObjective, constraint_type: ConstraintType,
                       target_value: float, weight: float = 1.0):
        self.constraints.append(DesignConstraint(
            objective=objective,
            constraint_type=constraint_type,
            target_value=target_value,
            weight=weight
        ))
    
    def to_dict(self) -> Dict:
        return {
            "context_id": self.context_id,
            "primary_objective": self.primary_objective.value,
            "constraints": [{
                "objective": c.objective.value,
                "type": c.constraint_type.value,
                "target": c.target_value,
                "weight": c.weight
            } for c in self.constraints],
            "exploration_parameters": self.exploration_parameters,
            "created_at": self.created_at,
            "version": self.version
        }

class ContractGenerator:
    def __init__(self):
        self.objective_priorities = {
            "medical": [DesignObjective.MAXIMIZE_ACCURACY, DesignObjective.MAXIMIZE_EXPLAINABILITY],
            "industrial": [DesignObjective.MINIMIZE_LATENCY, DesignObjective.MAXIMIZE_ACCURACY],
            "iot": [DesignObjective.MINIMIZE_ENERGY, DesignObjective.MINIMIZE_MEMORY],
            "automotive": [DesignObjective.MAXIMIZE_ROBUSTNESS, DesignObjective.MINIMIZE_LATENCY],
            "robotics": [DesignObjective.MINIMIZE_LATENCY, DesignObjective.MAXIMIZE_ROBUSTNESS]
        }
    
    def generate_contract(self, context, context_id: str = "ctx_001") -> DesignContract:
        domain = context.domain.value
        priorities = self.objective_priorities.get(domain, [DesignObjective.MAXIMIZE_ACCURACY])
        primary_objective = priorities[0] if priorities else DesignObjective.MAXIMIZE_ACCURACY
        
        contract = DesignContract(
            context_id=context_id,
            primary_objective=primary_objective,
            exploration_parameters={
                "population_size": 100,
                "generations": 50
            },
            created_at=datetime.now().isoformat()
        )
        
        # Ajouter les contraintes
        contract.add_constraint(DesignObjective.MINIMIZE_LATENCY, ConstraintType.HARD, context.max_latency_ms)
        contract.add_constraint(DesignObjective.MINIMIZE_ENERGY, ConstraintType.HARD, context.max_power_mw)
        contract.add_constraint(DesignObjective.MINIMIZE_MEMORY, ConstraintType.HARD, context.max_memory_kb)
        contract.add_constraint(DesignObjective.MAXIMIZE_ACCURACY, ConstraintType.HARD, context.min_accuracy)
        
        if context.requires_explainability:
            contract.add_constraint(DesignObjective.MAXIMIZE_EXPLAINABILITY, ConstraintType.SOFT, 0.8, weight=0.7)
        
        if context.requires_robustness:
            contract.add_constraint(DesignObjective.MAXIMIZE_ROBUSTNESS, ConstraintType.SOFT, 0.85, weight=0.8)
        
        return contract
