"""
Meta Controller v2 - Contrôleur méta-opérationnel complet
Intègre TOUS les modules de Phase 1
"""

from typing import Dict, List, Any, Optional
from dataclasses import asdict
from datetime import datetime

from .state_space import (
    MetaReasonerState, DesignContract, DesignCandidate,
    EvidenceSet, UncertaintyState, ResidualRisk, BudgetState
)
from .tri_state_logic import TriStateEvaluator, TriState
from .evi_calculator import EVICalculator
from .action_engine import ActionEngine, EvidenceAction, DecisionAction, LifecycleAction
from .conflict_resolver import ConflictResolver, Evidence
from .lifecycle_manager import LifecycleManager, DriftDetection
from .transition_logger import TransitionLogger
from .evidence_registry import EvidenceRegistry


class MetaControllerV2:
    """
    Contrôleur méta-opérationnel déterministe
    Implémente le cycle complet : contexte → contrat → preuves → décision → assurance → lifecycle
    """
    
    def __init__(self, evidence_registry: EvidenceRegistry = None):
        # Sous-systèmes
        self.tri_state = TriStateEvaluator()
        self.evi_calc = EVICalculator(lambda_cost=1.0, lambda_time=0.5)
        self.action_engine = ActionEngine()
        self.conflict_resolver = ConflictResolver()
        self.lifecycle_manager = LifecycleManager()
        self.transition_logger = TransitionLogger()
        self.evidence_registry = evidence_registry or EvidenceRegistry()
        
        # État courant
        self.current_state: Optional[MetaReasonerState] = None
    
    def reason(self, context: Dict) -> Dict:
        """
        Exécute le méta-raisonnement complet
        """
        print("=" * 70)
        print("🧠 MÉTA-RAISONNEMENT DÉTERMINISTE")
        print("=" * 70)
        
        # 1. Initialisation de l'état
        contract = self._formulate_contract(context)
        state = MetaReasonerState(
            state_id=f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            contract=contract
        )
        self.current_state = state
        
        # 2. Exploration des candidats
        self._explore_candidates(state)
        
        # 3. Collecte des preuves
        self._collect_evidence(state)
        
        # 4. Évaluation tri-état
        feasibility = self._evaluate_feasibility(state)
        
        # 5. Gestion des conflits
        self._resolve_conflicts(state)
        
        # 6. Décision
        decision = self._make_decision(state, feasibility)
        
        # 7. Résumé
        result = {
            "state": state.to_dict(),
            "feasibility": feasibility,
            "decision": decision,
            "action_history": self.action_engine.get_action_history(),
            "transition_history": self.transition_logger.get_history()
        }
        
        print(f"\n✅ Décision: {decision['decision']}")
        print(f"   Design: {decision.get('selected_design_id', 'N/A')}")
        print(f"   Raison: {decision['rationale']}")
        
        return result
    
    def _formulate_contract(self, context: Dict) -> DesignContract:
        """Étape 1 : Formuler le contrat depuis le contexte"""
        print("\n[1/7] Formulation du contrat...")
        
        domain = context.get('domain', 'industrial')
        
        if domain == 'medical':
            contract = DesignContract(
                context_id=f"ctx_{domain}_{datetime.now().strftime('%H%M%S')}",
                primary_objective="maximize_accuracy",
                hard_constraints={
                    "latency_ms": context.get('max_latency_ms', 20.0),
                    "memory_kb": context.get('max_memory_kb', 512.0),
                    "accuracy": context.get('min_accuracy', 0.95),
                    "delta_t_max_c": 5.0
                },
                soft_constraints={
                    "energy_mj": context.get('max_power_mw', 50.0) * 0.1
                }
            )
        else:
            contract = DesignContract(
                context_id=f"ctx_{domain}_{datetime.now().strftime('%H%M%S')}",
                primary_objective="minimize_latency",
                hard_constraints={
                    "latency_ms": context.get('max_latency_ms', 15.0),
                    "memory_kb": context.get('max_memory_kb', 256.0),
                    "accuracy": context.get('min_accuracy', 0.93),
                    "delta_t_max_c": 7.0
                },
                soft_constraints={}
            )
        
        print(f"   Contrat: {contract.context_id}")
        print(f"   Objectif: {contract.primary_objective}")
        
        return contract
    
    def _explore_candidates(self, state: MetaReasonerState):
        """Étape 2 : Explorer les candidats designs"""
        print("\n[2/7] Exploration des candidats...")
        
        from llm_nas.real_designs import get_designs_by_domain
        
        domain = state.contract.context_id.split('_')[1]
        designs = get_designs_by_domain(domain)
        
        for d in designs:
            candidate = DesignCandidate(
                design_id=d['id'],
                parameters=d['algorithm'],
                metrics=d['metrics']
            )
            state.candidates.append(candidate)
        
        print(f"   {len(state.candidates)} candidats explorés")
    
    def _collect_evidence(self, state: MetaReasonerState):
        """Étape 3 : Collecter les preuves (rapide)"""
        print("\n[3/7] Collecte des preuves (basse fidélité)...")
        
        for candidate in state.candidates:
            # Preuve latence
            action = self.action_engine.eval_low_fidelity(
                candidate.design_id,
                f"Évaluation initiale pour {candidate.design_id}"
            )
            
            # Enregistrer dans l'evidence set
            state.evidence.add(
                evidence_id=f"lat_{candidate.design_id}",
                evidence_type="latency"
            )
            state.evidence.add(
                evidence_id=f"mem_{candidate.design_id}",
                evidence_type="memory"
            )
            state.evidence.add(
                evidence_id=f"acc_{candidate.design_id}",
                evidence_type="accuracy"
            )
        
        print(f"   {len(state.evidence.evidence_ids)} preuves collectées")
        print(f"   Couverture: {state.evidence.coverage_score:.0%}")
    
    def _evaluate_feasibility(self, state: MetaReasonerState) -> Dict:
        """Étape 4 : Évaluation tri-état"""
        print("\n[4/7] Évaluation de la faisabilité (tri-état)...")
        
        all_checks = []
        for candidate in state.candidates:
            checks = [
                self.tri_state.check_constraint(
                    f"{candidate.design_id}_latency",
                    candidate.metrics.get('latency_ms'),
                    state.contract.hard_constraints.get('latency_ms', 20),
                    "max"
                ),
                self.tri_state.check_constraint(
                    f"{candidate.design_id}_memory",
                    candidate.metrics.get('memory_kb'),
                    state.contract.hard_constraints.get('memory_kb', 512),
                    "max"
                ),
                self.tri_state.check_constraint(
                    f"{candidate.design_id}_accuracy",
                    candidate.metrics.get('accuracy'),
                    state.contract.hard_constraints.get('accuracy', 0.95),
                    "min"
                )
            ]
            
            # Agrégation par candidat
            candidate_result = self.tri_state.aggregate_feasibility(checks)
            candidate.feasibility = candidate_result['overall']
            all_checks.extend(checks)
            
            print(f"   {candidate.design_id}: {candidate.feasibility}")
        
        return self.tri_state.aggregate_feasibility(all_checks)
    
    def _resolve_conflicts(self, state: MetaReasonerState):
        """Étape 5 : Résolution des conflits"""
        print("\n[5/7] Résolution des conflits...")
        
        for candidate in state.candidates:
            # Simuler des preuves multiples (surrogate + haute fidélité)
            evidence_list = [
                Evidence(
                    source_id="surrogate",
                    value=candidate.metrics.get('latency_ms', 10),
                    applicability=0.8,
                    fidelity="F1",
                    timestamp=datetime.now().isoformat(),
                    uncertainty=1.0
                ),
                Evidence(
                    source_id="high_fidelity_sim",
                    value=candidate.metrics.get('latency_ms', 10) * 1.05,
                    applicability=0.9,
                    fidelity="F2",
                    timestamp=datetime.now().isoformat(),
                    uncertainty=0.3
                )
            ]
            
            resolution = self.conflict_resolver.resolve(evidence_list)
            
            if resolution.get('conflict'):
                state.uncertainty.unresolved_conflicts.append(candidate.design_id)
                print(f"   ⚠️ Conflit résolu pour {candidate.design_id}: {resolution['method']}")
    
    def _make_decision(self, state: MetaReasonerState, 
                       feasibility: Dict) -> Dict:
        """Étape 6 : Décision finale"""
        print("\n[6/7] Prise de décision...")
        
        # Filtrer les candidats faisables
        feasible = [c for c in state.candidates if c.feasibility == "PASS"]
        unknown = [c for c in state.candidates if c.feasibility == "UNKNOWN"]
        
        if not feasible and not unknown:
            # Aucun faisable → REJECT
            decision = self.action_engine.decide(
                DecisionAction.REJECT,
                design_id="none",
                rationale="Aucun candidat ne satisfait les contraintes dures"
            )
            state.decision = "REJECT"
        
        elif not feasible and unknown:
            # Des UNKNOWN → DEFER pour investigation
            decision = self.action_engine.decide(
                DecisionAction.DEFER,
                design_id=unknown[0].design_id,
                rationale="Faisabilité incertaine, investigation supplémentaire nécessaire"
            )
            state.decision = "DEFER"
        
        else:
            # Sélectionner le meilleur faisable
            best = max(feasible, key=lambda c: c.metrics.get('accuracy', 0))
            
            # Décision
            decision = self.action_engine.decide(
                DecisionAction.ACCEPT,
                design_id=best.design_id,
                rationale=f"Meilleur compromis: accuracy={best.metrics['accuracy']:.3f}, "
                         f"latency={best.metrics['latency_ms']:.1f}ms"
            )
            state.decision = "ACCEPT"
        
        print(f"   Décision: {state.decision}")
        
        return {
            "decision": state.decision,
            "selected_design_id": decision.params.get('design_id'),
            "rationale": decision.rationale,
            "n_feasible": len(feasible),
            "n_unknown": len(unknown),
            "feasibility_summary": feasibility['counts']
        }
    
    def get_state(self) -> Optional[Dict]:
        if self.current_state:
            return self.current_state.to_dict()
        return None
