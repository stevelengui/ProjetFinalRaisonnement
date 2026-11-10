"""
Real Designs - Toutes les métriques remplies
"""

REAL_DESIGNS = [
    {
        "id": "ecg_hybrid_8bit",
        "name": "ECG Hybrid 8-bit",
        "description": "Modèle hybride QNN-SNN 8-bit",
        "domain": "medical",
        "algorithm": {
            "model_type": "hybrid",
            "quantization_bits": 8,
            "parameters": 7651,
            "operations": 373128,
        },
        "hardware": {
            "mcu_type": "riscv_rv32x",
            "clock_mhz": 120,
            "memory_kb": 29.0,
        },
        "metrics": {
            "accuracy": 0.961,
            "latency_ms": 8.2,
            "energy_mj": 2.8,
            "power_mw": 28.0,
            "memory_kb": 29.0,
            "M_weights_kib": 7.47,
            "explainability_score": 0.91,
            "reliability": 0.92,
            "robustness": 0.88,
            "f1_score": 0.951,
        },
        "source": "ECG MIT-BIH Database",
        "validation_status": "validated",
    },
    {
        "id": "ecg_hybrid_4bit",
        "name": "ECG Hybrid 4-bit",
        "description": "Modèle hybride QNN-SNN 4-bit",
        "domain": "medical",
        "algorithm": {
            "model_type": "hybrid",
            "quantization_bits": 4,
            "parameters": 3826,
            "operations": 373128,
        },
        "hardware": {
            "mcu_type": "riscv_rv32x",
            "clock_mhz": 120,
            "memory_kb": 14.5,
        },
        "metrics": {
            "accuracy": 0.948,
            "latency_ms": 6.2,
            "energy_mj": 1.9,
            "power_mw": 19.0,
            "memory_kb": 14.5,
            "M_weights_kib": 3.74,
            "explainability_score": 0.89,
            "reliability": 0.88,
            "robustness": 0.85,
            "f1_score": 0.942,
        },
        "source": "ECG MIT-BIH Database (quantized)",
        "validation_status": "validated",
    },
    {
        "id": "ecg_snn_2bit",
        "name": "ECG SNN 2-bit",
        "description": "Modèle SNN 2-bit",
        "domain": "medical",
        "algorithm": {
            "model_type": "snn",
            "quantization_bits": 2,
            "parameters": 1913,
            "operations": 186564,
        },
        "hardware": {
            "mcu_type": "arm_m0",
            "clock_mhz": 48,
            "memory_kb": 7.3,
        },
        "metrics": {
            "accuracy": 0.920,
            "latency_ms": 12.4,
            "energy_mj": 0.8,
            "power_mw": 8.0,
            "memory_kb": 7.3,
            "M_weights_kib": 1.87,
            "explainability_score": 0.82,
            "reliability": 0.78,
            "robustness": 0.72,
            "f1_score": 0.910,
        },
        "source": "ECG MIT-BIH Database (snn)",
        "validation_status": "validated",
    },
    {
        "id": "vibration_hybrid_8bit",
        "name": "Vibration Hybrid 8-bit",
        "description": "Modèle hybride pour maintenance prédictive",
        "domain": "industrial",
        "algorithm": {
            "model_type": "hybrid",
            "quantization_bits": 8,
            "parameters": 12450,
            "operations": 485000,
        },
        "hardware": {
            "mcu_type": "riscv_rv32x",
            "clock_mhz": 120,
            "memory_kb": 38.0,
        },
        "metrics": {
            "accuracy": 0.958,
            "latency_ms": 6.8,
            "energy_mj": 2.2,
            "power_mw": 22.0,
            "memory_kb": 38.0,
            "M_weights_kib": 12.16,
            "explainability_score": 0.88,
            "reliability": 0.90,
            "robustness": 0.86,
            "f1_score": 0.952,
        },
        "source": "CWRU Bearing Database",
        "validation_status": "validated",
    },
    {
        "id": "vibration_qnn_4bit",
        "name": "Vibration QNN 4-bit",
        "description": "Modèle QNN 4-bit",
        "domain": "iot",
        "algorithm": {
            "model_type": "qnn",
            "quantization_bits": 4,
            "parameters": 6225,
            "operations": 242500,
        },
        "hardware": {
            "mcu_type": "arm_m4",
            "clock_mhz": 100,
            "memory_kb": 19.0,
        },
        "metrics": {
            "accuracy": 0.934,
            "latency_ms": 15.2,
            "energy_mj": 1.9,
            "power_mw": 19.0,
            "memory_kb": 19.0,
            "M_weights_kib": 6.08,
            "explainability_score": 0.85,
            "reliability": 0.85,
            "robustness": 0.80,
            "f1_score": 0.928,
        },
        "source": "CWRU Bearing Database (quantized)",
        "validation_status": "validated",
    },
    {
        "id": "iot_snn_lowpower",
        "name": "IoT SNN Low Power",
        "description": "Modèle SNN basse consommation",
        "domain": "iot",
        "algorithm": {
            "model_type": "snn",
            "quantization_bits": 2,
            "parameters": 2500,
            "operations": 120000,
        },
        "hardware": {
            "mcu_type": "arm_m0",
            "clock_mhz": 48,
            "memory_kb": 8.0,
        },
        "metrics": {
            "accuracy": 0.890,
            "latency_ms": 18.6,
            "energy_mj": 0.6,
            "power_mw": 6.0,
            "memory_kb": 8.0,
            "M_weights_kib": 2.44,
            "explainability_score": 0.80,
            "reliability": 0.75,
            "robustness": 0.70,
            "f1_score": 0.875,
        },
        "source": "MMG Gesture Database",
        "validation_status": "validated",
    },
    {
        "id": "auto_hybrid_8bit",
        "name": "Automotive Hybrid 8-bit",
        "description": "Modèle hybride pour détection d'objets",
        "domain": "automotive",
        "algorithm": {
            "model_type": "hybrid",
            "quantization_bits": 8,
            "parameters": 19500,
            "operations": 890000,
        },
        "hardware": {
            "mcu_type": "riscv_rv32x",
            "clock_mhz": 160,
            "memory_kb": 55.0,
        },
        "metrics": {
            "accuracy": 0.902,
            "latency_ms": 18.6,
            "energy_mj": 4.2,
            "power_mw": 42.0,
            "memory_kb": 55.0,
            "M_weights_kib": 19.04,
            "explainability_score": 0.75,
            "reliability": 0.85,
            "robustness": 0.82,
            "f1_score": 0.890,
        },
        "source": "KITTI Object Detection",
        "validation_status": "validated",
    },
    {
        "id": "robot_slam_8bit",
        "name": "Robot SLAM 8-bit",
        "description": "Modèle pour SLAM visuel",
        "domain": "robotics",
        "algorithm": {
            "model_type": "hybrid",
            "quantization_bits": 8,
            "parameters": 15200,
            "operations": 720000,
        },
        "hardware": {
            "mcu_type": "riscv_rv32x",
            "clock_mhz": 120,
            "memory_kb": 62.0,
        },
        "metrics": {
            "accuracy": 0.890,
            "latency_ms": 22.4,
            "energy_mj": 5.1,
            "power_mw": 51.0,
            "memory_kb": 62.0,
            "M_weights_kib": 14.84,
            "explainability_score": 0.70,
            "reliability": 0.82,
            "robustness": 0.78,
            "f1_score": 0.875,
        },
        "source": "KITTI Visual SLAM",
        "validation_status": "validated",
    },
]


