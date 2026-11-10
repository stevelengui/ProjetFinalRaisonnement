"""
E4 — Domain-Shift Meta-Reasoning (RQ3)
Teste le méta-raisonnement conscient du domain shift

Exigences du directeur :
- MAML = UN OUTIL parmi : recalibration, MAML, fine-tuning, changement précision,
  switch sous-réseau, remapping, rerun AutoCoDesign
- Sévérités : D0 (nominal), D1 (léger → RECALIBRATE), D2 (modéré → MAML),
  D3 (sévère → REMAP/REDESIGN)
- Post-adaptation validity : ré-évaluer accuracy, latence, mémoire, énergie, fiabilité
- Scénario décisif : MAML restaure la prédiction MAIS cause M' > M_max → remapping forcé
"""

__version__ = "1.0.0"
