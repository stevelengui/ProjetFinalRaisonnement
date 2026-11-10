"""
Lifecycle Manager - Actions de cycle de vie
Exigence : "MONITOR, CALIBRATE, ADAPT, REMAP, REDESIGN"
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


class LifecycleState(Enum):
    NOMINAL = "nominal"          # C0 - Tout va bien
    MINOR_SHIFT = "minor"        # C1 - Léger drift
    MODERATE_SHIFT = "moderate"  # C2 - Drift significatif
    MAJOR_SHIFT = "major"        # C3 - Drift majeur
    STRUCTURAL_CHANGE = "structural"  # C4 - Changement structurel


class LifecycleAction(Enum):
    CONTINUE = "continue"      # C0 : rien à faire
    CALIBRATE = "calibrate"    # C1 : recalibration
    ADAPT = "adapt"            # C2 : adaptation (MAML, fine-tuning)
    REMAP = "remap"            # C3 : remapping complet
    REDESIGN = "redesign"      # C4 : nouvelle conception


@dataclass
class DriftDetection:
    """Détection de dérive"""
    severity: float  # 0-1
    evidence: str
    metrics_affected: List[str]


class LifecycleManager:
    """
    Gestion du cycle de vie post-déploiement
    """
    
    def __init__(self):
        self.deployment_states: Dict[str, LifecycleState] = {}
        self.action_history: List[Dict] = []
    
    def classify_drift(self, drift: DriftDetection) -> LifecycleState:
        """
        Classifie la sévérité d'une dérive
        """
        if drift.severity < 0.05:
            return LifecycleState.NOMINAL
        elif drift.severity < 0.15:
            return LifecycleState.MINOR_SHIFT
        elif drift.severity < 0.35:
            return LifecycleState.MODERATE_SHIFT
        elif drift.severity < 0.60:
            return LifecycleState.MAJOR_SHIFT
        else:
            return LifecycleState.STRUCTURAL_CHANGE
    
    def select_action(self, state: LifecycleState, 
                     deployment_id: str,
                     constraints: Dict) -> Dict:
        """
        Sélectionne l'action appropriée
        """
        action_map = {
            LifecycleState.NOMINAL: LifecycleAction.CONTINUE,
            LifecycleState.MINOR_SHIFT: LifecycleAction.CALIBRATE,
            LifecycleState.MODERATE_SHIFT: LifecycleAction.ADAPT,
            LifecycleState.MAJOR_SHIFT: LifecycleAction.REMAP,
            LifecycleState.STRUCTURAL_CHANGE: LifecycleAction.REDESIGN,
        }
        
        action = action_map[state]
        
        result = {
            "deployment_id": deployment_id,
            "state": state.value,
            "action": action.value,
            "timestamp": datetime.now().isoformat(),
            "rationale": self._get_rationale(state, action),
            "expected_cost": self._get_cost(action),
            "constraints_respected": self._check_constraints(action, constraints)
        }
        
        self.action_history.append(result)
        self.deployment_states[deployment_id] = state
        
        return result
    
    def _get_rationale(self, state: LifecycleState, 
                       action: LifecycleAction) -> str:
        """Génère une justification"""
        rationales = {
            LifecycleState.NOMINAL: "Aucun drift détecté, fonctionner normalement",
            LifecycleState.MINOR_SHIFT: "Drift léger, recalibration suffisante",
            LifecycleState.MODERATE_SHIFT: "Drift modéré, adaptation nécessaire",
            LifecycleState.MAJOR_SHIFT: "Drift majeur, remapping requis",
            LifecycleState.STRUCTURAL_CHANGE: "Changement structurel, redesign nécessaire"
        }
        return rationales.get(state, "Action par défaut")
    
    def _get_cost(self, action: LifecycleAction) -> float:
        """Coût relatif de l'action"""
        costs = {
            LifecycleAction.CONTINUE: 0.0,
            LifecycleAction.CALIBRATE: 0.1,
            LifecycleAction.ADAPT: 0.3,
            LifecycleAction.REMAP: 0.6,
            LifecycleAction.REDESIGN: 1.0,
        }
        return costs.get(action, 0.5)
    
    def _check_constraints(self, action: LifecycleAction, 
                          constraints: Dict) -> bool:
        """Vérifie si l'action respecte les contraintes"""
        # Simplifié : toutes les actions sauf REDESIGN respectent les contraintes
        if action == LifecycleAction.REDESIGN:
            return constraints.get("allow_redesign", False)
        return True
