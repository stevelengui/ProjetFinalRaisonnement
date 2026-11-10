#!/usr/bin/env python3
"""
Correction P1-1 : Provenance E0-E7
Crée un registre complet pour chaque expérience
"""

import os
import json
import hashlib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "artifacts/provenance")
os.makedirs(OUTPUT_DIR, exist_ok=True)


EXPERIMENTS = {
    "E0": {
        "name": "Context-to-Contract (RQ1)",
        "cases_file": "experiments/E0_context_to_contract/scenarios.py",
        "n_cases": 30,
        "seeds": [42],
        "oracle": "ground_truth_contracts.py (manual verification)",
        "script": "scripts/run_e0.sh",
        "denominators": {
            "contract_accuracy": 30,
            "primary_objective_accuracy": 30,
            "missing_info_detection": 5,
        },
        "results_file": "experiments/E0_context_to_contract/results/e0_results.json"
    },
    "E1": {
        "name": "Adaptive Evaluation-Fidelity (RQ2)",
        "cases_file": "experiments/E1_adaptive_fidelity/test_cases.py",
        "n_cases": 40,
        "seeds": [42],
        "oracle": "expected_verdict (computed from ground_truth)",
        "script": "scripts/run_e1.sh",
        "denominators": {
            "agreement_rate": 40,
            "cost": 40,
            "critical_accuracy": 19,
        },
        "results_file": "experiments/E1_adaptive_fidelity/results/e1_results.json"
    },
    "E2": {
        "name": "Lifecycle Replay (RQ5)",
        "cases_file": "experiments/E2_lifecycle_replay/lifecycle_perturbations.py",
        "n_cases": 10,
        "seeds": [42],
        "oracle": "expected_intervention",
        "script": "scripts/run_e2.sh",
        "denominators": {
            "intervention_correctness": 10,
        },
        "results_file": "experiments/E2_lifecycle_replay/results/e2_results.json"
    },
    "E3": {
        "name": "Fault Injection (RQ3)",
        "cases_file": "experiments/E3_fault_injection/candidate_designs.py",
        "n_cases": 800,
        "seeds": [42],
        "oracle": "nominal_accuracy + fault_sensitivity",
        "script": "scripts/run_e3.sh",
        "denominators": {
            "p_sdc": 200,
            "delta_a_f": 200,
        },
        "results_file": "experiments/E3_fault_injection/results/e3_results.json"
    },
    "E4": {
        "name": "Domain-Shift (RQ3)",
        "cases_file": "experiments/E4_domain_shift/domain_shift_scenarios.py",
        "n_cases": 6,
        "seeds": [42],
        "oracle": "expected_intervention",
        "script": "scripts/run_e4.sh",
        "denominators": {
            "method_correctness": 6,
        },
        "results_file": "experiments/E4_domain_shift/results/e4_results.json"
    },
    "E5": {
        "name": "Security (RQ3)",
        "cases_file": "experiments/E5_security/security_designs.py",
        "n_cases": 25,
        "seeds": [42],
        "oracle": "asr_threshold (0.20)",
        "script": "scripts/run_e5.sh",
        "denominators": {
            "decision_correctness": 25,
        },
        "results_file": "experiments/E5_security/results/e5_results.json"
    },
    "E6": {
        "name": "Decision Records (RQ4)",
        "cases_file": "experiments/E6_decision_records/decision_record.py",
        "n_cases": 3,
        "seeds": [42],
        "oracle": "counterfactual_tests",
        "script": "scripts/run_e6.sh",
        "denominators": {
            "audit_score": 6,
        },
        "results_file": "experiments/E6_decision_records/results/e6_results.json"
    },
    "E7": {
        "name": "Ablation (Cross-RQ)",
        "cases_file": "experiments/E7_ablation/ablation_configs.py",
        "n_cases": 30,
        "seeds": [42],
        "oracle": "dcr_full (0.94)",
        "script": "scripts/run_e7.sh",
        "denominators": {
            "dcr": 30,
        },
        "results_file": "experiments/E7_ablation/results/e7_results.json"
    },
}


def compute_file_hash(filepath):
    """Calcule le hash SHA256 d'un fichier"""
    if not os.path.exists(filepath):
        return "NOT_FOUND"

    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def generate_registry():
    """Génère le registre de provenance"""

    print("=" * 70)
    print("📊 GÉNÉRATION DU REGISTRE DE PROVENANCE (P1-1)")
    print("=" * 70)

    registry = {
        "generated_at": datetime.now().isoformat(),
        "framework": "LLM-NAS AutoCoDesign",
        "version": "2.1.0",
        "experiments": {}
    }

    for exp_id, info in EXPERIMENTS.items():
        exp_data = {
            "name": info["name"],
            "cases_file": info["cases_file"],
            "cases_file_hash": compute_file_hash(os.path.join(BASE_DIR, info["cases_file"])),
            "n_cases": info["n_cases"],
            "seeds": info["seeds"],
            "oracle": info["oracle"],
            "script": info["script"],
            "script_hash": compute_file_hash(os.path.join(BASE_DIR, info["script"])),
            "denominators": info["denominators"],
            "results_file": info["results_file"],
            "results_exists": os.path.exists(os.path.join(BASE_DIR, info["results_file"]))
        }
        registry["experiments"][exp_id] = exp_data
        status = "✅" if exp_data["results_exists"] else "⚠️"
        print(f"{status} {exp_id}: {info['name']} ({info['n_cases']} cas)")

    # Sauvegarder
    output_path = os.path.join(OUTPUT_DIR, "provenance_registry.json")
    with open(output_path, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"\n💾 Registre: {output_path}")

    # Générer aussi un rapport lisible
    report_path = os.path.join(OUTPUT_DIR, "PROVENANCE_REPORT.md")
    with open(report_path, 'w') as f:
        f.write("# Registre de Provenance E0-E7\n\n")
        f.write(f"Généré: {datetime.now().isoformat()}\n\n")
        f.write("## Résumé\n\n")
        f.write("| Exp | Nom | Cas | Seeds | Oracle |\n")
        f.write("|-----|-----|-----|-------|--------|\n")
        for exp_id, exp_data in registry["experiments"].items():
            f.write(f"| {exp_id} | {exp_data['name']} | {exp_data['n_cases']} | "
                   f"{exp_data['seeds']} | {exp_data['oracle'][:30]}... |\n")
        f.write("\n## Fichiers sources\n\n")
        for exp_id, exp_data in registry["experiments"].items():
            f.write(f"### {exp_id}\n")
            f.write(f"- Cases: `{exp_data['cases_file']}` (hash: {exp_data['cases_file_hash']})\n")
            f.write(f"- Script: `{exp_data['script']}` (hash: {exp_data['script_hash']})\n")
            f.write(f"- Results: `{exp_data['results_file']}` "
                   f"({'✅' if exp_data['results_exists'] else '⚠️ missing'})\n\n")

    print(f"📄 Rapport: {report_path}")

    return registry


if __name__ == "__main__":
    generate_registry()
