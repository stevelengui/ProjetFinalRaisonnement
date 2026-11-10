"""
Mise à jour du registre avec les VRAIES valeurs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meta_reasoning.evidence_registry import EvidenceRegistry, EvidenceEntry, EvidenceType, Provenance
from meta_reasoning.memory_profiler_v2 import MemoryProfilerReal


def update_registry():
    """Met à jour le registre avec les vraies valeurs"""
    
    registry = EvidenceRegistry()
    profiler = MemoryProfilerReal()
    report = profiler.profile_ecg_model()
    
    # Supprimer les anciennes entrées incorrectes
    registry.entries = {}
    
    # Ajouter les vraies entrées
    entries = [
        EvidenceEntry(
            result_id="ecg_real_params_001",
            experiment="E0", rq="RQ1",
            design_id="ecg_hybrid_8bit",
            dataset="N/A", split="N/A", seed=42,
            platform="RV32X", clock_mhz=120, quantization_bits=8,
            evidence_type=EvidenceType.MEMORY,
            value=float(report["total_parameters"]),
            unit="parameters",
            provenance=Provenance.DER,
            method="Direct count from C array declarations in model_weights.h",
            uncertainty=0, uncertainty_type="none", n_samples=1,
            assumptions=[
                "int8_t = 1 byte per parameter",
                "Scales are int32_t but not counted as weights",
                "Counted only learnable parameters"
            ],
            artifact_path="firmware/model/model_weights.h"
        ),
        EvidenceEntry(
            result_id="ecg_real_M_weights_001",
            experiment="E0", rq="RQ1",
            design_id="ecg_hybrid_8bit",
            dataset="N/A", split="N/A", seed=42,
            platform="RV32X", clock_mhz=120, quantization_bits=8,
            evidence_type=EvidenceType.MEMORY,
            value=float(report["M_weights"]),
            unit="bytes",
            provenance=Provenance.DER,
            method="Sum of array sizes from model_weights.h",
            uncertainty=0, uncertainty_type="none", n_samples=1,
            assumptions=["All arrays are int8_t"],
            artifact_path="firmware/model/model_weights.h"
        ),
        EvidenceEntry(
            result_id="ecg_real_M_total_001",
            experiment="E0", rq="RQ1",
            design_id="ecg_hybrid_8bit",
            dataset="N/A", split="N/A", seed=42,
            platform="RV32X", clock_mhz=120, quantization_bits=8,
            evidence_type=EvidenceType.MEMORY,
            value=float(report["M_total"]),
            unit="bytes",
            provenance=Provenance.DER,
            method="Sum of M_weights + M_activation + M_state + M_runtime + M_code",
            uncertainty=0, uncertainty_type="none", n_samples=1,
            assumptions=[
                "M_runtime estimated at 2048 bytes",
                "M_code estimated at 8192 bytes"
            ],
            artifact_path="evidence_registry/memory_reports_real.json"
        ),
    ]
    
    for entry in entries:
        registry.register(entry)
    
    path = registry.save()
    
    print(f"✅ {len(entries)} entrées enregistrées avec les VRAIES valeurs")
    print(f"📄 Registre: {path}")
    print(f"\n📊 Résumé:")
    import json
    print(json.dumps(registry.get_summary(), indent=2))


if __name__ == "__main__":
    update_registry()
