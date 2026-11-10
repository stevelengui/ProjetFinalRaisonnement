"""
Perturbation Engine - Perturbation d'un facteur à la fois
Exigence : "Perturbation d'un facteur à la fois : budget mémoire, criticité latence, 
criticité fiabilité, contexte de menace, exposition au domain shift, information manquante"
"""

from dataclasses import dataclass, replace
from typing import Dict, List, Optional
from copy import deepcopy
from scenarios import Context


@dataclass
class Perturbation:
    """Une perturbation appliquée à un contexte"""
    factor: str  # Nom du facteur perturbé
    original_value: any
    perturbed_value: any
    severity: str  # "mild", "moderate", "severe"


class PerturbationEngine:
    """
    Moteur de perturbation contrôlée
    Applique UN facteur à la fois pour permettre l'analyse causale
    """
    
    PERTURBATION_FACTORS = [
        "max_memory_kb",
        "max_latency_ms",
        "max_power_mw",
        "min_accuracy",
        "safety_relevant",
        "reliability_required",
        "security_required",
        "threat_context",
        "domain_shift_expected",
        "missing_info",
    ]
    
    def __init__(self):
        self.perturbation_log: List[Dict] = []
    
    def perturb_single_factor(self, base_context: Context, 
                              factor: str,
                              severity: str = "moderate") -> Context:
        """
        Perturbe UN SEUL facteur du contexte
        """
        if factor not in self.PERTURBATION_FACTORS:
            raise ValueError(f"Facteur inconnu: {factor}")
        
        perturbed = deepcopy(base_context)
        perturbed.context_id = f"{base_context.context_id}_pert_{factor}"
        
        original = getattr(perturbed, factor)
        
        # Appliquer la perturbation
        if factor == "max_memory_kb":
            if severity == "mild":
                new_value = original * 0.75 if original else 128.0
            elif severity == "moderate":
                new_value = original * 0.5 if original else 128.0
            else:  # severe
                new_value = original * 0.25 if original else 64.0
            perturbed.max_memory_kb = new_value
        
        elif factor == "max_latency_ms":
            if severity == "mild":
                new_value = original * 0.75 if original else 15.0
            elif severity == "moderate":
                new_value = original * 0.5 if original else 10.0
            else:
                new_value = original * 0.25 if original else 5.0
            perturbed.max_latency_ms = new_value
        
        elif factor == "max_power_mw":
            if severity == "mild":
                new_value = original * 0.75 if original else 37.5
            elif severity == "moderate":
                new_value = original * 0.5 if original else 25.0
            else:
                new_value = original * 0.25 if original else 12.5
            perturbed.max_power_mw = new_value
        
        elif factor == "min_accuracy":
            # Pour la précision, augmenter = plus strict
            if severity == "mild":
                new_value = min(0.99, original + 0.01) if original else 0.96
            elif severity == "moderate":
                new_value = min(0.99, original + 0.02) if original else 0.97
            else:
                new_value = min(0.99, original + 0.03) if original else 0.98
            perturbed.min_accuracy = new_value
        
        elif factor == "safety_relevant":
            perturbed.safety_relevant = not original
        
        elif factor == "reliability_required":
            perturbed.reliability_required = not original
        
        elif factor == "security_required":
            perturbed.security_required = not original
        
        elif factor == "threat_context":
            levels = ["none", "low", "medium", "high"]
            if severity == "moderate":
                new_value = "high" if original in ["none", "low"] else "none"
            else:
                new_value = "medium" if original in ["none"] else "high"
            perturbed.threat_context = new_value
        
        elif factor == "domain_shift_expected":
            perturbed.domain_shift_expected = not original
        
        elif factor == "missing_info":
            if original:
                perturbed.missing_info = []  # Supprimer les manquants
            else:
                perturbed.missing_info = ["max_latency_ms"]  # Ajouter un manquant
        
        # Log
        self.perturbation_log.append({
            "base_context_id": base_context.context_id,
            "perturbed_context_id": perturbed.context_id,
            "factor": factor,
            "original_value": str(original),
            "perturbed_value": str(getattr(perturbed, factor)),
            "severity": severity
        })
        
        return perturbed
    
    def generate_perturbation_matrix(self, base_context: Context) -> List[Context]:
        """
        Génère toutes les perturbations d'un contexte de base
        Une ligne = un facteur perturbé
        """
        perturbations = []
        
        for factor in self.PERTURBATION_FACTORS:
            for severity in ["mild", "moderate", "severe"]:
                try:
                    p = self.perturb_single_factor(base_context, factor, severity)
                    perturbations.append(p)
                except Exception as e:
                    print(f"⚠️ Erreur perturbation {factor}/{severity}: {e}")
        
        return perturbations
    
    def generate_perturbations_for_all(self, base_contexts: List[Context]) -> List[Context]:
        """Génère toutes les perturbations pour tous les contextes de base"""
        all_perturbed = []
        
        # Ne prendre que quelques contextes de base pour éviter explosion combinatoire
        # Prendre C01, C06, C11, C16 (références principales)
        base_ids = ["C01", "C06", "C11", "C16"]
        bases = [c for c in base_contexts if c.context_id in base_ids]
        
        for base in bases:
            perturbations = self.generate_perturbation_matrix(base)
            all_perturbed.extend(perturbations)
        
        return all_perturbed
    
    def get_log(self) -> List[Dict]:
        return self.perturbation_log


if __name__ == "__main__":
    from scenarios import get_all_scenarios
    
    scenarios = get_all_scenarios()
    engine = PerturbationEngine()
    
    # Test sur un contexte
    base = scenarios[0]  # C01
    print(f"Base: {base.context_id}")
    print(f"  max_latency_ms: {base.max_latency_ms}")
    
    perturbed = engine.perturb_single_factor(base, "max_latency_ms", "moderate")
    print(f"\nPerturbé: {perturbed.context_id}")
    print(f"  max_latency_ms: {perturbed.max_latency_ms}")
    
    # Test matrice complète
    all_pert = engine.generate_perturbation_matrix(base)
    print(f"\n✅ {len(all_pert)} perturbations générées pour {base.context_id}")
    
    # Log
    print(f"\n📋 Log: {len(engine.get_log())} entrées")
