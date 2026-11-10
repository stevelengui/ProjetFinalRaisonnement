"""
E6 — Design Decision Records (RQ4)
Teste les enregistrements de décision de conception auditables

Exigences du directeur :
- Design Decision Record J(D) = {C, Γ, A, E, U, R, Alt, Dec, CF}
- Métriques : EC, CT, DF, CF, AC, AV
- 3 tests contrefactuels décisifs :
  1. Relaxer contrainte → doit devenir admissible
  2. Suppression de preuve → ne pas affirmer confidemment
  3. Preuve contradictoire → déclencher gestion de conflit
"""

__version__ = "1.0.0"
