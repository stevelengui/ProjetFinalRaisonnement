"""
Enregistre les preuves E0 dans le registre central
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "meta_reasoning"))

from evidence_registry import EvidenceRegistry, EvidenceEntry, EvidenceType, Provenance


def register_e0_evidence():
    """Enregistre les preuves E0"""
    
    registry = EvidenceRegistry()
    
    # Charger les résultats E0
    results_path = os.path.join(os.path.dirname(__file__), "results", "e0_results.json")
    with open(results_path) as f:
        results = json.load(f)
    
    metrics = results["metrics"]
    
    # Enregistrer les métriques principales
    entries = [
        EvidenceEntry(
            result_id="e0_contract_accuracy_001",
            experiment="E0", rq="RQ1",
            design_id="all_contexts",
            dataset="30 controlled contexts", split="full", seed=42,
            platform="N/A", clock_mhz=0, quantization_bits=0,
            evidence_type=EvidenceType.ACCURACY,
            value=metrics["contract_accuracy"],
            unit="ratio",
            provenance=Provenance.SIM,
            method="Contract accuracy vs manually-verified reference contracts",
            uncertainty=0.0, uncertainty_type="none", n_samples=30,
            assumptions=["Reference contracts verified by domain experts"],
            artifact_path="experiments/E0_context_to_contract/results/e0_results.json"
        ),
        EvidenceEntry(
            result_id="e0_primary_objective_accuracy_001",
            experiment="E0", rq="RQ1",
            design_id="all_contexts",
            dataset="30 controlled contexts", split="full", seed=42,
            platform="N/A", clock_mhz=0, quantization_bits=0,
            evidence_type=EvidenceType.ACCURACY,
            value=metrics["primary_objective_accuracy"],
            unit="ratio",
            provenance=Provenance.SIM,
            method="Primary objective correctness rate",
            uncertainty=0.0, uncertainty_type="none", n_samples=30,
            assumptions=["Reference objectives verified by domain experts"],
            artifact_path="experiments/E0_context_to_contract/results/e0_results.json"
        ),
        EvidenceEntry(
            result_id="e0_missing_info_detection_001",
            experiment="E0", rq="RQ1",
            design_id="all_contexts",
            dataset="5 contexts with missing info", split="full", seed=42,
            platform="N/A", clock_mhz=0, quantization_bits=0,
            evidence_type=EvidenceType.RELIABILITY,
            value=metrics["missing_info_detection_rate"],
            unit="ratio",
            provenance=Provenance.SIM,
            method="Missing information detection (recall)",
            uncertainty=0.0, uncertainty_type="none", n_samples=5,
            assumptions=["Missing info known a priori"],
            artifact_path="experiments/E0_context_to_contract/results/e0_results.json"
        ),
        EvidenceEntry(
            result_id="e0_reliability_transition_001",
            experiment="E0", rq="RQ1",
            design_id="C01_vs_C06",
            dataset="ECG normal vs ICU", split="controlled", seed=42,
            platform="N/A", clock_mhz=0, quantization_bits=0,
            evidence_type=EvidenceType.RELIABILITY,
            value=1.0 if metrics["reliability_transition_valid"] else 0.0,
            unit="boolean",
            provenance=Provenance.SIM,
            method="Reliability preference→hard constraint transition test",
            uncertainty=0.0, uncertainty_type="none", n_samples=1,
            assumptions=["C01 = normal, C06 = safety-relevant"],
            artifact_path="experiments/E0_context_to_contract/results/e0_results.json"
        ),
    ]
    
    for entry in entries:
        try:
            registry.register(entry)
            print(f"✅ Enregistré: {entry.result_id}")
        except ValueError as e:
            print(f"⚠️ {e}")
    
    # Sauvegarder
    registry.save()
    
    print(f"\n📊 Registre mis à jour: {len(registry.entries)} entrées")
    print(json.dumps(registry.get_summary(), indent=2))


if __name__ == "__main__":
    register_e0_evidence()
