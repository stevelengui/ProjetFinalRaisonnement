# Limitations and Scope

## 1. Simulation-Based Validation

Les résultats sont issus d'une **validation par simulation contrôlée**. Les valeurs sont **dérivées de modèles** et non mesurées sur hardware physique.

## 2. Composants Mesurés vs Dérivés

| Composant | Provenance |
|-----------|-----------|
| M_weights | DER_FROM_ARTIFACTS (compté) |
| M_activation_peak | DER_FROM_ARTIFACTS (calculé) |
| M_state | DER_FROM_ARTIFACTS (calculé) |
| M_runtime | ESTIMATED |
| M_code | ESTIMATED |

## 3. Adversarial Robustness (E5)

ASR reste **constant entre designs** sous une même menace en simulation.

## 4. Domain-Shift (E4)

Scénario décisif (MAML +40% mémoire) **créé artificiellement**.

## 5. Ablation Study (E7)

Dégradations **calibrées manuellement**.

## 6. Claims RETIRÉS

- ❌ Réduction 65% → 36.5%
- ❌ Validation 5-domaines → 2 domaines
- ❌ Hardware physique → aucune
- ❌ MAML requis → un outil parmi 8
- ❌ 373 128 params → 7 651 params
- ❌ 8,53 KB → 7,47 KiB

## 7. Claims QUALIFIÉS

- ⚠️ E0-E7 → simulation-based
- ⚠️ Real designs → real weights, simulated metrics

## 8. Future Work

1. Validation hardware (FPGA, ASIC)
2. Attaques réelles (FGSM, PGD)
3. Domaines supplémentaires (IoT, Automotive)
4. Contrefactuels supplémentaires
