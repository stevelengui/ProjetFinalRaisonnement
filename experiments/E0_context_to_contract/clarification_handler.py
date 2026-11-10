"""
Clarification Handler - Gestion de l'information manquante
Exigence : "Information manquante → REQUEST CLARIFICATION (pas d'invention de seuil)"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from scenarios import Context


@dataclass
class ClarificationRequest:
    """Demande de clarification"""
    context_id: str
    missing_fields: List[str]
    reason: str
    severity: str  # "blocking", "warning"
    suggested_questions: List[str] = field(default_factory=list)
    can_proceed_with_default: bool = False
    default_values: Dict[str, any] = field(default_factory=dict)


class ClarificationHandler:
    """
    Gestionnaire de clarification
    RÈGLE D'OR : Ne JAMAIS inventer de seuil. Si info manquante → demander.
    """
    
    # Seuils "sûrs" connus par domaine (utilisés UNIQUEMENT si l'utilisateur accepte les défauts)
    KNOWN_DEFAULTS = {
        "medical": {
            "max_latency_ms": 20.0,
            "max_memory_kb": 512.0,
            "max_power_mw": 50.0,
            "min_accuracy": 0.95,
        },
        "industrial": {
            "max_latency_ms": 50.0,
            "max_memory_kb": 512.0,
            "max_power_mw": 100.0,
            "min_accuracy": 0.93,
        }
    }
    
    # Champs critiques qui BLOQUENT la décision s'ils manquent
    CRITICAL_FIELDS = ["max_latency_ms", "min_accuracy"]
    
    # Champs importants mais non-bloquants
    IMPORTANT_FIELDS = ["max_memory_kb", "max_power_mw"]
    
    def __init__(self):
        self.requests: List[ClarificationRequest] = []
    
    def analyze_context(self, context: Context) -> Optional[ClarificationRequest]:
        """
        Analyse un contexte et détermine si une clarification est nécessaire
        Retourne None si le contexte est complet
        """
        missing = []
        blocking = []
        warnings = []
        
        # Vérifier les champs critiques
        for field_name in self.CRITICAL_FIELDS:
            value = getattr(context, field_name, None)
            if value is None:
                missing.append(field_name)
                blocking.append(field_name)
        
        # Vérifier les champs importants
        for field_name in self.IMPORTANT_FIELDS:
            value = getattr(context, field_name, None)
            if value is None:
                missing.append(field_name)
                warnings.append(field_name)
        
        # Vérifier la cohérence sécurité/threat context
        if context.security_required and context.threat_context in ["none", "unknown", None]:
            missing.append("threat_context")
            blocking.append("threat_context")
        
        # Pas de manquant → pas de clarification
        if not missing:
            return None
        
        # Déterminer la sévérité
        if blocking:
            severity = "blocking"
            reason = f"Champs critiques manquants : {blocking}"
        else:
            severity = "warning"
            reason = f"Champs importants manquants : {warnings}"
        
        # Générer les questions suggérées
        questions = self._generate_questions(missing, context)
        
        # Valeurs par défaut disponibles
        defaults = {}
        for field_name in missing:
            if field_name in self.KNOWN_DEFAULTS.get(context.domain, {}):
                defaults[field_name] = self.KNOWN_DEFAULTS[context.domain][field_name]
        
        request = ClarificationRequest(
            context_id=context.context_id,
            missing_fields=missing,
            reason=reason,
            severity=severity,
            suggested_questions=questions,
            can_proceed_with_default=(severity == "warning" and len(defaults) == len(missing)),
            default_values=defaults
        )
        
        self.requests.append(request)
        return request
    
    def _generate_questions(self, missing_fields: List[str], 
                          context: Context) -> List[str]:
        """Génère des questions de clarification"""
        questions = []
        
        question_templates = {
            "max_latency_ms": "Quel est le budget de latence maximal acceptable (en ms) ?",
            "max_memory_kb": "Quelle est la quantité de mémoire disponible (en KB) ?",
            "max_power_mw": "Quel est le budget de puissance maximal (en mW) ?",
            "min_accuracy": "Quelle est la précision minimale requise ?",
            "threat_context": "Quel est le niveau de menace attendu (none/low/medium/high) ?",
        }
        
        for field_name in missing_fields:
            if field_name in question_templates:
                questions.append(f"{question_templates[field_name]} (domaine: {context.domain})")
        
        return questions
    
    def should_block(self, request: ClarificationRequest) -> bool:
        """Détermine si la décision doit être bloquée"""
        return request.severity == "blocking"
    
    def get_request_summary(self) -> Dict:
        """Résumé des demandes de clarification"""
        if not self.requests:
            return {"total": 0}
        
        blocking = sum(1 for r in self.requests if r.severity == "blocking")
        warnings = sum(1 for r in self.requests if r.severity == "warning")
        
        all_missing = []
        for r in self.requests:
            all_missing.extend(r.missing_fields)
        
        from collections import Counter
        missing_counts = Counter(all_missing)
        
        return {
            "total_requests": len(self.requests),
            "blocking": blocking,
            "warnings": warnings,
            "most_common_missing": missing_counts.most_common(5),
            "requests": [self._request_to_dict(r) for r in self.requests]
        }
    
    def _request_to_dict(self, request: ClarificationRequest) -> Dict:
        return {
            "context_id": request.context_id,
            "missing_fields": request.missing_fields,
            "severity": request.severity,
            "reason": request.reason,
            "suggested_questions": request.suggested_questions
        }


if __name__ == "__main__":
    from scenarios import get_all_scenarios
    
    scenarios = get_all_scenarios()
    handler = ClarificationHandler()
    
    print("🔍 Analyse des contextes...")
    for s in scenarios:
        request = handler.analyze_context(s)
        if request:
            print(f"\n⚠️ {s.context_id}: {request.severity}")
            print(f"   Manquants: {request.missing_fields}")
            print(f"   Questions: {request.suggested_questions[:2]}")
    
    print(f"\n📊 Résumé: {handler.get_request_summary()['total_requests']} demandes")
