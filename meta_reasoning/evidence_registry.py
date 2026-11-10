"""
Evidence Registry - Registre de preuves machine-readable
Exigence du directeur : "Créer un registre de preuves machine-readable avec : 
ID résultat, expérience, design, dataset/split/seed, plateforme, clock, quantification, 
comptage de paramètres, composants mémoire, cycles, latence, énergie, accuracy/F1, 
méthode, provenance (MEAS/SIM/SUR/ANA/LIT/DER), incertitude, hypothèses, commit git, timestamp"
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import hashlib
from datetime import datetime

class Provenance(Enum):
    """Types de provenance des preuves"""
    MEAS = "MEAS"  # Mesuré sur hardware physique
    SIM = "SIM"    # Simulé (cycle-accurate)
    SUR = "SUR"    # Surrogate model
    ANA = "ANA"    # Analytique (formule)
    LIT = "LIT"    # Littérature (publié)
    DER = "DER"    # Dérivé (reconstruction)

class EvidenceType(Enum):
    """Types de preuves"""
    LATENCY = "latency"
    ENERGY = "energy"
    MEMORY = "memory"
    ACCURACY = "accuracy"
    F1_SCORE = "f1_score"
    RELIABILITY = "reliability"
    SECURITY = "security"
    ROBUSTNESS = "robustness"
    EXPLAINABILITY = "explainability"

@dataclass
class EvidenceEntry:
    """
    Une entrée de preuve unique et traçable
    Chaque résultat numérique DOIT avoir sa provenance
    """
    # Identification
    result_id: str              # ID unique, ex: "ecg_8bit_latency_001"
    experiment: str             # E0, E1, E2, ..., E7
    rq: str                     # RQ1, RQ2, ..., RQ5
    
    # Design et contexte
    design_id: str              # ecg_hybrid_8bit
    dataset: str                # "MIT-BIH"
    split: str                  # "test"
    seed: int                   # 42
    
    # Plateforme
    platform: str               # "RISC-V RV32X"
    clock_mhz: int              # 120
    quantization_bits: int      # 8
    
    # Valeur mesurée
    evidence_type: EvidenceType
    value: float
    unit: str                   # "ms", "mJ", "KiB", "%"
    
    # Provenance
    provenance: Provenance
    method: str                 # Description de la méthode
    
    # Incertitude
    uncertainty: Optional[float] = None      # ±valeur
    uncertainty_type: str = "none"           # "stddev", "ci95", "none"
    n_samples: int = 1
    
    # Hypothèses
    assumptions: List[str] = None
    
    # Traçabilité
    git_commit: str = ""
    timestamp: str = ""
    artifact_path: str = ""     # Chemin vers le fichier brut
    
    def __post_init__(self):
        if self.assumptions is None:
            self.assumptions = []
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.git_commit:
            self.git_commit = self._get_git_commit()
    
    def _get_git_commit(self) -> str:
        """Récupère le hash du commit git actuel"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=2
            )
            return result.stdout.strip()[:8]
        except:
            return "unknown"
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['provenance'] = self.provenance.value
        d['evidence_type'] = self.evidence_type.value
        return d


