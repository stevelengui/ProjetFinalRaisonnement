#!/usr/bin/env python3
"""
python_reference_torch.py - PyTorch oracle for the hybrid model

Loads best_hybrid_model_ecg.pth and runs the standard PyTorch forward pass
(BatchNorm, learned router, learned fusion, standard LSTM).

Input: same deterministic vector as main_host.c and python_reference_c.py
  input[i] = (i * 37) % 256 - 128

Output: LOGITS <5 values>
"""

import numpy as np
import torch
import torch.nn as nn
from pathlib import Path

# Same constants as model.py
INPUT_SIZE = 360
N_FEATURES = 1
CONV1_FILTERS = 6
CONV2_FILTERS = 12
LSTM_HIDDEN = 24
SNN_HIDDEN = 24
OUTPUT_SIZE = 5
TIME_STEPS = 32
FC1_SIZE = 12
FUSION_SIZE = 24
DROPOUT_RATE = 0.2


class LIFNeuron(nn.Module):
    def __init__(self, threshold=0.5, decay=0.95, time_steps=32):
        super().__init__()
        self.threshold = threshold
        self.decay = decay
        self.time_steps = time_steps

    def forward(self, x):
        batch_size, seq_len, features = x.shape
        membrane = torch.zeros(batch_size, features)
        spikes = torch.zeros(batch_size, seq_len, features)
        for t in range(seq_len):
            membrane = self.decay * membrane + x[:, t, :]
            s = (membrane > self.threshold).float()
            spikes[:, t, :] = s
            membrane = membrane * (1 - s)
        return spikes


class ECGHybridModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv_blocks = nn.Sequential(
            nn.Conv1d(N_FEATURES, CONV1_FILTERS, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm1d(CONV1_FILTERS),
            nn.ReLU(),
            nn.Dropout(DROPOUT_RATE),
            nn.Conv1d(CONV1_FILTERS, CONV2_FILTERS, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm1d(CONV2_FILTERS),
            nn.ReLU(),
            nn.Dropout(DROPOUT_RATE)
        )
        self.conv2_out_length = INPUT_SIZE // 4
        self.conv2_out_features = CONV2_FILTERS
        self.snn_input_size = (self.conv2_out_length * self.conv2_out_features) // TIME_STEPS
        self.lif_layer1 = LIFNeuron(threshold=0.5, decay=0.95, time_steps=TIME_STEPS)
        self.lif_layer2 = LIFNeuron(threshold=0.6, decay=0.9, time_steps=TIME_STEPS)
        self.lstm = nn.LSTM(self.snn_input_size, LSTM_HIDDEN, batch_first=True)
        self.feature_router = nn.Sequential(
            nn.Linear(CONV2_FILTERS + LSTM_HIDDEN, FC1_SIZE),
            nn.ReLU(),
            nn.Linear(FC1_SIZE, 2),
            nn.Softmax(dim=-1)
        )
        self.fusion_layer = nn.Linear(CONV2_FILTERS + LSTM_HIDDEN, FUSION_SIZE)
        self.classifier = nn.Sequential(
            nn.Linear(FUSION_SIZE, FC1_SIZE),
            nn.ReLU(),
            nn.Dropout(DROPOUT_RATE),
            nn.Linear(FC1_SIZE, OUTPUT_SIZE)
        )

    def forward(self, x, domain="ECG"):
        x_spatial = x.unsqueeze(1)
        x_spatial = self.conv_blocks(x_spatial)
        x_spatial = x_spatial.permute(0, 2, 1)
        total_features = self.conv2_out_length * self.conv2_out_features
        usable = (total_features // TIME_STEPS) * TIME_STEPS
        x_reshaped = x_spatial.contiguous().view(x.size(0), -1)[:, :usable]
        spatial_reshaped = x_reshaped.view(x.size(0), TIME_STEPS, -1)
        spike1 = self.lif_layer1(spatial_reshaped)
        spike2 = self.lif_layer2(spike1)
        temporal, _ = self.lstm(spike2)
        temporal = temporal[:, -1, :]
        spatial_avg = x_spatial.mean(dim=1)
        combined = torch.cat([temporal, spatial_avg], dim=1)
        attn = self.feature_router(combined)
        base = torch.tensor([0.7, 0.3])
        rw = base.unsqueeze(0) * attn
        rw = rw / rw.sum(dim=1, keepdim=True)
        alpha = rw[:, 0:1]
        fused = torch.cat([temporal * alpha, spatial_avg * (1 - alpha)], dim=1)
        fused = torch.relu(self.fusion_layer(fused))
        return self.classifier(fused)


def main():
    model = ECGHybridModel()
    model.load_state_dict(torch.load("tests/oracle/best_hybrid_model_ecg.pth", map_location="cpu"))
    model.eval()

    input_buf = np.array([(i * 37) % 256 - 128 for i in range(INPUT_SIZE)], dtype=np.float32)
    input_buf = (input_buf - input_buf.mean()) / (input_buf.std() + 1e-8)
    x = torch.from_numpy(input_buf).unsqueeze(0)

    with torch.no_grad():
        logits = model(x, domain="ECG")

    print("LOGITS", " ".join(f"{v:.4f}" for v in logits[0].tolist()))


if __name__ == "__main__":
    main()
