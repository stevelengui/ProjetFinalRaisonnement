"""
Policies - 4 politiques d'évaluation de fidélité
Version STOCHASTIQUE - 10 runs par cas, moyenne
"""

import sys
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import List
import random

# Ajouter le chemin pour les imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

from experiments.E1_adaptive_fidelity.fidelity_hierarchy import Fidelity, FidelityHierarchy
from experiments.E1_adaptive_fidelity.test_cases import TestCase, CaseCategory


class PolicyType(Enum):
    LOW_FIDELITY_ONLY = "low_fidelity_only"
    EXHAUSTIVE = "exhaustive"
    FIXED_WORKFLOW = "fixed_workflow"
    ADAPTIVE = "adaptive"


@dataclass
class EvaluationStep:
    fidelity: Fidelity
    cost: float
    time_s: float
    verdict: str
    reason: str


@dataclass
class PolicyResult:
    policy: PolicyType
    case_id: str
    steps: List[EvaluationStep] = field(default_factory=list)
    final_verdict: str = "UNKNOWN"
    total_cost: float = 0.0
    total_time_s: float = 0.0
    correct: bool = False
    correct_rate: float = 0.0


class Policy:
    def __init__(self, hierarchy: FidelityHierarchy):
        self.hierarchy = hierarchy
        self.type = None
        self.n_runs = 10

    def evaluate(self, case: TestCase) -> PolicyResult:
        raise NotImplementedError

    def _evaluate_at_fidelity(self, case: TestCase, fidelity: Fidelity,
                              run_id: int = 0) -> EvaluationStep:
        level = self.hierarchy.get_level(fidelity)
        seed = hash(case.case_id + fidelity.name + str(run_id)) % 2**32
        rng = random.Random(seed)

        accuracy_by_fidelity = {
            Fidelity.F0_ANALYTICAL: 0.60,
            Fidelity.F1_SURROGATE: 0.80,
            Fidelity.F2_SIMULATION: 0.95,
            Fidelity.F3_REFERENCE: 1.00,
        }

        prob_correct = accuracy_by_fidelity[fidelity]
        if rng.random() < prob_correct:
            verdict = case.expected_verdict
        else:
            verdict = "FAIL" if case.expected_verdict == "PASS" else "PASS"

        return EvaluationStep(
            fidelity=fidelity,
            cost=level.cost,
            time_s=level.time_s,
            verdict=verdict,
            reason=f"Évaluation à {fidelity.name} (run {run_id})"
        )

    def _evaluate_with_runs(self, case: TestCase, policy_fn) -> PolicyResult:
        runs = []
        for run_id in range(self.n_runs):
            result = policy_fn(case, run_id)
            runs.append(result)

        pass_count = sum(1 for r in runs if r.final_verdict == "PASS")
        fail_count = sum(1 for r in runs if r.final_verdict == "FAIL")

        if pass_count > fail_count:
            majority_verdict = "PASS"
            correct_rate = pass_count / self.n_runs
        else:
            majority_verdict = "FAIL"
            correct_rate = fail_count / self.n_runs

        final = runs[0]
        final.final_verdict = majority_verdict
        final.total_cost = sum(r.total_cost for r in runs) / self.n_runs
        final.total_time_s = sum(r.total_time_s for r in runs) / self.n_runs
        final.correct = (majority_verdict == case.expected_verdict)
        final.correct_rate = correct_rate

        return final


class LowFidelityOnlyPolicy(Policy):
    def __init__(self, hierarchy):
        super().__init__(hierarchy)
        self.type = PolicyType.LOW_FIDELITY_ONLY

    def evaluate(self, case):
        def single_run(c, run_id):
            result = PolicyResult(policy=self.type, case_id=c.case_id)
            step = self._evaluate_at_fidelity(c, Fidelity.F1_SURROGATE, run_id)
            result.steps.append(step)
            result.final_verdict = step.verdict
            result.total_cost = step.cost
            result.total_time_s = step.time_s
            return result

        return self._evaluate_with_runs(case, single_run)


