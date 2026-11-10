"""
Explanation Generator - Génération d'explications
Exigence : "Design Decision Record auditable avec explication complète"
"""

from typing import Dict, List
from decision_record import DecisionRecord


class ExplanationGenerator:
    """Génère des explications textuelles à partir d'un DDR"""
    
    def generate_full_explanation(self, record: DecisionRecord) -> str:
        """Génère l'explication complète du DDR"""
        lines = [
            "=" * 70,
            f"DESIGN DECISION RECORD - {record.record_id}",
            "=" * 70,
            f"Design: {record.design_id}",
            f"Timestamp: {record.timestamp}",
            f"Hash: {record.compute_hash()}",
            "",
            "=" * 70,
            "C - CONTEXTE",
            "=" * 70,
        ]
        
        if record.context:
            ctx = record.context
            lines.extend([
                f"Context ID: {ctx.context_id}",
                f"Domain: {ctx.domain}",
                f"Environment: {ctx.environment}",
                f"Safety Relevant: {ctx.safety_relevant}",
                f"Requirements: {ctx.requirements}",
            ])
        
        lines.extend([
            "",
            "=" * 70,
            "Γ - CONTRAT",
            "=" * 70,
        ])
        
        if record.contract:
            c = record.contract
            lines.extend([
                f"Primary Objective: {c.primary_objective}",
                "Hard Constraints:",
            ])
            for k, v in c.hard_constraints.items():
                lines.append(f"  - {k}: {v}")
            lines.append("Soft Constraints:")
            for k, v in c.soft_constraints.items():
                lines.append(f"  - {k}: {v}")
        
        lines.extend([
            "",
            "=" * 70,
            "A - ACTIONS",
            "=" * 70,
        ])
        
        for action in record.actions:
            lines.append(f"[{action.action_id}] {action.action_type}: {action.name}")
            lines.append(f"   Rationale: {action.rationale}")
        
        lines.extend([
            "",
            "=" * 70,
            "E - PREUVES",
            "=" * 70,
        ])
        
        for ev in record.evidence:
            lines.append(f"[{ev.evidence_id}] {ev.evidence_type}: {ev.value}")
            lines.append(f"   Provenance: {ev.provenance}")
            lines.append(f"   Confidence: {ev.confidence:.2%}")
            lines.append(f"   Source: {ev.source}")
        
        lines.extend([
            "",
            "=" * 70,
            "U - INCERTITUDE",
            "=" * 70,
            f"Overall Uncertainty: {record.uncertainty.overall:.2%}",
        ])
        for k, v in record.uncertainty.per_metric.items():
            lines.append(f"  - {k}: {v:.2%}")
        
        lines.extend([
            "",
            "=" * 70,
            "R - RISQUE RÉSIDUEL",
            "=" * 70,
            f"Overall Risk: {record.residual_risk.overall:.2%}",
            f"Acceptable: {record.residual_risk.acceptable}",
        ])
        
        lines.extend([
            "",
            "=" * 70,
            "Alt - ALTERNATIVES",
            "=" * 70,
        ])
        
        for alt in record.alternatives:
            lines.append(f"[{alt.design_id}]")
            lines.append(f"   Rejected because: {alt.reason_rejected}")
            for k, v in alt.metrics.items():
                lines.append(f"   - {k}: {v}")
        
        lines.extend([
            "",
            "=" * 70,
            "Dec - DÉCISION",
            "=" * 70,
        ])
        
        if record.decision:
            lines.extend([
                f"Selected Design: {record.decision.design_id}",
                f"Decision: {record.decision.decision}",
                f"Justification: {record.decision.justification}",
            ])
        
        lines.extend([
            "",
            "=" * 70,
            "CF - CONTREFAICTUELS",
            "=" * 70,
        ])
        
        for cf in record.counterfactuals:
            lines.append(f"[{cf.counterfactual_id}] {cf.description}")
            lines.append(f"   Original: {cf.original_outcome}")
            lines.append(f"   Counterfactual: {cf.counterfactual_outcome}")
            lines.append(f"   Condition changed: {cf.changed_condition}")
            lines.append(f"   Valid: {cf.valid}")
        
        lines.extend([
            "",
            "=" * 70,
            "FIN DU DDR",
            "=" * 70,
        ])
        
        return "\n".join(lines)
    
    def generate_concise_explanation(self, record: DecisionRecord) -> str:
        """Génère une explication concise"""
        if not record.decision:
            return "Aucune décision enregistrée"
        
        lines = [
            f"Design {record.design_id} : {record.decision.decision}",
            f"Raison: {record.decision.justification}",
        ]
        
        if record.alternatives:
            lines.append(f"\nAlternatives rejetées:")
            for alt in record.alternatives[:3]:
                lines.append(f"  - {alt.design_id}: {alt.reason_rejected}")
        
        return "\n".join(lines)
    
    def generate_audit_report(self, record: DecisionRecord, 
                            metrics: Dict) -> str:
        """Génère un rapport d'audit complet"""
        lines = [
            self.generate_full_explanation(record),
            "",
            "=" * 70,
            "MÉTRIQUES D'AUDIT",
            "=" * 70,
            f"EC (Explanation Completeness): {metrics.get('EC', 0):.3f}",
            f"CT (Counterfactual Testability): {metrics.get('CT', 0):.3f}",
            f"DF (Decision Fidelity): {metrics.get('DF', 0):.3f}",
            f"CF (Counterfactual Fidelity): {metrics.get('CF', 0):.3f}",
            f"AC (Audit Consistency): {metrics.get('AC', 0):.3f}",
            f"AV (Audit Verifiability): {metrics.get('AV', 0):.3f}",
            f"Overall Score: {metrics.get('overall', 0):.3f}",
            "=" * 70,
        ]
        
        return "\n".join(lines)


if __name__ == "__main__":
    from decision_record import create_sample_decision_record
    from audit_metrics import AuditMetricsComputer
    
    record = create_sample_decision_record()
    generator = ExplanationGenerator()
    computer = AuditMetricsComputer()
    metrics = computer.to_dict(computer.compute_all(record))
    
    print(generator.generate_audit_report(record, metrics))
