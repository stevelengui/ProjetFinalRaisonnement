"""
External Validator - Simule une validation externe des contrats
Résout l'écart modéré #6
"""

from dataclasses import dataclass
from typing import Dict, List

from ground_truth_contracts import get_reference_contract


@dataclass
class ValidationResult:
    contract_id: str
    validator: str
    is_valid: bool
    confidence: float
    comments: List[str]


class ExternalValidator:
    """
    Simule une validation externe des contrats de référence
    Dans un vrai système, ce serait un expert humain
    """
    
    # Règles de validation externe
    VALIDATION_RULES = {
        "medical": {
            "max_latency_ms": {"min": 5.0, "max": 50.0},
            "min_accuracy": {"min": 0.90, "max": 0.99},
            "must_have_reliability": True,
        },
        "industrial": {
            "max_latency_ms": {"min": 10.0, "max": 100.0},
            "min_accuracy": {"min": 0.85, "max": 0.98},
            "must_have_reliability": True,
        }
    }
    
    def validate_contract(self, context_id: str, 
                        reference_contract,
                        external_expert: str = "expert_001") -> ValidationResult:
        """
        Valide un contrat de référence selon des règles externes
        """
        comments = []
        is_valid = True
        confidence = 0.90
        
        # Récupérer les contraintes
        hc = reference_contract.hard_constraints
        
        # Déterminer le domaine (depuis context_id)
        domain = "medical" if "medical" in context_id.lower() or int(context_id[1:]) <= 10 else "industrial"
        rules = self.VALIDATION_RULES.get(domain, self.VALIDATION_RULES["industrial"])
        
        # Vérifier max_latency_ms
        if "latency_ms_max" in hc:
            latency = hc["latency_ms_max"]
            if latency < rules["max_latency_ms"]["min"]:
                is_valid = False
                comments.append(f"Latence {latency}ms trop basse (min: {rules['max_latency_ms']['min']}ms)")
            elif latency > rules["max_latency_ms"]["max"]:
                is_valid = False
                comments.append(f"Latence {latency}ms trop haute (max: {rules['max_latency_ms']['max']}ms)")
            else:
                comments.append(f"Latence {latency}ms dans les limites acceptables")
        
        # Vérifier min_accuracy
        if "accuracy_min" in hc:
            accuracy = hc["accuracy_min"]
            if accuracy < rules["min_accuracy"]["min"]:
                is_valid = False
                comments.append(f"Précision {accuracy} trop basse")
            elif accuracy > rules["min_accuracy"]["max"]:
                comments.append(f"Précision {accuracy} très élevée (à valider)")
                confidence -= 0.10
            else:
                comments.append(f"Précision {accuracy} dans les limites acceptables")
        
        # Vérifier la fiabilité
        if rules["must_have_reliability"]:
            has_reliability = "reliability_min" in hc
            if not has_reliability:
                comments.append("Attention : fiabilité non spécifiée explicitement")
                confidence -= 0.05
        
        return ValidationResult(
            contract_id=reference_contract.context_id,
            validator=external_expert,
            is_valid=is_valid,
            confidence=confidence,
            comments=comments
        )
    
    def validate_all_contracts(self) -> Dict:
        """Valide tous les contrats de référence"""
        from ground_truth_contracts import get_all_reference_contracts
        
        contracts = get_all_reference_contracts()
        results = []
        
        for ctx_id, contract in contracts.items():
            result = self.validate_contract(ctx_id, contract)
            results.append(result)
        
        valid_count = sum(1 for r in results if r.is_valid)
        
        return {
            "total_contracts": len(results),
            "validated": valid_count,
            "validation_rate": valid_count / len(results) if results else 0,
            "results": [
                {
                    "contract_id": r.contract_id,
                    "validator": r.validator,
                    "is_valid": r.is_valid,
                    "confidence": r.confidence,
                    "comments": r.comments
                }
                for r in results
            ]
        }


if __name__ == "__main__":
    import json
    
    validator = ExternalValidator()
    results = validator.validate_all_contracts()
    
    print("=" * 70)
    print("🔍 VALIDATION EXTERNE DES CONTRATS")
    print("=" * 70)
    print(f"\nContrats validés: {results['validated']}/{results['total_contracts']}")
    print(f"Taux de validation: {results['validation_rate']:.0%}")
    
    for r in results["results"][:3]:
        status = "✅" if r["is_valid"] else "❌"
        print(f"\n{status} {r['contract_id']}:")
        for c in r["comments"]:
            print(f"   - {c}")
