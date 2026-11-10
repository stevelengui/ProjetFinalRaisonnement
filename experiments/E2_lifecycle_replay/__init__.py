"""
E2 — Lifecycle Replay (RQ5)
Teste la validité du cycle de vie post-déploiement via controlled replay

Exigences du directeur :
- Contrat de déploiement Γ_dep = {D*, A_dep, V(D*), M, I}
- 5 perturbations : C0 (nominal→CONTINUE), C1 (mineur→CALIBRATE),
  C2 (modéré→ADAPT), C3 (majeur→REMAP), C4 (structurel→REDESIGN)
- Sélection d'intervention : a* = argmax[Q_restore(a) - λ_C·C(a) - λ_R·R_residual(a)]
- Workloads : ECG et vibration
- Dire "controlled lifecycle replay" (pas "runtime adaptation")
"""

__version__ = "1.0.0"