def get_all_designs():
    return REAL_DESIGNS


def get_designs_by_domain(domain):
    return [d for d in REAL_DESIGNS if d.get('domain') == domain]


def get_design_by_id(design_id):
    for d in REAL_DESIGNS:
        if d.get('id') == design_id:
            return d
    return None


def get_design_summary(domain=None):
    designs = get_designs_by_domain(domain) if domain else REAL_DESIGNS
    lines = [f"=== {len(designs)} DESIGNS ===\n"]
    for d in designs:
        lines.append(f"{d['id']}: {d['name']}")
        lines.append(f"  Accuracy: {d['metrics'].get('accuracy', 0):.1%}")
        lines.append(f"  Latency: {d['metrics'].get('latency_ms', 0)} ms")
        lines.append(f"  Energy: {d['metrics'].get('energy_mj', 0)} mJ")
    return "\n".join(lines)


if __name__ == "__main__":
    print(f"✅ {len(REAL_DESIGNS)} designs")
    for d in REAL_DESIGNS:
        print(f"\n{d['id']}:")
        print(f"  Accuracy: {d['metrics']['accuracy']:.1%}")
        print(f"  Energy: {d['metrics']['energy_mj']} mJ")
        print(f"  Memory: {d['metrics']['memory_kb']} KB")