class ExhaustivePolicy(Policy):
    def __init__(self, hierarchy):
        super().__init__(hierarchy)
        self.type = PolicyType.EXHAUSTIVE

    def evaluate(self, case):
        def single_run(c, run_id):
            result = PolicyResult(policy=self.type, case_id=c.case_id)
            step = self._evaluate_at_fidelity(c, Fidelity.F2_SIMULATION, run_id)
            result.steps.append(step)
            result.final_verdict = step.verdict
            result.total_cost = step.cost
            result.total_time_s = step.time_s
            return result

        return self._evaluate_with_runs(case, single_run)


class FixedWorkflowPolicy(Policy):
    def __init__(self, hierarchy):
        super().__init__(hierarchy)
        self.type = PolicyType.FIXED_WORKFLOW

    def evaluate(self, case):
        def single_run(c, run_id):
            result = PolicyResult(policy=self.type, case_id=c.case_id)
            step1 = self._evaluate_at_fidelity(c, Fidelity.F1_SURROGATE, run_id)
            result.steps.append(step1)
            result.total_cost = step1.cost
            result.total_time_s = step1.time_s

            should_escalate = c.category in [
                CaseCategory.BOUNDARY, CaseCategory.UNCERTAIN, CaseCategory.CONFLICT
            ]

            if should_escalate:
                step2 = self._evaluate_at_fidelity(c, Fidelity.F2_SIMULATION, run_id)
                result.steps.append(step2)
                result.total_cost += step2.cost
                result.total_time_s += step2.time_s
                result.final_verdict = step2.verdict
            else:
                result.final_verdict = step1.verdict

            return result

        return self._evaluate_with_runs(case, single_run)


class AdaptivePolicy(Policy):
    def __init__(self, hierarchy):
        super().__init__(hierarchy)
        self.type = PolicyType.ADAPTIVE

    def evaluate(self, case):
        def single_run(c, run_id):
            result = PolicyResult(policy=self.type, case_id=c.case_id)
            step1 = self._evaluate_at_fidelity(c, Fidelity.F1_SURROGATE, run_id)
            result.steps.append(step1)
            result.total_cost = step1.cost
            result.total_time_s = step1.time_s

            if self._should_escalate(c):
                step2 = self._evaluate_at_fidelity(c, Fidelity.F2_SIMULATION, run_id)
                result.steps.append(step2)
                result.total_cost += step2.cost
                result.total_time_s += step2.time_s
                result.final_verdict = step2.verdict
            else:
                result.final_verdict = step1.verdict

            return result

        return self._evaluate_with_runs(case, single_run)

    def _should_escalate(self, case: TestCase) -> bool:
        if case.category in [CaseCategory.SAFE, CaseCategory.INFEASIBLE]:
            return False

        if case.category in [CaseCategory.BOUNDARY, CaseCategory.UNCERTAIN, CaseCategory.CONFLICT]:
            return True

        if case.category == CaseCategory.PARETO_CLOSE:
            margin = self._compute_margin(case)
            return margin < 0.03

        return False

    def _compute_margin(self, case: TestCase) -> float:
        margins = []
        for constraint, threshold in case.hard_constraints.items():
            if "max" in constraint:
                if "latency" in constraint:
                    value = case.metrics.get("latency_ms", 0)
                elif "power" in constraint:
                    value = case.metrics.get("power_mw", 0)
                elif "memory" in constraint:
                    value = case.metrics.get("memory_kb", 0)
                else:
                    value = 0
                if threshold > 0:
                    margins.append((threshold - value) / threshold)
            elif "min" in constraint:
                if "accuracy" in constraint:
                    value = case.metrics.get("accuracy", 0)
                elif "reliability" in constraint:
                    value = case.metrics.get("reliability", 0)
                else:
                    value = 0
                if value > 0:
                    margins.append((value - threshold) / value)
        return min(margins) if margins else 0.5


def get_all_policies(hierarchy: FidelityHierarchy) -> List[Policy]:
    return [
        LowFidelityOnlyPolicy(hierarchy),
        ExhaustivePolicy(hierarchy),
        FixedWorkflowPolicy(hierarchy),
        AdaptivePolicy(hierarchy),
    ]
