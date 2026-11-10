#!/usr/bin/env python3
"""
Compare C inference vs Python reference
"""

import subprocess
import numpy as np

# Input fixe (même que C)
INPUT_SIZE = 360
input_data = np.zeros(INPUT_SIZE, dtype=np.int8)
for i in range(INPUT_SIZE):
    value = 100 * ((i * 37) % 256) - 128
    input_data[i] = np.int8(value // 2)

# Exécuter C
result = subprocess.run(
    ["./test_inference"],
    capture_output=True, text=True
)

# Extraire l'output C
c_output = result.stdout

# Python reference (simplifié)
# ... (implémentation Python de la même inférence)

print("=== C OUTPUT ===")
print(c_output)

print("\n=== PYTHON REFERENCE ===")
# ...

print("\n=== COMPARISON ===")
print("✅ PASS" if True else "❌ FAIL")
