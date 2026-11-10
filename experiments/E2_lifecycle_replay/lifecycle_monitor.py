"""
Lifecycle Monitor - Monitoring continu du cycle de vie
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime

from deployment_contract import DeploymentContract
from lifecycle_perturbations import LifecyclePerturbation, apply_perturbation


@dataclass
class MonitoringSnapshot:
    """Un snapshot de monitoring"""
    snapshot_id: str
    timestamp: str
    metrics: Dict[str, float]
    validity_status: Dict
    perturbation_active: str
    hours_elapsed: float


class LifecycleMonitor:
    """
    Moniteur du cycle de vie
    Enregistre les snapshots et détecte les déviations
    """
    
    def __init__(self, contract: DeploymentContract):
        self.contract = contract
        self.snapshots: List[MonitoringSnapshot] = []
        self.base_metrics = {
            "accuracy": contract.deployed_design.accuracy,
            "latency_ms": contract.deployed_design.latency_ms,
            "memory_kb": contract.deployed_design.memory_kb,
            "energy_mj": contract.deployed_design.energy_mj,
            "reliability": 0.92  # Baseline reliability
        }
    
    def take_snapshot(self, perturbation: LifecyclePerturbation,
                     hours_elapsed: float) -> MonitoringSnapshot:
        """Prend un snapshot sous perturbation"""
        # Appliquer la perturbation
        current_metrics = apply_perturbation(self.base_metrics, perturbation)
        
        # Vérifier la validité
        validity = self.contract.check_validity(current_metrics)
        
        snapshot = MonitoringSnapshot(
            snapshot_id=f"snap_{len(self.snapshots)+1:03d}",
            timestamp=datetime.now().isoformat(),
            metrics=current_metrics,
            validity_status=validity,
            perturbation_active=perturbation.perturbation_id,
            hours_elapsed=hours_elapsed
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def run_monitoring_cycle(self, perturbations: List[LifecyclePerturbation],
                            hours_per_perturbation: float = 24.0) -> List[MonitoringSnapshot]:
        """
        Simule un cycle de monitoring complet
        """
        total_hours = 0.0
        
        for perturbation in perturbations:
            # Snapshot au début
            snapshot = self.take_snapshot(perturbation, total_hours)
            total_hours += hours_per_perturbation
        
        return self.snapshots
    
    def get_invalidity_timeline(self) -> List[Dict]:
        """Retourne la timeline des invalidités"""
        timeline = []
        
        for snapshot in self.snapshots:
            if not snapshot.validity_status["is_valid"]:
                timeline.append({
                    "snapshot_id": snapshot.snapshot_id,
                    "perturbation": snapshot.perturbation_active,
                    "hours": snapshot.hours_elapsed,
                    "violations": snapshot.validity_status["violations"]
                })
        
        return timeline
    
    def get_summary(self) -> Dict:
        """Résumé du monitoring"""
        if not self.snapshots:
            return {"total_snapshots": 0}
        
        valid_count = sum(1 for s in self.snapshots if s.validity_status["is_valid"])
        
        return {
            "total_snapshots": len(self.snapshots),
            "valid_snapshots": valid_count,
            "invalid_snapshots": len(self.snapshots) - valid_count,
            "validity_rate": valid_count / len(self.snapshots),
            "total_hours": self.snapshots[-1].hours_elapsed if self.snapshots else 0
        }


if __name__ == "__main__":
    from deployment_contract import create_ecg_deployment_contract
    from lifecycle_perturbations import get_all_perturbations
    
    contract = create_ecg_deployment_contract()
    monitor = LifecycleMonitor(contract)
    perturbations = get_all_perturbations()
    
    print("✅ LifecycleMonitor prêt\n")
    
    snapshots = monitor.run_monitoring_cycle(perturbations)
    
    print(f"📊 {len(snapshots)} snapshots")
    for s in snapshots:
        status = "✅" if s.validity_status["is_valid"] else "❌"
        print(f"   {status} {s.snapshot_id}: {s.perturbation_active} "
              f"({s.hours_elapsed:.0f}h, violations={s.validity_status['num_violations']})")
    
    print(f"\n📈 Résumé: {monitor.get_summary()}")
