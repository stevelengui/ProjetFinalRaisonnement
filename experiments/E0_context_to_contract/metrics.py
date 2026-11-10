"""
Metrics - Métriques E0
Mesure : précision du contrat, complétude, conséquence décisionnelle, clarifications
"""

from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class E0Metrics:
    """Métriques de l'expérience E0"""
    
    # Précision du contrat
    contract_accuracy: float = 0.0          # Ratio de champs corrects
    primary_objective_accuracy: float = 0.0  # Ratio d'objectif principal correct
    constraints_accuracy: float = 0.0        # Ratio de contraintes correctes
    
    # Complétude
    missing_info_detection_rate: float = 0.0  # Ratio d'info manquante détectée
    false_positive_rate: float = 0.0          # Ratio de fausses détections
    
    # Conséquence décisionnelle
    decision_change_rate: float = 0.0         # Ratio de contextes où décision change
    reliability_transition_valid: bool = False  # Fiabilité préférence → hard
    
    # Clarifications
    clarification_requests: int = 0
    blocking_clarifications: int = 0
    warning_clarifications: int = 0
    
    # Compteurs
    total_contexts: int = 0
    contexts_with_changes: int = 0
    contexts_complete: int = 0


class MetricsComputer:
    """Calcule les métriques E0"""
    
    def compute_contract_accuracy(self, generated: Dict, 
                                 reference: Dict) -> float:
        """
        Calcule la précision du contrat généré vs référence
        """
        if not reference:
            return 0.0
        
        correct_fields = 0
        total_fields = 0
        
        # Objectif principal
        total_fields += 1
        if generated.get("primary_objective") == reference.get("primary_objective"):
            correct_fields += 1
        
        # Contraintes dures
        gen_constraints = set(generated.get("hard_constraints", {}).keys())
        ref_constraints = set(reference.get("hard_constraints", {}).keys())
        
        if ref_constraints:
            total_fields += 1
            if gen_constraints == ref_constraints:
                correct_fields += 1
        
        return correct_fields / total_fields if total_fields > 0 else 0.0
    
    def compute_missing_detection(self, context, 
                                 clarification_request) -> Dict:
        """
        Vérifie si l'info manquante a été correctement détectée
        """
        actual_missing = set(context.missing_info)
        detected_missing = set(clarification_request.missing_fields) if clarification_request else set()
        
        # Vrais positifs : manquants détectés
        tp = len(actual_missing & detected_missing)
        # Faux négatifs : manquants non détectés
        fn = len(actual_missing - detected_missing)
        # Faux positifs : non-manquants signalés
        fp = len(detected_missing - actual_missing)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        
        return {
            "true_positives": tp,
            "false_negatives": fn,
            "false_positives": fp,
            "precision": precision,
            "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        }
    
    def aggregate_metrics(self, results: List[Dict]) -> E0Metrics:
        """Agrège les métriques sur tous les contextes"""
        metrics = E0Metrics()
        metrics.total_contexts = len(results)
        
        if not results:
            return metrics
        
        # Précision
        accuracies = [r.get("contract_accuracy", 0) for r in results]
        metrics.contract_accuracy = sum(accuracies) / len(accuracies)
        
        objective_accs = [r.get("primary_objective_correct", False) for r in results]
        metrics.primary_objective_accuracy = sum(objective_accs) / len(objective_accs)
        
        # Complétude
        tp_total = sum(r.get("tp", 0) for r in results)
        fp_total = sum(r.get("fp", 0) for r in results)
        fn_total = sum(r.get("fn", 0) for r in results)
        
        if (tp_total + fn_total) > 0:
            metrics.missing_info_detection_rate = tp_total / (tp_total + fn_total)
        if (tp_total + fp_total) > 0:
            metrics.false_positive_rate = fp_total / (tp_total + fp_total)
        
        # Clarifications
        metrics.clarification_requests = sum(1 for r in results if r.get("clarification_requested"))
        metrics.blocking_clarifications = sum(1 for r in results if r.get("clarification_severity") == "blocking")
        metrics.warning_clarifications = sum(1 for r in results if r.get("clarification_severity") == "warning")
        
        # Conséquence décisionnelle
        changes = [r.get("decision_changed", False) for r in results]
        metrics.contexts_with_changes = sum(changes)
        if results:
            metrics.decision_change_rate = sum(changes) / len(changes)
        
        # Complétude des contextes
        complete = sum(1 for r in results if not r.get("missing_info", []))
        metrics.contexts_complete = complete
        
        return metrics
    
    def to_dict(self, metrics: E0Metrics) -> Dict:
        """Convertit les métriques en dict"""
        return {
            "contract_accuracy": round(metrics.contract_accuracy, 3),
            "primary_objective_accuracy": round(metrics.primary_objective_accuracy, 3),
            "missing_info_detection_rate": round(metrics.missing_info_detection_rate, 3),
            "false_positive_rate": round(metrics.false_positive_rate, 3),
            "decision_change_rate": round(metrics.decision_change_rate, 3),
            "reliability_transition_valid": metrics.reliability_transition_valid,
            "clarification_requests": metrics.clarification_requests,
            "blocking_clarifications": metrics.blocking_clarifications,
            "warning_clarifications": metrics.warning_clarifications,
            "total_contexts": metrics.total_contexts,
            "contexts_with_changes": metrics.contexts_with_changes,
            "contexts_complete": metrics.contexts_complete,
        }
