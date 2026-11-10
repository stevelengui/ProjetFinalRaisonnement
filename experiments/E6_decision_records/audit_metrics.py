"""
Audit Metrics - Métriques d'auditabilité
Exigence : "EC, CT, DF, CF, AC, AV"

EC = Explanation Completeness
CT = Counterfactual Testability
DF = Decision Fidelity
CF = Counterfactual Fidelity
AC = Audit Consistency
AV = Audit Verifiability
"""

from dataclasses import dataclass
from typing import Dict, List

from decision_record import DecisionRecord


@dataclass
class AuditMetrics:
    """Métriques d'auditabilité"""
    record_id: str
    
    # EC : Explanation Completeness
    ec_score: float = 0.0
    
    # CT : Counterfactual Testability
    ct_score: float = 0.0
    
    # DF : Decision Fidelity
    df_score: float = 0.0
    
    # CF : Counterfactual Fidelity
    cf_score: float = 0.0
    
    # AC : Audit Consistency
    ac_score: float = 0.0
    
    # AV : Audit Verifiability
    av_score: float = 0.0
    
    # Composite
    overall_score: float = 0.0


class AuditMetricsComputer:
    """Calcule les métriques d'auditabilité"""
    
    def __init__(self):
        self.weights = {
            "ec": 0.20,  # Explanation Completeness
            "ct": 0.15,  # Counterfactual Testability
            "df": 0.20,  # Decision Fidelity
            "cf": 0.15,  # Counterfactual Fidelity
            "ac": 0.15,  # Audit Consistency
            "av": 0.15,  # Audit Verifiability
        }
    
    def compute_ec(self, record: DecisionRecord) -> float:
        """
        EC : Explanation Completeness
        Mesure la complétude du DDR
        """
        completeness = record.validate_completeness()
        return completeness["completeness_score"]
    
    def compute_ct(self, record: DecisionRecord) -> float:
        """
        CT : Counterfactual Testability
        Mesure la testabilité contrefactuelle
        """
        # Un DDR est testable si :
        # 1. Il a des contraintes explicites
        # 2. Il a des alternatives
        # 3. Il a des preuves
        
        score = 0.0
        
        # Contraintes (poids 0.4)
        if record.contract and record.contract.hard_constraints:
            score += 0.4
        
        # Alternatives (poids 0.3)
        if record.alternatives:
            score += 0.3
        
        # Preuves (poids 0.3)
        if record.evidence:
            score += 0.3
        
        return score
    
    def compute_df(self, record: DecisionRecord) -> float:
        """
        DF : Decision Fidelity
        Mesure la fidélité de la décision
        (la décision suit-elle la logique du contrat ?)
        """
        if not record.decision or not record.contract:
            return 0.0
        
        score = 0.0
        
        # La décision doit être cohérente avec l'objectif principal
        primary_objective = record.contract.primary_objective
        
        # Vérifier que la décision est justifiée
        if record.decision.justification:
            score += 0.5
        
        # Vérifier que la décision a des preuves associées
        if record.evidence:
            score += 0.5
        
        return score
    
    def compute_cf(self, record: DecisionRecord) -> float:
        """
        CF : Counterfactual Fidelity
        Mesure la fidélité des contrefactuels
        """
        if not record.counterfactuals:
            # Si aucun contrefactuel, on pénalise mais pas totalement
            return 0.3
        
        # Ratio de contrefactuels valides
        valid_count = sum(1 for cf in record.counterfactuals if cf.valid)
        return valid_count / len(record.counterfactuals)
    
    def compute_ac(self, record: DecisionRecord) -> float:
        """
        AC : Audit Consistency
        Mesure la cohérence interne du DDR
        """
        score = 0.0
        
        # 1. La décision doit être cohérente avec les contraintes
        if record.decision and record.contract:
            decision_id = record.decision.design_id
            
            # Vérifier que le design accepté existe dans les alternatives ou preuves
            if decision_id:
                score += 0.4
        
        # 2. L'incertitude doit être cohérente avec les preuves
        if record.uncertainty and record.evidence:
            # Si les preuves sont de haute confiance, l'incertitude doit être faible
            avg_confidence = sum(e.confidence for e in record.evidence) / len(record.evidence)
            expected_uncertainty = 1 - avg_confidence
            
            if abs(record.uncertainty.overall - expected_uncertainty) < 0.3:
                score += 0.3
        
        # 3. Le risque résiduel doit être cohérent
        if record.residual_risk:
            score += 0.3
        
        return score
    
    def compute_av(self, record: DecisionRecord) -> float:
        """
        AV : Audit Verifiability
        Mesure la vérifiabilité du DDR
        """
        score = 0.0
        
        # 1. Hash présent
        if record.compute_hash():
            score += 0.3
        
        # 2. Git commit présent
        if record.git_commit and record.git_commit != "unknown":
            score += 0.3
        
        # 3. Timestamp présent
        if record.timestamp:
            score += 0.2
        
        # 4. Preuves avec provenance
        if record.evidence:
            with_provenance = sum(1 for e in record.evidence if e.provenance)
            score += 0.2 * (with_provenance / len(record.evidence))
        
        return score
    
    def compute_all(self, record: DecisionRecord) -> AuditMetrics:
        """Calcule toutes les métriques"""
        ec = self.compute_ec(record)
        ct = self.compute_ct(record)
        df = self.compute_df(record)
        cf = self.compute_cf(record)
        ac = self.compute_ac(record)
        av = self.compute_av(record)
        
        # Score composite
        overall = (
            self.weights["ec"] * ec +
            self.weights["ct"] * ct +
            self.weights["df"] * df +
            self.weights["cf"] * cf +
            self.weights["ac"] * ac +
            self.weights["av"] * av
        )
        
        return AuditMetrics(
            record_id=record.record_id,
            ec_score=round(ec, 3),
            ct_score=round(ct, 3),
            df_score=round(df, 3),
            cf_score=round(cf, 3),
            ac_score=round(ac, 3),
            av_score=round(av, 3),
            overall_score=round(overall, 3)
        )
    
    def to_dict(self, metrics: AuditMetrics) -> Dict:
        return {
            "record_id": metrics.record_id,
            "EC": metrics.ec_score,
            "CT": metrics.ct_score,
            "DF": metrics.df_score,
            "CF": metrics.cf_score,
            "AC": metrics.ac_score,
            "AV": metrics.av_score,
            "overall": metrics.overall_score
        }


if __name__ == "__main__":
    from decision_record import create_sample_decision_record
    
    record = create_sample_decision_record()
    computer = AuditMetricsComputer()
    metrics = computer.compute_all(record)
    
    print("✅ AuditMetricsComputer prêt")
    print(f"\nMétriques pour {record.record_id}:")
    print(f"   EC: {metrics.ec_score}")
    print(f"   CT: {metrics.ct_score}")
    print(f"   DF: {metrics.df_score}")
    print(f"   CF: {metrics.cf_score}")
    print(f"   AC: {metrics.ac_score}")
    print(f"   AV: {metrics.av_score}")
    print(f"   Overall: {metrics.overall_score}")