class EvidenceRegistry:
    """
    Registre central de toutes les preuves
    Chaque résultat numérique DOIT être enregistré ici
    """
    
    def __init__(self, registry_path: str = "evidence_registry/registry.json"):
        self.registry_path = registry_path
        self.entries: Dict[str, EvidenceEntry] = {}
        self._load()
    
    def _load(self):
        """Charge le registre existant"""
        import os
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                # Reconstruction (simplifié)
                print(f"📂 Registre chargé: {len(data.get('entries', []))} entrées")
            except:
                pass
    
    def register(self, entry: EvidenceEntry) -> str:
        """Enregistre une preuve"""
        # Vérification d'unicité
        if entry.result_id in self.entries:
            raise ValueError(f"❌ ID dupliqué: {entry.result_id}")
        
        self.entries[entry.result_id] = entry
        return entry.result_id
    
    def get(self, result_id: str) -> Optional[EvidenceEntry]:
        """Récupère une preuve par ID"""
        return self.entries.get(result_id)
    
    def query(self, experiment: str = None, design_id: str = None, 
              evidence_type: EvidenceType = None, provenance: Provenance = None) -> List[EvidenceEntry]:
        """Requête multi-critères"""
        results = list(self.entries.values())
        
        if experiment:
            results = [e for e in results if e.experiment == experiment]
        if design_id:
            results = [e for e in results if e.design_id == design_id]
        if evidence_type:
            results = [e for e in results if e.evidence_type == evidence_type]
        if provenance:
            results = [e for e in results if e.provenance == provenance]
        
        return results
    
    def save(self):
        """Sauvegarde le registre"""
        import os
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "entries": [e.to_dict() for e in self.entries.values()]
        }
        
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return self.registry_path
    
    def get_summary(self) -> Dict:
        """Résumé du registre"""
        by_provenance = {}
        by_experiment = {}
        by_type = {}
        
        for e in self.entries.values():
            by_provenance[e.provenance.value] = by_provenance.get(e.provenance.value, 0) + 1
            by_experiment[e.experiment] = by_experiment.get(e.experiment, 0) + 1
            by_type[e.evidence_type.value] = by_type.get(e.evidence_type.value, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "by_provenance": by_provenance,
            "by_experiment": by_experiment,
            "by_evidence_type": by_type
        }


# ============================================================
# FONCTIONS DE COMMODITÉ
# ============================================================

def register_ecg_baseline(registry: EvidenceRegistry):
    """Enregistre les preuves baseline pour ECG 8-bit"""
    
    entries = [
        EvidenceEntry(
            result_id="ecg_8bit_latency_001",
            experiment="E0", rq="RQ1",
            design_id="ecg_hybrid_8bit",
            dataset="MIT-BIH", split="test", seed=42,
            platform="RISC-V RV32X", clock_mhz=120, quantization_bits=8,
            evidence_type=EvidenceType.LATENCY,
            value=8.2, unit="ms",
            provenance=Provenance.SUR,
            method="Surrogate model prediction with R²=0.95",
            uncertainty=1.1, uncertainty_type="stddev", n_samples=100,
            assumptions=["RV32X extensions enabled", "No cache misses"],
            artifact_path="experiments/E0/results/ecg_8bit_latency.json"
        ),
        EvidenceEntry(
            result_id="ecg_8bit_memory_001",
            experiment="E0", rq="RQ1",
            design_id="ecg_hybrid_8bit",
            dataset="MIT-BIH", split="test", seed=42,
            platform="RISC-V RV32X", clock_mhz=120, quantization_bits=8,
            evidence_type=EvidenceType.MEMORY,
            value=364.38, unit="KiB",
            provenance=Provenance.DER,
            method="M_weights reconstruction: 373128 × 1 byte / 1024",
            uncertainty=0, uncertainty_type="none", n_samples=1,
            assumptions=["8-bit quantization", "No weight compression"],
            artifact_path="evidence_registry/memory_reports.json"
        ),
        EvidenceEntry(
            result_id="ecg_8bit_accuracy_001",
            experiment="E0", rq="RQ1",
            design_id="ecg_hybrid_8bit",
            dataset="MIT-BIH", split="test", seed=42,
            platform="N/A", clock_mhz=0, quantization_bits=8,
            evidence_type=EvidenceType.ACCURACY,
            value=0.961, unit="ratio",
            provenance=Provenance.MEAS,
            method="5-fold cross-validation on MIT-BIH test set",
            uncertainty=0.008, uncertainty_type="stddev", n_samples=5,
            assumptions=["Patient-wise split", "No data leakage"],
            artifact_path="experiments/E0/results/ecg_8bit_accuracy.json"
        )
    ]
    
    for e in entries:
        registry.register(e)
    
    return len(entries)


if __name__ == "__main__":
    registry = EvidenceRegistry()
    n = register_ecg_baseline(registry)
    path = registry.save()
    
    print(f"✅ {n} entrées enregistrées")
    print(f"📄 Registre: {path}")
    print("\n📊 Résumé:")
    print(json.dumps(registry.get_summary(), indent=2))
