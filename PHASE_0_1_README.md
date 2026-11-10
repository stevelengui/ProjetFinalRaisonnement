# Phase 0 + Phase 1 : Intégrité Numérique + Contrôleur Méta-Opérationnel

## 🚨 PHASE 0 : Intégrité Numérique (PRIORITÉ ABSOLUE)

### Résout l'Issue 8 du directeur
- **Problème** : 373 128 params × 1 octet ≠ 8,53 KB
- **Solution** : `memory_profiler.py` reconstruit les vraies valeurs
- **Valeur correcte** : M_weights = 373 128 bytes = **364,38 KiB**
- **Valeur incorrecte** : 8,53 KB (à ne jamais utiliser)

### Modules créés
1. `memory_profiler.py` — Profiling mémoire exact
2. `evidence_registry.py` — Registre de preuves traçable
3. `qa_gate.py` — Vérifications automatiques

### Livrables
- `evidence_registry/memory_reports.json`
- `evidence_registry/registry.json`

---

## 🏗️ PHASE 1 : Contrôleur Méta-Opérationnel

### Résout l'Issue 10 du directeur
- **Exigence** : Contrôleur exécutable et déterministe
- **Solution** : 8 modules interconnectés

### Modules créés
1. `state_space.py` — s_t = {Γ, D, E, U, R, B, H}
2. `tri_state_logic.py` — PASS/FAIL/UNKNOWN (UNKNOWN ≠ PASS)
3. `evi_calculator.py` — Expected Value of Information
4. `action_engine.py` — Actions partitionnées
5. `conflict_resolver.py` — Applicabilité > fidélité > récence > incertitude
6. `lifecycle_manager.py` — MONITOR/CALIBRATE/ADAPT/REMAP/REDESIGN
7. `transition_logger.py` — Logger toutes transitions
8. `meta_controller_v2.py` — Contrôleur complet

### Utilisation
```python
from meta_reasoning.meta_controller_v2 import MetaControllerV2

controller = MetaControllerV2()
result = controller.reason({
    "domain": "medical",
    "max_latency_ms": 20,
    "max_memory_kb": 512,
    "min_accuracy": 0.95
})

print(result['decision'])


