#!/bin/bash
# P1-2 : Code Generation complet

cd ~/ProjetFinalRaisonnement/artifacts/generated_code

echo "=========================================="
echo "🔧 P1-2 : CODE GENERATION COMPLET"
echo "=========================================="
echo ""

# 1. Compilation host
echo "📊 1. Compilation host (gcc)..."
gcc -O2 -Wall -o test_inference main_inference.c 2>&1 | tee compile.log
if [ -f test_inference ]; then
    echo "✅ Compilation host OK"
else
    echo "❌ Compilation host échouée"
    exit 1
fi
echo ""

# 2. Exécution host
echo "📊 2. Exécution host..."
./test_inference > host_output.log 2>&1
cat host_output.log
echo ""

# 3. Comparaison C vs Python
echo "📊 3. Comparaison C vs Python..."
python compare_c_python.py 2>&1 | tee c_python_comparison.log
echo ""

# 4. Cross-compile RISC-V
echo "📊 4. Cross-compile RISC-V..."
if command -v riscv64-unknown-elf-gcc &> /dev/null; then
    riscv64-unknown-elf-gcc -O2 -Wall -nostdlib -ffreestanding \
        -o test_inference_riscv main_inference_riscv.c 2>&1 | tee cross_compile.log
    
    if [ -f test_inference_riscv ]; then
        echo "✅ Cross-compile OK"
        file test_inference_riscv
        riscv64-unknown-elf-size test_inference_riscv
    else
        echo "❌ Cross-compile échoué"
    fi
else
    echo "⚠️ riscv64-unknown-elf-gcc non disponible"
fi
echo ""

echo "=========================================="
echo "✅ P1-2 TERMINÉ"
echo "=========================================="
