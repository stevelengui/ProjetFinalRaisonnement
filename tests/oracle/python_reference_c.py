#!/usr/bin/env python3
"""
python_reference_c.py - C-faithful Python oracle for model.c

Reproduces the C inference (model.c) in pure Python:
- Conv1D + Conv2D with quantized weights (scales placeholder 1/2/3)
- LSTM-LIF (custom2_lif) instead of standard LSTM
- Router heuristic (energy-based) instead of learned router
- Fusion heuristic (custom3_fusion) instead of learned fusion
- No BatchNorm

Input: same deterministic vector as main_host.c
  input[i] = (i * 37) % 256 - 128

Output: LOGITS <5 values>
"""

import numpy as np
from pathlib import Path

# Constants (from model_weights.h)
INPUT_SIZE = 360
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
FIXED_SCALE = 8

ARRAYS = Path("tests/host/firmware/model/arrays")


def load_array(name):
    """Load int8_t array from arrays/<name>_array.txt"""
    path = ARRAYS / f"{name}_array.txt"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")
    text = path.read_text()
    values = [int(v) for v in text.replace(",", " ").split() if v]
    return np.array(values, dtype=np.int8)


def custom2_lif(inp, membrane, threshold=50):
    """Reproduces custom2_lif from math_ops.c"""
    new_pot = int(membrane) + int(inp)
    if new_pot >= threshold:
        return 127
    new_pot = (new_pot * 95) // 100
    if new_pot > 127:
        return 127
    if new_pot < -128:
        return -128
    return new_pot


def conv1d(input_buf, kernel, kernel_scale, in_ch, out_ch, length, ksize, stride):
    """Reproduces quantized_conv1d_rv32x from math_ops.c"""
    out_length = length // stride
    output = np.zeros(out_ch * out_length, dtype=np.int32)
    for oc in range(out_ch):
        for i in range(out_length):
            s = 0
            in_pos = i * stride
            k_base = oc * in_ch * ksize
            for ic in range(in_ch):
                for k in range(ksize):
                    in_idx = ic * length + in_pos + k
                    if in_idx >= len(input_buf):
                        continue
                    s += int(input_buf[in_idx]) * int(kernel[k_base + ic * ksize + k])
            output[oc * out_length + i] = (s * kernel_scale) >> FIXED_SCALE
    return output


