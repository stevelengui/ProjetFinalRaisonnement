"""
Fault Injector - Injecteur de fautes contrôlé
Exigence : "Injection de fautes contrôlée (logicielle/simulation)"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import random

from fault_models import FaultType, FaultModel, FaultModelRegistry
from candidate_designs import CandidateDesign


@dataclass
class InjectionResult:
    """Résultat d'une injection de faute"""
    design_id: str
    fault_type: FaultType
    fault_severity: str
    accuracy_before: float
    accuracy_after: float
    accuracy_drop: float
    detected: bool
    sdc: bool  # Silent Data Corruption
    recovered: bool


class FaultInjector:
    """
    Injecteur de fautes contrôlé
    Simule l'injection de fautes selon les modèles définis
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.registry = FaultModelRegistry()
        self.injection_log: List[InjectionResult] = []
    
    def inject_single_fault(self, design: CandidateDesign, 
                           fault_type: FaultType,
                           run_id: int = 0) -> InjectionResult:
        """
        Injecte UNE faute dans un design
        """
        model = self.registry.models[fault_type]
        
        # Seed déterministe pour reproductibilité
        seed = hash(f"{design.design_id}_{fault_type.value}_{run_id}") % 2**32
        rng = random.Random(seed)
        
        # Décider si la faute se produit (probabilité)
        if rng.random() > model.probability:
            # Pas de faute
            return InjectionResult(
                design_id=design.design_id,
                fault_type=fault_type,
                fault_severity=model.severity,
                accuracy_before=design.nominal_accuracy,
                accuracy_after=design.nominal_accuracy,
                accuracy_drop=0.0,
                detected=False,
                sdc=False,
                recovered=True
            )
        
        # Faute injectée
        accuracy_before = design.nominal_accuracy
        
        # Impact selon la sensibilité du design
        sensitivity = design.fault_sensitivity.get(fault_type.value, 0.05)
        
        # Si le design est protégé, réduire l'impact
        if design.has_protection:
            sensitivity *= (1 - design.protection_coverage)
        
        # Ajouter un peu de variabilité
        impact = sensitivity * (1 + rng.uniform(-0.2, 0.2))
        
        # Accuracy après faute
        accuracy_after = max(0, accuracy_before - impact)
        accuracy_drop = accuracy_before - accuracy_after
        
        # Détection
        detected = rng.random() < model.detection_likelihood
        
        # Silent Data Corruption : erreur non détectée mais impactful
        sdc = (not detected) and (accuracy_drop > 0.01)
        
        # Récupération (si protection)
        recovered = False
        if design.has_protection and rng.random() < design.protection_coverage:
            recovered = True
            accuracy_after = accuracy_before * 0.995  # Récupération partielle
            accuracy_drop = accuracy_before - accuracy_after
        
        result = InjectionResult(
            design_id=design.design_id,
            fault_type=fault_type,
            fault_severity=model.severity,
            accuracy_before=accuracy_before,
            accuracy_after=accuracy_after,
            accuracy_drop=accuracy_drop,
            detected=detected,
            sdc=sdc,
            recovered=recovered
        )
        
        self.injection_log.append(result)
        return result
    
    def inject_n_faults(self, design: CandidateDesign, 
                       n_faults: int = 100) -> List[InjectionResult]:
        """Injecte N fautes aléatoires"""
        results = []
        fault_types = list(FaultType)
        
        for i in range(n_faults):
            fault_type = random.choice(fault_types)
            result = self.inject_single_fault(design, fault_type, run_id=i)
            results.append(result)
        
        return results
    
    def inject_systematic(self, design: CandidateDesign, 
                         n_runs: int = 10) -> Dict[FaultType, List[InjectionResult]]:
        """
        Injection systématique : chaque type de faute N fois
        """
        results_by_type = {}
        
        for fault_type in FaultType:
            results = []
            for i in range(n_runs):
                result = self.inject_single_fault(design, fault_type, run_id=i)
                results.append(result)
            results_by_type[fault_type] = results
        
        return results_by_type
    
    def get_summary(self) -> Dict:
        """Résumé de l'injection"""
        if not self.injection_log:
            return {"total": 0}
        
        sdc_count = sum(1 for r in self.injection_log if r.sdc)
        detected_count = sum(1 for r in self.injection_log if r.detected)
        recovered_count = sum(1 for r in self.injection_log if r.recovered)
        
        return {
            "total_injections": len(self.injection_log),
            "sdc_count": sdc_count,
            "detected_count": detected_count,
            "recovered_count": recovered_count,
            "avg_accuracy_drop": sum(r.accuracy_drop for r in self.injection_log) / len(self.injection_log)
        }


if __name__ == "__main__":
    injector = FaultInjector()
    
    from candidate_designs import get_all_candidates
    candidates = get_all_candidates()
    
    print("✅ FaultInjector prêt")
    for design in candidates:
        results = injector.inject_n_faults(design, n_faults=20)
        avg_drop = sum(r.accuracy_drop for r in results) / len(results)
        sdc_count = sum(1 for r in results if r.sdc)
        print(f"\n{design.design_id}:")
        print(f"   Avg accuracy drop: {avg_drop:.4f}")
        print(f"   SDC count: {sdc_count}/20")
