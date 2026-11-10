"""
Replay Engine - Controlled Lifecycle Replay
Exigence : "Si replay : dire 'controlled lifecycle replay', pas 'runtime adaptation'"
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime

from deployment_contract import DeploymentContract
from lifecycle_perturbations import (
    LifecyclePerturbation, PerturbationClass, 
    InterventionType, apply_perturbation, get_all_perturbations
)
from intervention_selector import InterventionSelector
from lifecycle_monitor import LifecycleMonitor


@dataclass
class ReplayEvent:
    """Un événement de replay"""
    event_id: str
    timestamp: str
    perturbation_id: str
    perturbation_class: str
    metrics_before: Dict[str, float]
    metrics_after_perturbation: Dict[str, float]
    validity_after: Dict
    selected_intervention: str
    intervention_score: float
    matches_expected: bool


class ControlledLifecycleReplay:
    """
    Controlled Lifecycle Replay
    
    IMPORTANT : Ce n'est PAS du "runtime adaptation"
    C'est un REPLAY CONTRÔLÉ de scénarios de cycle de vie
    """
    
    def __init__(self, contract: DeploymentContract):
        self.contract = contract
        self.selector = InterventionSelector()
        self.monitor = LifecycleMonitor(contract)
        self.events: List[ReplayEvent] = []
    
    def replay_perturbation(self, perturbation: LifecyclePerturbation) -> ReplayEvent:
        """
        Rejoue UNE perturbation (controlled replay)
        """
        # 1. Métriques avant perturbation
        base_metrics = self.monitor.base_metrics.copy()
        
        # 2. Appliquer la perturbation
        perturbed_metrics = apply_perturbation(base_metrics, perturbation)
        
        # 3. Vérifier la validité
        validity = self.contract.check_validity(perturbed_metrics)
        
        # 4. Sélectionner l'intervention
        selection = self.selector.select_intervention(perturbation)
        
        event = ReplayEvent(
            event_id=f"replay_{len(self.events)+1:03d}",
            timestamp=datetime.now().isoformat(),
            perturbation_id=perturbation.perturbation_id,
            perturbation_class=perturbation.perturbation_class.value,
            metrics_before=base_metrics,
            metrics_after_perturbation=perturbed_metrics,
            validity_after=validity,
            selected_intervention=selection["selected_intervention"],
            intervention_score=selection["score"],
            matches_expected=selection["matches_expected"]
        )
        
        self.events.append(event)
        return event
    
    def run_full_replay(self) -> Dict:
        """
        Rejoue le cycle de vie complet
        """
        print("="*70)
        print("🔄 CONTROLLED LIFECYCLE REPLAY")
        print("="*70)
        print(f"Contract: {self.contract.contract_id}")
        print(f"Design: {self.contract.deployed_design.design_id}")
        print(f"Domain: {self.contract.domain}")
        
        perturbations = get_all_perturbations()
        
        print(f"\n📊 Replay de {len(perturbations)} perturbations...\n")
        
        for perturbation in perturbations:
            event = self.replay_perturbation(perturbation)
            
            status = "✅" if event.matches_expected else "❌"
            valid_status = "✅" if event.validity_after["is_valid"] else "❌"
            
            print(f"{status} {event.perturbation_id} ({event.perturbation_class}):")
            print(f"   Validité après perturbation: {valid_status}")
            print(f"   Intervention: {event.selected_intervention} "
                  f"(expected: {perturbation.expected_intervention})")
            print(f"   Violations: {event.validity_after['num_violations']}")
            print()
        
        # Résumé
        matches_count = sum(1 for e in self.events if e.matches_expected)
        
        print("="*70)
        print("📊 RÉSUMÉ DU REPLAY")
        print("="*70)
        print(f"Événements: {len(self.events)}")
        print(f"Interventions correctes: {matches_count}/{len(self.events)}")
        print(f"Taux de correspondance: {matches_count/len(self.events):.0%}")
        
        return {
            "contract_id": self.contract.contract_id,
            "design_id": self.contract.deployed_design.design_id,
            "events": [
                {
                    "event_id": e.event_id,
                    "perturbation_id": e.perturbation_id,
                    "perturbation_class": e.perturbation_class,
                    "validity_after": e.validity_after["is_valid"],
                    "selected_intervention": e.selected_intervention,
                    "matches_expected": e.matches_expected,
                    "metrics_change": {
                        k: {
                            "before": e.metrics_before[k],
                            "after": e.metrics_after_perturbation[k],
                            "delta_pct": (e.metrics_after_perturbation[k] - e.metrics_before[k]) / e.metrics_before[k] * 100
                        }
                        for k in e.metrics_before.keys()
                    }
                }
                for e in self.events
            ],
            "matches_count": matches_count,
            "total_events": len(self.events),
            "match_rate": matches_count / len(self.events) if self.events else 0
        }
    
    def get_validity_envelope(self) -> Dict:
        """
        Retourne l'enveloppe de validité
        (quelles perturbations cassent la validité)
        """
        invalid_events = [e for e in self.events if not e.validity_after["is_valid"]]
        
        return {
            "valid_perturbations": [e.perturbation_id for e in self.events 
                                   if e.validity_after["is_valid"]],
            "invalid_perturbations": [e.perturbation_id for e in invalid_events],
            "validity_envelope_size": len([e for e in self.events 
                                          if e.validity_after["is_valid"]]),
            "total_perturbations": len(self.events)
        }


if __name__ == "__main__":
    from deployment_contract import create_ecg_deployment_contract
    import json
    
    contract = create_ecg_deployment_contract()
    replay = ControlledLifecycleReplay(contract)
    result = replay.run_full_replay()
    
    print("\n📊 Enveloppe de validité:")
    envelope = replay.get_validity_envelope()
    print(json.dumps(envelope, indent=2))
