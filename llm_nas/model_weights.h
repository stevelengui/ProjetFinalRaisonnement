#ifndef MODEL_WEIGHTS_H
#define MODEL_WEIGHTS_H

#include <stdint.h>

// ==================== MODEL CONFIGURATION ====================
#define INPUT_SIZE 360
#define N_FEATURES 1
#define CONV1_FILTERS 6
#define CONV2_FILTERS 12
#define LSTM_HIDDEN 24
#define SNN_HIDDEN 24
#define OUTPUT_SIZE 5
#define TIME_STEPS 32
#define FUSION_SIZE 24
#define FC1_SIZE 12

// Calculated sizes
#define CONV1_OUT_SIZE 180
#define CONV2_OUT_SIZE 90
#define SNN_INPUT_SIZE 33
#define TOTAL_CONV2_FEATURES (CONV2_OUT_SIZE * CONV2_FILTERS)
#define USABLE_FEATURES ((TOTAL_CONV2_FEATURES / TIME_STEPS) * TIME_STEPS)

// ==================== VRAIS NOMBRES DE PARAMÈTRES ====================
// 373128 est le nombre d'OPÉRATIONS, PAS de paramètres !
#define TOTAL_PARAMETERS 7651

// ==================== NOMBRE D'OPÉRATIONS ====================
#define CONV1_OPS (6 * 180 * 5 * 2)  // 10800
#define CONV2_OPS (12 * 90 * 3 * 2)  // 6480
#define LSTM_OPS (4 * 24 * (33 + 24) * 32 * 2)  // 350208
#define LIF_OPS (32 * 24 * 3)  // 2304
#define FC_OPS ((24 * (12 + 24) + 12 * 24 + 5 * 12) * 2)  // 2424
#define ROUTER_OPS ((12 * (12 + 24) + 2 * 12) * 2)  // 912
#define TOTAL_OPS (CONV1_OPS + CONV2_OPS + LSTM_OPS + LIF_OPS + FC_OPS + ROUTER_OPS)  // 373128

// ==================== MÉMOIRE ====================
#define M_WEIGHTS_BYTES 7651
#define M_WEIGHTS_KIB 7.47
#define M_ACTIVATION_PEAK_BYTES 11014
#define M_STATE_BYTES 792
#define M_RUNTIME_BYTES 2560
#define M_CODE_BYTES 12288

// RV32X-SQ Extensions
#define RV32X_CUSTOM1  0x0B
#define RV32X_CUSTOM2  0x0C
#define RV32X_CUSTOM3  0x0D

// Thermal management
#define TEMP_THRESHOLD_HIGH   70
#define TEMP_THRESHOLD_MEDIUM 50
#define PRECISION_HIGH        0
#define PRECISION_MEDIUM      1
#define PRECISION_LOW         2

// Fixed-point configuration
#define Q_BITS 8
#define FIXED_SCALE 8
#define FIXED_SCALE_VAL 256

// ==================== BUFFER STRUCTURE ====================
typedef struct {
    int8_t input_buf[INPUT_SIZE];
    int32_t conv1_out[CONV1_FILTERS * CONV1_OUT_SIZE];
    int32_t conv2_out[CONV2_FILTERS * CONV2_OUT_SIZE];
    int8_t snn_input[SNN_INPUT_SIZE * TIME_STEPS];
    int8_t spike_train[TIME_STEPS * SNN_HIDDEN];
    int8_t lstm_state[LSTM_HIDDEN];
    int8_t router_output[2];
    int32_t fused_features[FUSION_SIZE];
    int32_t fc1_out[FC1_SIZE];
    int32_t output[OUTPUT_SIZE];
    uint8_t precision_mode;
    int16_t temperature;
    uint32_t total_cycles;
    uint32_t inference_count;
} HybridModelBuffers;

// ==================== WEIGHT DECLARATIONS ====================
extern const int8_t conv1_weight[30];
extern const int32_t conv1_weight_scale;

extern const int8_t conv1_bias[6];
extern const int32_t conv1_bias_scale;

extern const int8_t conv2_weight[216];
extern const int32_t conv2_weight_scale;

extern const int8_t conv2_bias[12];
extern const int32_t conv2_bias_scale;

extern const int8_t lstm_weight_ih[3168];
extern const int32_t lstm_weight_ih_scale;

extern const int8_t lstm_weight_hh[2304];
extern const int32_t lstm_weight_hh_scale;

extern const int8_t lstm_bias_ih[96];
extern const int32_t lstm_bias_ih_scale;

extern const int8_t lstm_bias_hh[96];
extern const int32_t lstm_bias_hh_scale;

extern const int8_t router_fc1_weight[432];
extern const int32_t router_fc1_weight_scale;

extern const int8_t router_fc1_bias[12];
extern const int32_t router_fc1_bias_scale;

extern const int8_t router_fc2_weight[24];
extern const int32_t router_fc2_weight_scale;

extern const int8_t router_fc2_bias[2];
extern const int32_t router_fc2_bias_scale;

extern const int8_t fusion_weight[864];
extern const int32_t fusion_weight_scale;

extern const int8_t fusion_bias[24];
extern const int32_t fusion_bias_scale;

extern const int8_t fc1_weight[288];
extern const int32_t fc1_weight_scale;

extern const int8_t fc1_bias[12];
extern const int32_t fc1_bias_scale;

extern const int8_t fc2_weight[60];
extern const int32_t fc2_weight_scale;

extern const int8_t fc2_bias[5];
extern const int32_t fc2_bias_scale;

// ==================== FUNCTION PROTOTYPES ====================
void model_init(HybridModelBuffers* buffers);
void model_predict(HybridModelBuffers* buffers, const int8_t* input, uint8_t domain);
void thermal_management(HybridModelBuffers* buffers);
uint8_t feature_router(const int8_t* spatial_features, const int8_t* temporal_features);

int32_t custom1_mac(int8_t a, int8_t b, int32_t acc);
int8_t custom2_lif(int8_t input, int8_t membrane_potential, int8_t threshold);
int8_t custom3_fusion(int8_t snn_out, int8_t qnn_out, int8_t attention_weight);

void benchmark_latency(HybridModelBuffers* buffers, uint8_t domain, uint32_t iterations);
float calculate_tops(uint32_t cycles, uint32_t operations, uint32_t cpu_freq_hz);
float calculate_tops_w(float tops, uint32_t power_mw);

#endif // MODEL_WEIGHTS_H
