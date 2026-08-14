"""
Context Analyzer - Analyse le contexte applicatif
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

class ApplicationDomain(Enum):
    MEDICAL = "medical"
    INDUSTRIAL = "industrial"
    IOT = "iot"
    AUTOMOTIVE = "automotive"
    ROBOTICS = "robotics"

class CriticalityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SAFETY_CRITICAL = "safety_critical"

class DeploymentEnvironment(Enum):
    LAB = "lab"
    FIELD = "field"
    MEDICAL_FACILITY = "medical_facility"
    INDUSTRIAL_PLANT = "industrial_plant"

@dataclass
class ApplicationContext:
    domain: ApplicationDomain
    criticality: CriticalityLevel
    environment: DeploymentEnvironment
    max_latency_ms: float = 20.0
    max_power_mw: float = 50.0
    max_memory_kb: float = 64.0
    min_accuracy: float = 0.90
    requires_explainability: bool = True
    requires_robustness: bool = True
    requires_security: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "domain": self.domain.value,
            "criticality": self.criticality.value,
            "environment": self.environment.value,
            "max_latency_ms": self.max_latency_ms,
            "max_power_mw": self.max_power_mw,
            "max_memory_kb": self.max_memory_kb,
            "min_accuracy": self.min_accuracy,
            "requires_explainability": self.requires_explainability,
            "requires_robustness": self.requires_robustness,
            "requires_security": self.requires_security
        }

class ContextAnalyzer:
    def __init__(self):
        self.domain_rules = {
            ApplicationDomain.MEDICAL: {
                "criticality": CriticalityLevel.SAFETY_CRITICAL,
                "requires_explainability": True,
                "requires_robustness": True,
                "max_latency_ms": 20.0,
                "min_accuracy": 0.95
            },
            ApplicationDomain.INDUSTRIAL: {
                "criticality": CriticalityLevel.HIGH,
                "requires_explainability": True,
                "requires_robustness": True,
                "max_latency_ms": 10.0,
                "min_accuracy": 0.94
            }
        }
    
    def analyze(self, raw_context: Dict) -> ApplicationContext:
        domain_str = raw_context.get("domain", "industrial")
        domain = ApplicationDomain(domain_str)
        domain_config = self.domain_rules.get(domain, self.domain_rules[ApplicationDomain.INDUSTRIAL])
        
        return ApplicationContext(
            domain=domain,
            criticality=domain_config.get("criticality", CriticalityLevel.MEDIUM),
            environment=DeploymentEnvironment(raw_context.get("environment", "field")),
            max_latency_ms=raw_context.get("max_latency_ms", domain_config.get("max_latency_ms", 20.0)),
            max_power_mw=raw_context.get("max_power_mw", 50.0),
            max_memory_kb=raw_context.get("max_memory_kb", 64.0),
            min_accuracy=raw_context.get("min_accuracy", domain_config.get("min_accuracy", 0.90)),
            requires_explainability=raw_context.get("requires_explainability", domain_config.get("requires_explainability", True)),
            requires_robustness=raw_context.get("requires_robustness", domain_config.get("requires_robustness", True)),
            requires_security=raw_context.get("requires_security", False)
        )
    
    def get_constraints_summary(self, context: ApplicationContext) -> Dict:
        return {
            "domain": context.domain.value,
            "criticality": context.criticality.value,
            "environment": context.environment.value,
            "latency_budget_ms": context.max_latency_ms,
            "power_budget_mw": context.max_power_mw,
            "memory_budget_kb": context.max_memory_kb,
            "min_accuracy": context.min_accuracy
        }
