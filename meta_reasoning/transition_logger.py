"""
Transition Logger - Log complet de toutes les transitions
Exigence : "Logger chaque transition état/action/preuve"
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any
from datetime import datetime
import json
import hashlib


@dataclass
class Transition:
    """Une transition dans le méta-raisonneur"""
    transition_id: str
    timestamp: str
    state_before: Dict
    action: Dict
    evidence_used: List[str]
    state_after: Dict
    outcome: str
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class TransitionLogger:
    """
    Logger de toutes les transitions
    Fournit un historique complet et auditable
    """
    
    def __init__(self, log_path: str = "evidence_registry/transitions.jsonl"):
        self.log_path = log_path
        self.transitions: List[Transition] = []
    
    def log_transition(self, state_before: Dict, action: Dict,
                      evidence_used: List[str], state_after: Dict,
                      outcome: str, notes: str = "") -> str:
        """Enregistre une transition"""
        
        # ID unique
        transition_id = self._generate_id(state_before, action, state_after)
        
        transition = Transition(
            transition_id=transition_id,
            timestamp=datetime.now().isoformat(),
            state_before=self._summarize(state_before),
            action=action,
            evidence_used=evidence_used,
            state_after=self._summarize(state_after),
            outcome=outcome,
            notes=notes
        )
        
        self.transitions.append(transition)
        self._append_to_file(transition)
        
        return transition_id
    
    def _generate_id(self, s1: Dict, a: Dict, s2: Dict) -> str:
        """ID unique basé sur le contenu"""
        content = json.dumps([s1, a, s2], sort_keys=True, default=str)
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _summarize(self, state: Dict) -> Dict:
        """Résumé compact de l'état"""
        return {
            "phase": state.get("phase", "unknown"),
            "decision": state.get("decision"),
            "n_candidates": len(state.get("candidates", [])),
            "n_evidence": len(state.get("evidence", {}).get("evidence_ids", []))
        }
    
    def _append_to_file(self, transition: Transition):
        """Append au fichier JSONL"""
        import os
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(transition.to_dict()) + "\n")
    
    def get_history(self) -> List[Dict]:
        return [t.to_dict() for t in self.transitions]
    
    def get_stats(self) -> Dict:
        """Statistiques du logger"""
        if not self.transitions:
            return {"total": 0}
        
        outcomes = {}
        for t in self.transitions:
            outcomes[t.outcome] = outcomes.get(t.outcome, 0) + 1
        
        return {
            "total_transitions": len(self.transitions),
            "by_outcome": outcomes,
            "first_transition": self.transitions[0].timestamp,
            "last_transition": self.transitions[-1].timestamp
        }