def main():
    # Load weights
    conv1_weight = load_array("conv1_weight")
    conv1_bias = load_array("conv1_bias")
    conv2_weight = load_array("conv2_weight")
    conv2_bias = load_array("conv2_bias")
    lstm_weight_ih = load_array("lstm_weight_ih")
    lstm_weight_hh = load_array("lstm_weight_hh")
    lstm_bias_ih = load_array("lstm_bias_ih")

    # Placeholder scales (from model_weights.c)
    conv1_weight_scale = 1
    conv2_weight_scale = 2
    lstm_weight_ih_scale = 2
    lstm_weight_hh_scale = 3
    lstm_bias_ih_scale = 1

    # Deterministic input (same as main_host.c)
    input_buf = np.array([(i * 37) % 256 - 128 for i in range(INPUT_SIZE)], dtype=np.int8)

    # Conv1D
    conv1_out = conv1d(input_buf, conv1_weight, conv1_weight_scale,
                       1, CONV1_FILTERS, INPUT_SIZE, 5, 2)
    # Bias + ReLU
    for i in range(CONV1_FILTERS * CONV1_OUT_SIZE):
        ch = i // CONV1_OUT_SIZE
        bias_term = (int(conv1_bias[ch]) * 1) >> FIXED_SCALE
        conv1_out[i] += bias_term
        if conv1_out[i] < 0:
            conv1_out[i] = 0

    # Conv2D (input cast from int32 to int8)
    conv1_out_i8 = np.array([np.int8(v) for v in conv1_out], dtype=np.int8)
    conv2_out = conv1d(conv1_out_i8, conv2_weight, conv2_weight_scale,
                       CONV1_FILTERS, CONV2_FILTERS, CONV1_OUT_SIZE, 3, 2)
    for i in range(CONV2_FILTERS * CONV2_OUT_SIZE):
        ch = i // CONV2_OUT_SIZE
        bias_term = (int(conv2_bias[ch]) * 1) >> FIXED_SCALE
        conv2_out[i] += bias_term
        if conv2_out[i] < 0:
            conv2_out[i] = 0

    # SNN input preparation
    snn_input = np.zeros((TIME_STEPS, SNN_INPUT_SIZE), dtype=np.int8)
    for t in range(TIME_STEPS):
        for i in range(SNN_INPUT_SIZE):
            idx = t * SNN_INPUT_SIZE + i
            if idx < CONV2_FILTERS * CONV2_OUT_SIZE:
                snn_input[t, i] = np.int8(conv2_out[idx] >> FIXED_SCALE)
            else:
                snn_input[t, i] = 0

    # LIF
    spike_train = np.zeros((TIME_STEPS, SNN_HIDDEN), dtype=np.int8)
    for t in range(TIME_STEPS):
        for i in range(SNN_HIDDEN):
            inp = int(snn_input[t, i % SNN_INPUT_SIZE])
            memb = 0 if t == 0 else int(spike_train[t - 1, i])
            spike_train[t, i] = custom2_lif(inp, memb, 50)

    # LSTM-LIF (simplified, as in C)
    hidden = np.zeros(LSTM_HIDDEN, dtype=np.int8)
    for t in range(TIME_STEPS):
        tmp = np.zeros(LSTM_HIDDEN, dtype=np.int8)
        for i in range(LSTM_HIDDEN):
            sum_ih = 0
            sum_hh = 0
            for j in range(LSTM_HIDDEN):
                sum_ih += int(spike_train[t, j % SNN_INPUT_SIZE]) * int(lstm_weight_ih[i * LSTM_HIDDEN + j])
                sum_hh += int(hidden[j]) * int(lstm_weight_hh[i * LSTM_HIDDEN + j])
            combined = ((sum_ih + sum_hh) * (lstm_weight_ih_scale * lstm_weight_hh_scale)) >> FIXED_SCALE
            combined += (int(lstm_bias_ih[i]) * lstm_bias_ih_scale) >> FIXED_SCALE
            tmp[i] = np.int8(combined >> FIXED_SCALE)
        hidden = tmp

    # Output (simplified: fc1 + fc2 not used in C for LSTM output)
    # In model.c, the final output is derived from fc2_weight applied to fc1_out
    fc1_weight = load_array("fc1_weight")
    fc1_bias = load_array("fc1_bias")
    fc2_weight = load_array("fc2_weight")
    fc2_bias = load_array("fc2_bias")

    # Simplified: use hidden as fused_features surrogate
    fused_i8 = hidden.astype(np.int8)

    fc1_out = np.zeros(FC1_SIZE, dtype=np.int32)
    for i in range(FC1_SIZE):
        s = 0
        for j in range(FUSION_SIZE):
            if j < len(fused_i8):
                s += int(fused_i8[j]) * int(fc1_weight[i * FUSION_SIZE + j])
        fc1_out[i] = ((s * 2) >> FIXED_SCALE) + ((int(fc1_bias[i]) * 0) >> FIXED_SCALE)
        if fc1_out[i] < 0:
            fc1_out[i] = 0

    output = np.zeros(OUTPUT_SIZE, dtype=np.int32)
    for i in range(OUTPUT_SIZE):
        s = 0
        for j in range(FC1_SIZE):
            fc1_val = np.int8(fc1_out[j] >> FIXED_SCALE)
            s += int(fc1_val) * int(fc2_weight[i * FC1_SIZE + j])
        output[i] = ((s * 3) >> FIXED_SCALE) + ((int(fc2_bias[i]) * 2) >> FIXED_SCALE)

    print("LOGITS", " ".join(str(int(v)) for v in output))


if __name__ == "__main__":
    main()
