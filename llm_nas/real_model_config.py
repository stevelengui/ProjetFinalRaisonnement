"""
Real Model Config - Vraies valeurs du modèle ECG
Basé sur les artefacts réels : model_weights.h / model_weights.c
"""

# ============================================================
# VRAIES VALEURS DEPUIS model_weights.h
# ============================================================

# Nombre RÉEL de paramètres (compté depuis les tableaux C)
REAL_PARAMETER_COUNT = 7651

# Mémoire RÉELLE des poids (int8_t = 1 byte)
REAL_M_WEIGHTS_BYTES = 7651
REAL_M_WEIGHTS_KIB = 7651 / 1024  # 7.47 KiB

# Composants mémoire (valeurs recalculées)
REAL_M_ACTIVATION_PEAK_BYTES = 11014   # Corrigé : buffers int32_t
REAL_M_STATE_BYTES = 792                # LSTM (24) + SNN (768)
REAL_M_RUNTIME_BYTES = 2048             # Stack + heap
REAL_M_CODE_BYTES = 8192                # Firmware binaire

# Total
REAL_M_TOTAL_BYTES = (
    REAL_M_WEIGHTS_BYTES + 
    REAL_M_ACTIVATION_PEAK_BYTES + 
    REAL_M_STATE_BYTES + 
    REAL_M_RUNTIME_BYTES + 
    REAL_M_CODE_BYTES
)  # 29 697 bytes

REAL_M_TOTAL_KIB = REAL_M_TOTAL_BYTES / 1024  # 29.00 KiB

# ============================================================
# CONFIGURATION DU MODÈLE (depuis model_weights.h)
# ============================================================
INPUT_SIZE = 360
N_FEATURES = 1
CONV1_FILTERS = 6
CONV2_FILTERS = 12
LSTM_HIDDEN = 24
SNN_HIDDEN = 24
OUTPUT_SIZE = 5
TIME_STEPS = 32
FUSION_SIZE = 24
FC1_SIZE = 12

CONV1_OUT_SIZE = 180
CONV2_OUT_SIZE = 90
SNN_INPUT_SIZE = 33

# ============================================================
# NOMBRE D'OPÉRATIONS (TOTAL_OPS, PAS de params)
# ============================================================
TOTAL_OPS = 373128
TOTAL_OPERATIONS = TOTAL_OPS  # Alias

# Breakdown des opérations
CONV1_OPS = 6 * 180 * 5 * 2       # 10800
CONV2_OPS = 12 * 90 * 3 * 2       # 6480
LSTM_OPS = 4 * 24 * (33 + 24) * 32 * 2  # 350208
LIF_OPS = 32 * 24 * 3             # 2304
FC_OPS = (24 * 36 + 12 * 24 + 5 * 12) * 2  # 2424
ROUTER_OPS = (12 * 36 + 2 * 12) * 2  # 912

# Vérification
assert CONV1_OPS + CONV2_OPS + LSTM_OPS + LIF_OPS + FC_OPS + ROUTER_OPS == 373128, "Erreur TOTAL_OPS"

# ============================================================
# DÉTAIL DES COUCHES (vraies tailles)
# ============================================================
LAYER_DETAILS = {
    "conv1_weight": {"shape": (30,), "params": 30, "bytes": 30},
    "conv1_bias": {"shape": (6,), "params": 6, "bytes": 6},
    "conv2_weight": {"shape": (216,), "params": 216, "bytes": 216},
    "conv2_bias": {"shape": (12,), "params": 12, "bytes": 12},
    "lstm_weight_ih": {"shape": (3168,), "params": 3168, "bytes": 3168},
    "lstm_weight_hh": {"shape": (2304,), "params": 2304, "bytes": 2304},
    "lstm_bias_ih": {"shape": (96,), "params": 96, "bytes": 96},
    "lstm_bias_hh": {"shape": (96,), "params": 96, "bytes": 96},
    "router_fc1_weight": {"shape": (432,), "params": 432, "bytes": 432},
    "router_fc1_bias": {"shape": (12,), "params": 12, "bytes": 12},
    "router_fc2_weight": {"shape": (24,), "params": 24, "bytes": 24},
    "router_fc2_bias": {"shape": (2,), "params": 2, "bytes": 2},
    "fusion_weight": {"shape": (864,), "params": 864, "bytes": 864},
    "fusion_bias": {"shape": (24,), "params": 24, "bytes": 24},
    "fc1_weight": {"shape": (288,), "params": 288, "bytes": 288},
    "fc1_bias": {"shape": (12,), "params": 12, "bytes": 12},
    "fc2_weight": {"shape": (60,), "params": 60, "bytes": 60},
    "fc2_bias": {"shape": (5,), "params": 5, "bytes": 5},
}

# Vérification
TOTAL_PARAMS_FROM_LAYERS = sum(l["params"] for l in LAYER_DETAILS.values())
assert TOTAL_PARAMS_FROM_LAYERS == 7651, f"Erreur: {TOTAL_PARAMS_FROM_LAYERS}"

# ============================================================
# RÉSUMÉ POUR AFFICHAGE
# ============================================================
def get_summary():
    return {
        "parameter_count": REAL_PARAMETER_COUNT,
        "operations_count": TOTAL_OPS,
        "M_weights_bytes": REAL_M_WEIGHTS_BYTES,
        "M_weights_kib": round(REAL_M_WEIGHTS_KIB, 2),
        "M_total_bytes": REAL_M_TOTAL_BYTES,
        "M_total_kib": round(REAL_M_TOTAL_KIB, 2),
        "quantization": "int8_t",
        "note": "373128 = nombre d'OPÉRATIONS, PAS de paramètres"
    }


if __name__ == "__main__":
    import json
    print("=" * 70)
    print("📊 VRAIES VALEURS DU MODÈLE ECG")
    print("=" * 70)
    print(json.dumps(get_summary(), indent=2))
    
    print(f"\n✅ Total params: {TOTAL_PARAMS_FROM_LAYERS}")
    print(f"✅ Total ops: {TOTAL_OPS}")
    print(f"✅ M_weights: {REAL_M_WEIGHTS_BYTES} bytes ({REAL_M_WEIGHTS_KIB:.2f} KiB)")
    print(f"✅ M_total: {REAL_M_TOTAL_BYTES} bytes ({REAL_M_TOTAL_KIB:.2f} KiB)")
