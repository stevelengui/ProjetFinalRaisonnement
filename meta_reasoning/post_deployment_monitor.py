"""
Post-Deployment Monitor - Détection des changements de domaine après déploiement
Surveille les performances en production et déclenche des alertes
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceMetric:
    name: str
    value: float
    timestamp: str
    source: str

@dataclass
class Alert:
    level: AlertLevel
    message: str
    timestamp: str
    metrics: Dict[str, float]
    recommended_action: str

@dataclass
class DeploymentContext:
    design_id: str
    domain: str
    expected_metrics: Dict[str, float]
    tolerance: Dict[str, float]
    deployment_date: str
    environment: str

class PostDeploymentMonitor:
    """
    Moniteur post-déploiement
    Détecte les dérives de performance et les changements de domaine
    """
    
    def __init__(self):
        self.active_monitors: Dict[str, DeploymentContext] = {}
        self.performance_history: Dict[str, List[PerformanceMetric]] = {}
        self.alert_history: List[Alert] = []
        
        # Seuils de détection
        self.detection_thresholds = {
            "accuracy": 0.05,        # 5% de dégradation
            "latency": 0.20,         # 20% d'augmentation
            "energy": 0.25,          # 25% d'augmentation
            "memory": 0.15           # 15% d'augmentation
        }
    
    def register_deployment(self, design: Dict, expected_metrics: Dict) -> str:
        """
        Enregistre un nouveau déploiement
        """
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        context = DeploymentContext(
            design_id=design.get("id", "unknown"),
            domain=design.get("domain", "industrial"),
            expected_metrics=expected_metrics,
            tolerance={k: v * self.detection_thresholds.get(k, 0.10) 
                      for k, v in expected_metrics.items()},
            deployment_date=datetime.now().isoformat(),
            environment=design.get("environment", "production")
        )
        
        self.active_monitors[deployment_id] = context
        self.performance_history[deployment_id] = []
        
        return deployment_id
    
    def report_metric(self, deployment_id: str, metric_name: str, value: float, 
                      source: str = "production") -> Dict:
        """
        Reçoit une métrique de production
        """
        if deployment_id not in self.active_monitors:
            return {"error": "Déploiement inconnu"}
        
        context = self.active_monitors[deployment_id]
        
        # Ajouter à l'historique
        metric = PerformanceMetric(
            name=metric_name,
            value=value,
            timestamp=datetime.now().isoformat(),
            source=source
        )
        self.performance_history[deployment_id].append(metric)
        
        # Vérifier les alertes
        alerts = self._check_metrics(metric, context)
        
        return {
            "status": "recorded",
            "deployment_id": deployment_id,
            "metric": metric_name,
            "value": value,
            "alerts": [a.__dict__ for a in alerts]
        }
    
    def _check_metrics(self, metric: PerformanceMetric, context: DeploymentContext) -> List[Alert]:
        """
        Vérifie si la métrique déclenche une alerte
        """
        alerts = []
        
        expected = context.expected_metrics.get(metric.name, None)
        if expected is None:
            return alerts
        
        tolerance = context.tolerance.get(metric.name, expected * 0.10)
        current_value = metric.value
        
        # Détection de dérive
        delta = abs(current_value - expected)
        
        if delta > tolerance * 2:
            if metric.name in ["accuracy"]:
                # Pour accuracy, une baisse est critique
                if current_value < expected - tolerance:
                    alerts.append(Alert(
                        level=AlertLevel.CRITICAL,
                        message=f"Dégradation sévère de {metric.name}: {current_value:.3f} vs {expected:.3f} attendu",
                        timestamp=datetime.now().isoformat(),
                        metrics={metric.name: current_value, "expected": expected},
                        recommended_action=f"Ré-entraîner le modèle ou revenir à la version précédente"
                    ))
                else:
                    alerts.append(Alert(
                        level=AlertLevel.WARNING,
                        message=f"Variation de {metric.name}: {current_value:.3f} vs {expected:.3f} attendu",
                        timestamp=datetime.now().isoformat(),
                        metrics={metric.name: current_value, "expected": expected},
                        recommended_action="Surveiller la tendance sur les prochaines heures"
                    ))
            else:
                # Pour les autres métriques, toute variation est surveillée
                if delta > tolerance * 1.5:
                    alerts.append(Alert(
                        level=AlertLevel.WARNING,
                        message=f"Variation significative de {metric.name}: {current_value:.3f} vs {expected:.3f} attendu",
                        timestamp=datetime.now().isoformat(),
                        metrics={metric.name: current_value, "expected": expected},
                        recommended_action="Vérifier les conditions d'opération"
                    ))
        
        # Détection de changement de domaine (domain shift)
        if len(self.performance_history.get(context.design_id, [])) > 10:
            domain_shift = self._detect_domain_shift(context.design_id)
            if domain_shift:
                alerts.append(Alert(
                    level=AlertLevel.EMERGENCY,
                    message="Changement de domaine détecté !",
                    timestamp=datetime.now().isoformat(),
                    metrics={"domain_shift_score": domain_shift},
                    recommended_action="Ré-évaluer le design avec le nouveau contexte"
                ))
        
        return alerts
    
    def _detect_domain_shift(self, design_id: str) -> float:
        """
        Détecte un changement de domaine basé sur les métriques récentes
        """
        history = self.performance_history.get(design_id, [])
        if len(history) < 10:
            return 0.0
        
        # Analyser les 5 dernières métriques
        recent = history[-5:]
        older = history[-10:-5]
        
        # Comparer les tendances
        if len(recent) < 5 or len(older) < 5:
            return 0.0
        
        # Calculer la moyenne de chaque groupe
        recent_acc = np.mean([m.value for m in recent if m.name == "accuracy"])
        older_acc = np.mean([m.value for m in older if m.name == "accuracy"])
        
        if older_acc == 0:
            return 0.0
        
        # Score de shift (0-1)
        shift_score = abs(recent_acc - older_acc) / older_acc
        
        return min(1.0, shift_score)
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """
        Retourne le statut complet d'un déploiement
        """
        if deployment_id not in self.active_monitors:
            return {"error": "Déploiement inconnu"}
        
        context = self.active_monitors[deployment_id]
        history = self.performance_history.get(deployment_id, [])
        
        # Analyser les tendances
        trends = {}
        for metric in ["accuracy", "latency", "energy", "memory"]:
            values = [m.value for m in history if m.name == metric]
            if values:
                trends[metric] = {
                    "current": values[-1],
                    "expected": context.expected_metrics.get(metric, 0),
                    "trend": "up" if len(values) > 1 and values[-1] > values[-2] else "down",
                    "stability": round(1 - np.std(values) / np.mean(values) if values else 1, 3)
                }
        
        # Alertes récentes
        recent_alerts = [a.__dict__ for a in self.alert_history 
                         if a.timestamp > (datetime.now() - timedelta(hours=24)).isoformat()]
        
        return {
            "deployment_id": deployment_id,
            "design_id": context.design_id,
            "domain": context.domain,
            "deployment_date": context.deployment_date,
            "environment": context.environment,
            "total_metrics_received": len(history),
            "trends": trends,
            "recent_alerts": recent_alerts[-5:],
            "status": "healthy" if not recent_alerts else "warning"
        }
    
    def get_monitoring_report(self) -> str:
        """
        Génère un rapport de monitoring
        """
        lines = [
            "=" * 60,
            "RAPPORT DE MONITORING POST-DÉPLOIEMENT",
            "=" * 60,
            f"Date: {datetime.now().isoformat()}",
            f"Déploiements actifs: {len(self.active_monitors)}",
            f"Alertes: {len(self.alert_history)}",
            ""
        ]
        
        for deploy_id, context in self.active_monitors.items():
            status = self.get_deployment_status(deploy_id)
            lines.append(f"--- {deploy_id} ---")
            lines.append(f"  Design: {context.design_id}")
            lines.append(f"  Domaine: {context.domain}")
            lines.append(f"  Status: {status.get('status', 'unknown')}")
            
            for metric, trend in status.get('trends', {}).items():
                lines.append(f"  {metric}: {trend.get('current', 'N/A'):.3f} "
                            f"(attendu: {trend.get('expected', 'N/A'):.3f}, "
                            f"stabilité: {trend.get('stability', 0):.0%})")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def get_auto_reasoning_trigger(self, deployment_id: str) -> Optional[Dict]:
        """
        Détermine si le méta-raisonnement doit être déclenché
        """
        if deployment_id not in self.active_monitors:
            return None
        
        context = self.active_monitors[deployment_id]
        status = self.get_deployment_status(deployment_id)
        
        # Conditions de déclenchement
        triggers = []
        
        # 1. Dégradation de performance significative
        for metric, trend in status.get('trends', {}).items():
            if metric == "accuracy" and trend.get('stability', 1) < 0.85:
                triggers.append({
                    "reason": f"Stabilité de {metric} faible ({trend['stability']:.0%})",
                    "severity": "high"
                })
        
        # 2. Alertes critiques récentes
        recent_alerts = status.get('recent_alerts', [])
        critical_alerts = [a for a in recent_alerts if a.get('level') == 'critical']
        if critical_alerts:
            triggers.append({
                "reason": f"{len(critical_alerts)} alertes critiques récentes",
                "severity": "critical"
            })
        
        # 3. Changement de domaine détecté
        if status.get('trends', {}).get('accuracy', {}).get('trend') == 'down' and \
           status.get('trends', {}).get('accuracy', {}).get('stability', 1) < 0.90:
            triggers.append({
                "reason": "Changement de domaine potentiel détecté",
                "severity": "medium"
            })
        
        if triggers:
            return {
                "trigger": True,
                "reasons": triggers,
                "recommendation": "Relancer le méta-raisonnement avec le nouveau contexte",
                "context_to_use": {
                    "domain": context.domain,
                    "environment": context.environment,
                    "max_latency_ms": context.expected_metrics.get("latency", 20),
                    "max_power_mw": context.expected_metrics.get("power", 50),
                    "max_memory_kb": context.expected_metrics.get("memory", 64),
                    "min_accuracy": context.expected_metrics.get("accuracy", 0.95)
                }
            }
        
        return {"trigger": False, "message": "Pas de déclenchement nécessaire"}
