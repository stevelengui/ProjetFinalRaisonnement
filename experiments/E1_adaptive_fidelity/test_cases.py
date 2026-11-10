"""
Test Cases - 40 cas contrôlés pour E1
Version CORRIGÉE : expected_verdict calculé depuis ground_truth
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class CaseCategory(Enum):
    INFEASIBLE = "infeasible"
    SAFE = "safe"
    BOUNDARY = "boundary"
    UNCERTAIN = "uncertain"
    PARETO_CLOSE = "pareto_close"
    CONFLICT = "conflict"


@dataclass
class TestCase:
    case_id: str
    category: CaseCategory
    description: str
    design_id: str
    metrics: Dict[str, float]
    hard_constraints: Dict[str, float]
    ground_truth: Dict[str, float]
    expected_verdict: str = "UNKNOWN"
    difficulty: str = "medium"
    notes: str = ""
    
    def compute_expected_verdict(self) -> str:
        """
        Calcule le verdict attendu à partir du GROUND TRUTH + contraintes
        C'est la RÉFÉRENCE pour comparer les politiques
        """
        for constraint, threshold in self.hard_constraints.items():
            if "max" in constraint:
                if "latency" in constraint:
                    gt_value = self.ground_truth.get("latency_ms", self.metrics.get("latency_ms", 0))
                elif "power" in constraint:
                    gt_value = self.ground_truth.get("power_mw", self.metrics.get("power_mw", 0))
                elif "memory" in constraint:
                    gt_value = self.ground_truth.get("memory_kb", self.metrics.get("memory_kb", 0))
                else:
                    gt_value = 0
                
                if gt_value > threshold:
                    return "FAIL"
            
            elif "min" in constraint:
                if "accuracy" in constraint:
                    gt_value = self.ground_truth.get("accuracy", self.metrics.get("accuracy", 0))
                elif "reliability" in constraint:
                    gt_value = self.ground_truth.get("reliability", self.metrics.get("reliability", 0))
                else:
                    gt_value = 0
                
                if gt_value < threshold:
                    return "FAIL"
        
        return "PASS"


# ============================================================
# 40 CAS CONTRÔLÉS (avec ground_truth cohérent)
# ============================================================

def get_all_test_cases() -> List[TestCase]:
    cases = [
        # ========== INFEASIBLE (7 cas) ==========
        TestCase(
            case_id="TC01", category=CaseCategory.INFEASIBLE,
            description="Latence hors budget",
            design_id="ecg_snn_2bit",
            metrics={"latency_ms": 45.0, "memory_kb": 6.0, "accuracy": 0.920},
            hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 48.0, "memory_kb": 6.0, "accuracy": 0.918}
        ),
        TestCase(
            case_id="TC02", category=CaseCategory.INFEASIBLE,
            description="Précision insuffisante",
            design_id="ecg_snn_2bit",
            metrics={"latency_ms": 12.4, "accuracy": 0.920},
            hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.98},
            ground_truth={"latency_ms": 12.6, "accuracy": 0.919}
        ),
        TestCase(
            case_id="TC03", category=CaseCategory.INFEASIBLE,
            description="Mémoire insuffisante",
            design_id="robot_slam_8bit",
            metrics={"latency_ms": 22.4, "memory_kb": 64.0, "accuracy": 0.890},
            hard_constraints={"memory_kib_max": 32.0, "accuracy_min": 0.88},
            ground_truth={"latency_ms": 22.8, "memory_kb": 66.5, "accuracy": 0.890}
        ),
        TestCase(
            case_id="TC04", category=CaseCategory.INFEASIBLE,
            description="Puissance trop élevée",
            design_id="auto_hybrid_8bit",
            metrics={"latency_ms": 18.6, "power_mw": 42.0, "accuracy": 0.902},
            hard_constraints={"power_mw_max": 20.0, "accuracy_min": 0.90},
            ground_truth={"latency_ms": 19.2, "power_mw": 43.5, "accuracy": 0.902}
        ),
        TestCase(
            case_id="TC05", category=CaseCategory.INFEASIBLE,
            description="Multiple violations",
            design_id="ecg_snn_2bit",
            metrics={"latency_ms": 30.0, "accuracy": 0.90},
            hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 32.0, "accuracy": 0.898}
        ),
        TestCase(
            case_id="TC06", category=CaseCategory.INFEASIBLE,
            description="Latence 2x hors budget",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 40.0, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 15.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 42.0, "accuracy": 0.946}
        ),
        TestCase(
            case_id="TC07", category=CaseCategory.INFEASIBLE,
            description="Précision insuffisante",
            design_id="vibration_qnn_4bit",
            metrics={"latency_ms": 15.2, "accuracy": 0.934},
            hard_constraints={"accuracy_min": 0.96},
            ground_truth={"latency_ms": 15.5, "accuracy": 0.932}
        ),
        
        # ========== SAFE (8 cas) - ground_truth bien dans les budgets ==========
        TestCase(
            case_id="TC08", category=CaseCategory.SAFE,
            description="Large marge sur toutes contraintes",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 8.2, "memory_kb": 24.0, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 20.0, "memory_kib_max": 64.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 8.4, "memory_kb": 24.5, "accuracy": 0.961}
        ),
        TestCase(
            case_id="TC09", category=CaseCategory.SAFE,
            description="Design dans le budget",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "memory_kb": 32.0, "accuracy": 0.958},
            hard_constraints={"latency_ms_max": 20.0, "memory_kib_max": 64.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 6.9, "memory_kb": 32.5, "accuracy": 0.958}
        ),
        TestCase(
            case_id="TC10", category=CaseCategory.SAFE,
            description="Latence excellente",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "memory_kb": 12.0, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 15.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 6.3, "memory_kb": 12.5, "accuracy": 0.948}
        ),
        TestCase(
            case_id="TC11", category=CaseCategory.SAFE,
            description="Safety-critical avec marge",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "accuracy": 0.948, "reliability": 0.90},
            hard_constraints={"latency_ms_max": 15.0, "accuracy_min": 0.94, "reliability_min": 0.85},
            ground_truth={"latency_ms": 6.3, "accuracy": 0.948, "reliability": 0.90}
        ),
        TestCase(
            case_id="TC12", category=CaseCategory.SAFE,
            description="Design idéal IoT",
            design_id="iot_snn_lowpower",
            metrics={"latency_ms": 18.6, "power_mw": 6.0, "accuracy": 0.890},
            hard_constraints={"latency_ms_max": 25.0, "power_mw_max": 10.0, "accuracy_min": 0.88},
            ground_truth={"latency_ms": 18.8, "power_mw": 6.2, "accuracy": 0.890}
        ),
        TestCase(
            case_id="TC13", category=CaseCategory.SAFE,
            description="Vibration sûre",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "accuracy": 0.958},
            hard_constraints={"latency_ms_max": 30.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 6.9, "accuracy": 0.958}
        ),
        TestCase(
            case_id="TC14", category=CaseCategory.SAFE,
            description="Large marge latence",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 8.2, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 30.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 8.4, "accuracy": 0.961}
        ),
        TestCase(
            case_id="TC15", category=CaseCategory.SAFE,
            description="Tout satisfait largement",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "memory_kb": 12.0, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 20.0, "memory_kib_max": 32.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 6.3, "memory_kb": 12.5, "accuracy": 0.948}
        ),
        
        # ========== BOUNDARY (7 cas) - ground_truth à la limite ==========
        TestCase(
            case_id="TC16", category=CaseCategory.BOUNDARY,
            description="Latence proche seuil (estimation basse, GT au-dessus)",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 19.0, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 20.5, "accuracy": 0.961},
            notes="Estimation 19 < 20, mais GT 20.5 > 20 → FAIL"
        ),
        TestCase(
            case_id="TC17", category=CaseCategory.BOUNDARY,
            description="Précision proche seuil (GT légèrement sous)",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "accuracy": 0.950},
            hard_constraints={"accuracy_min": 0.950, "latency_ms_max": 10.0},
            ground_truth={"latency_ms": 6.3, "accuracy": 0.9498},
            notes="Estimation 0.950 ≥ 0.950, mais GT 0.9498 < 0.950 → FAIL"
        ),
        TestCase(
            case_id="TC18", category=CaseCategory.BOUNDARY,
            description="Latence estimation sous seuil, GT dépasse",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 19.0, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 20.5, "accuracy": 0.961}
        ),
        TestCase(
            case_id="TC19", category=CaseCategory.BOUNDARY,
            description="Mémoire estimation sous seuil, GT dépasse",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "memory_kb": 45.0, "accuracy": 0.958},
            hard_constraints={"memory_kib_max": 48.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 6.9, "memory_kb": 49.5, "accuracy": 0.958}
        ),
        TestCase(
            case_id="TC20", category=CaseCategory.BOUNDARY,
            description="Puissance estimation au seuil, GT dépasse",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "power_mw": 19.5, "accuracy": 0.948},
            hard_constraints={"power_mw_max": 20.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 6.3, "power_mw": 20.8, "accuracy": 0.948}
        ),
        TestCase(
            case_id="TC21", category=CaseCategory.BOUNDARY,
            description="Précision estimation sous seuil",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "accuracy": 0.955},
            hard_constraints={"accuracy_min": 0.96},
            ground_truth={"latency_ms": 6.9, "accuracy": 0.943}
        ),
        TestCase(
            case_id="TC22", category=CaseCategory.BOUNDARY,
            description="Latence estimation légèrement au-dessus",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 11.5, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 10.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 11.8, "accuracy": 0.948}
        ),
        
        # ========== UNCERTAIN (6 cas) ==========
        TestCase(
            case_id="TC23", category=CaseCategory.UNCERTAIN,
            description="Estimation à la limite, GT inconnu",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 15.0, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 15.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 15.2, "accuracy": 0.948}
        ),
        TestCase(
            case_id="TC24", category=CaseCategory.UNCERTAIN,
            description="Incertitude précision",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "accuracy": 0.960},
            hard_constraints={"accuracy_min": 0.96},
            ground_truth={"latency_ms": 6.9, "accuracy": 0.9601}
        ),
        TestCase(
            case_id="TC25", category=CaseCategory.UNCERTAIN,
            description="Valeur estimée loin, GT différent",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 8.2, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 10.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 9.8, "accuracy": 0.960}
        ),
        TestCase(
            case_id="TC26", category=CaseCategory.UNCERTAIN,
            description="Modèle vieux, incertitude élevée",
            design_id="ecg_snn_2bit",
            metrics={"latency_ms": 15.0, "accuracy": 0.930},
            hard_constraints={"latency_ms_max": 20.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 15.5, "accuracy": 0.928}
        ),
        TestCase(
            case_id="TC27", category=CaseCategory.UNCERTAIN,
            description="Données incertaines",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 8.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 6.5, "accuracy": 0.948}
        ),
        TestCase(
            case_id="TC28", category=CaseCategory.UNCERTAIN,
            description="Estimation à la limite, GT dépasse",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 9.8, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 10.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 10.5, "accuracy": 0.960}
        ),
        
        # ========== PARETO-CLOSE (6 cas) ==========
        TestCase(
            case_id="TC29", category=CaseCategory.PARETO_CLOSE,
            description="Design Pareto proche seuil",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "power_mw": 19.0, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 10.0, "power_mw_max": 20.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 6.3, "power_mw": 19.5, "accuracy": 0.948}
        ),
        TestCase(
            case_id="TC30", category=CaseCategory.PARETO_CLOSE,
            description="Designs très proches",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 8.2, "power_mw": 28.0, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 10.0, "power_mw_max": 30.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 8.4, "power_mw": 28.5, "accuracy": 0.961}
        ),
        TestCase(
            case_id="TC31", category=CaseCategory.PARETO_CLOSE,
            description="Mémoire au bord",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "memory_kb": 32.0, "accuracy": 0.958},
            hard_constraints={"latency_ms_max": 7.0, "memory_kib_max": 32.5, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 6.9, "memory_kb": 32.8, "accuracy": 0.958}
        ),
        TestCase(
            case_id="TC32", category=CaseCategory.PARETO_CLOSE,
            description="Latence critique proche",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 6.5, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 6.3, "accuracy": 0.948}
        ),
        TestCase(
            case_id="TC33", category=CaseCategory.PARETO_CLOSE,
            description="Compromis latence/précision",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 8.2, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 8.5, "accuracy_min": 0.960},
            ground_truth={"latency_ms": 8.4, "accuracy": 0.9605}
        ),
        TestCase(
            case_id="TC34", category=CaseCategory.PARETO_CLOSE,
            description="Optimal à la limite",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "memory_kb": 32.0, "accuracy": 0.958},
            hard_constraints={"latency_ms_max": 7.0, "memory_kib_max": 33.0, "accuracy_min": 0.955},
            ground_truth={"latency_ms": 6.9, "memory_kb": 32.5, "accuracy": 0.958}
        ),
        
        # ========== CONFLICT (6 cas) ==========
        TestCase(
            case_id="TC35", category=CaseCategory.CONFLICT,
            description="Surrogate vs analytique divergents",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 8.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 6.3, "accuracy": 0.948}
        ),
        TestCase(
            case_id="TC36", category=CaseCategory.CONFLICT,
            description="Deux sources en conflit",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "accuracy": 0.958},
            hard_constraints={"latency_ms_max": 7.0, "accuracy_min": 0.955},
            ground_truth={"latency_ms": 7.5, "accuracy": 0.957}
        ),
        TestCase(
            case_id="TC37", category=CaseCategory.CONFLICT,
            description="Précision limite",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 10.0, "accuracy_min": 0.95},
            ground_truth={"latency_ms": 6.3, "accuracy": 0.947}
        ),
        TestCase(
            case_id="TC38", category=CaseCategory.CONFLICT,
            description="Budget vs qualité",
            design_id="ecg_hybrid_8bit",
            metrics={"latency_ms": 8.2, "power_mw": 28.0, "accuracy": 0.961},
            hard_constraints={"latency_ms_max": 10.0, "power_mw_max": 25.0, "accuracy_min": 0.96},
            ground_truth={"latency_ms": 8.4, "power_mw": 28.5, "accuracy": 0.961}
        ),
        TestCase(
            case_id="TC39", category=CaseCategory.CONFLICT,
            description="Conflit latence exact vs estimé",
            design_id="ecg_hybrid_4bit",
            metrics={"latency_ms": 6.2, "accuracy": 0.948},
            hard_constraints={"latency_ms_max": 6.0, "accuracy_min": 0.94},
            ground_truth={"latency_ms": 6.3, "accuracy": 0.948}
        ),
        TestCase(
            case_id="TC40", category=CaseCategory.CONFLICT,
            description="Incertitude + limite",
            design_id="vibration_hybrid_8bit",
            metrics={"latency_ms": 6.8, "accuracy": 0.958},
            hard_constraints={"latency_ms_max": 7.0, "accuracy_min": 0.955},
            ground_truth={"latency_ms": 7.2, "accuracy": 0.957}
        ),
    ]
    
    # ⭐ Calculer automatiquement expected_verdict depuis ground_truth
    for case in cases:
        case.expected_verdict = case.compute_expected_verdict()
    
    return cases


def get_cases_by_category() -> Dict[str, List[TestCase]]:
    all_cases = get_all_test_cases()
    groups = {}
    for category in CaseCategory:
        groups[category.value] = [c for c in all_cases if c.category == category]
    return groups


if __name__ == "__main__":
    cases = get_all_test_cases()
    print(f"✅ {len(cases)} cas chargés")
    
    # Compter les verdicts
    pass_count = sum(1 for c in cases if c.expected_verdict == "PASS")
    fail_count = sum(1 for c in cases if c.expected_verdict == "FAIL")
    print(f"   PASS: {pass_count}, FAIL: {fail_count}")
    
    groups = get_cases_by_category()
    for cat, cat_cases in groups.items():
        pass_c = sum(1 for c in cat_cases if c.expected_verdict == "PASS")
        fail_c = sum(1 for c in cat_cases if c.expected_verdict == "FAIL")
        print(f"   {cat}: {len(cat_cases)} cas (PASS={pass_c}, FAIL={fail_c})")
