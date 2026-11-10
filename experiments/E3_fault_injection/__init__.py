"""
E3 — Fault Injection (RQ3)
Teste la fiabilité consciente avec injection de fautes contrôlée

Exigences du directeur :
- Injection de fautes contrôlée (logicielle/simulation)
- 5 modèles de fautes : bit flips poids, flips activation, perturbations SNN, 
  fautes mémoire, perturbations état contrôle
- 4 candidats : ECG 8bit, 4bit, SNN 2bit, protégé (ECC)
- Renversement décisif : efficacité nominale favorise D_A, 
  mais injection montre que D_A viole contrat → D_B admissible
- Métriques : P_SDC, ΔA_f, sensibilité critique, couverture détection, 
  pente dégradation gracieuse
"""

__version__ = "1.0.0"
