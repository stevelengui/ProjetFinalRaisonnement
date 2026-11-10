"""
ASR Evaluator - VERSION CORRIGÉE
Mapping correct des attaques et ajustement selon le design
"""

from dataclasses import dataclass
from typing import Dict, List

from threat_models import ThreatModel, ThreatModelRegistry
from attack_scenarios import AttackScenario, AttackScenarioRegistry, AttackType
from security_designs import SecurityDesign


@dataclass
class ASRResult:
    design_id: str
    attack_id: str
    asr_base: float
    asr_adjusted: float
    threat_level: float
    asr_valid: bool
    threshold: float


class ASREvaluator:
    def __init__(self, asr_threshold: float = 0.20):
        self.asr_threshold = asr_threshold
        self.threat_registry = ThreatModelRegistry()
        self.attack_registry = AttackScenarioRegistry()
    
    def evaluate_attack(self, design: SecurityDesign, 
                       attack: AttackScenario,
                       threat_model: ThreatModel) -> ASRResult:
        """
        Évalue l'ASR d'un design contre une attaque
        """
        # CORRECTION : Utiliser l'ID court (ex: "A1" au lieu de "A1_fgsm")
        asr_base = design.asr_by_attack.get(attack.attack_id, 0.5)
        
        # Ajuster selon le niveau de menace
        threat_multiplier = 1.0 + threat_model.threat_level * 0.3
        asr_adjusted = min(1.0, asr_base * threat_multiplier)
        
        asr_valid = asr_adjusted <= self.asr_threshold
        
        return ASRResult(
            design_id=design.design_id,
            attack_id=attack.attack_id,
            asr_base=asr_base,
            asr_adjusted=asr_adjusted,
            threat_level=threat_model.threat_level,
            asr_valid=asr_valid,
            threshold=self.asr_threshold
        )
    
    def evaluate_design_all_attacks(self, design: SecurityDesign,
                                    threat_model: ThreatModel) -> Dict:
        """
        Évalue un design contre toutes les attaques
        """
        # CORRECTION : Toujours utiliser TOUTES les attaques, pas seulement celles de la menace
        attacks = list(self.attack_registry.scenarios.values())
        
        # Filtrer : seulement les attaques pertinentes pour cette menace
        # (celles qui ont ce threat_model_id ou une menace compatible)
        relevant_attacks = []
        for attack in attacks:
            attack_threat = self.threat_registry.get_by_id(attack.threat_model_id)
            if attack_threat and threat_model.threat_level >= attack_threat.threat_level * 0.7:
                relevant_attacks.append(attack)
        
        # Si aucune attaque pertinente, prendre toutes les attaques
        if not relevant_attacks:
            if threat_model.threat_level < 0.1:
                # Pas de menace → ASR = 0
                return {
                    "design_id": design.design_id,
                    "threat_id": threat_model.threat_id,
                    "threat_level": threat_model.threat_level,
                    "attacks_evaluated": 0,
                    "max_asr": 0.0,
                    "avg_asr": 0.0,
                    "all_valid": True,
                    "asr_threshold": self.asr_threshold,
                    "results": []
                }
            relevant_attacks = attacks
        
        results = []
        for attack in relevant_attacks:
            result = self.evaluate_attack(design, attack, threat_model)
            results.append(result)
        
        if results:
            max_asr = max(r.asr_adjusted for r in results)
            avg_asr = sum(r.asr_adjusted for r in results) / len(results)
            all_valid = all(r.asr_valid for r in results)
        else:
            max_asr = 0.0
            avg_asr = 0.0
            all_valid = True
        
        return {
            "design_id": design.design_id,
            "threat_id": threat_model.threat_id,
            "threat_level": threat_model.threat_level,
            "attacks_evaluated": len(results),
            "max_asr": max_asr,
            "avg_asr": avg_asr,
            "all_valid": all_valid,
            "asr_threshold": self.asr_threshold,
            "results": [
                {
                    "attack_id": r.attack_id,
                    "asr_base": r.asr_base,
                    "asr_adjusted": r.asr_adjusted,
                    "valid": r.asr_valid
                }
                for r in results
            ]
        }
    
    def compare_designs(self, designs: List[SecurityDesign],
                       threat_model: ThreatModel) -> Dict:
        """Compare plusieurs designs"""
        comparison = {}
        
        for design in designs:
            result = self.evaluate_design_all_attacks(design, threat_model)
            comparison[design.design_id] = {
                "max_asr": round(result["max_asr"], 4),
                "avg_asr": round(result["avg_asr"], 4),
                "all_valid": result["all_valid"],
                "protection": design.protection_type.value,
                "resource_overhead": {
                    "latency_pct": design.protection_overhead_latency,
                    "memory_pct": design.protection_overhead_memory,
                    "energy_pct": design.protection_overhead_energy
                }
            }
        
        return comparison
    
    def get_security_score(self, design: SecurityDesign,
                          threat_model: ThreatModel) -> float:
        """Score de sécurité composite"""
        result = self.evaluate_design_all_attacks(design, threat_model)
        
        asr_score = 1.0 - result["avg_asr"]
        
        total_overhead = (
            design.protection_overhead_latency +
            design.protection_overhead_memory +
            design.protection_overhead_energy
        ) / 3.0
        
        if total_overhead > 100:
            overhead_penalty = 0.5
        elif total_overhead > 50:
            overhead_penalty = 0.2
        else:
            overhead_penalty = 0.0
        
        security_score = asr_score - overhead_penalty
        
        return max(0, min(1, security_score))


if __name__ == "__main__":
    from security_designs import get_all_security_designs
    
    evaluator = ASREvaluator(asr_threshold=0.20)
    designs = get_all_security_designs()
    
    print("✅ ASREvaluator CORRIGÉ\n")
    
    for threat_id in ["T0", "T2", "T4"]:
        threat = evaluator.threat_registry.get_by_id(threat_id)
        print(f"\n=== {threat_id} (level={threat.threat_level}) ===")
        
        comparison = evaluator.compare_designs(designs, threat)
        for design_id, metrics in comparison.items():
            print(f"   {design_id}: ASR={metrics['max_asr']:.3f}, valid={metrics['all_valid']}")
