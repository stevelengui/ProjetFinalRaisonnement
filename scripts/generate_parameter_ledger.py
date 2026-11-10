#!/usr/bin/env python3
"""
Génère parameter_ledger.csv et memory_ledger.csv
à partir de model_weights.h (recherche automatique)
"""

import re
import csv
import os
from datetime import datetime

# Chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "artifacts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def find_model_weights_file():
    """Cherche model_weights.h dans plusieurs emplacements"""
    possible_paths = [
        os.path.join(BASE_DIR, "firmware/model/model_weights.h"),
        os.path.join(BASE_DIR, "llm_nas/model_weights.h"),
        os.path.join(BASE_DIR, "model_weights.h"),
        os.path.join(BASE_DIR, "backend/model_weights.h"),
        os.path.join(BASE_DIR, "hardware/model_weights.h"),
    ]
    
    # Chercher récursivement si pas trouvé
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Recherche récursive
    for root, dirs, files in os.walk(BASE_DIR):
        if "model_weights.h" in files:
            return os.path.join(root, "model_weights.h")
    
    return None


# ============================================================
# PARSER model_weights.h
# ============================================================

def parse_model_weights_header(filepath):
    """Parse les déclarations extern depuis model_weights.h"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern: extern const int8_t NAME[SIZE];
    pattern = r'extern const (int8_t|int32_t) (\w+)\[(\d+)\];'
    matches = re.findall(pattern, content)
    
    tensors = []
    for dtype, name, size in matches:
        size = int(size)
        bytes_per_element = 1 if dtype == "int8_t" else 4
        
        tensors.append({
            "name": name,
            "dtype": dtype,
            "n_elements": size,
            "bytes_per_element": bytes_per_element,
            "total_bytes": size * bytes_per_element,
            "is_weight": "weight" in name,
            "is_bias": "bias" in name,
            "is_scale": "scale" in name,
            "category": classify_tensor(name),
            "layer": extract_layer_name(name)
        })
    
    return tensors


def classify_tensor(name):
    """Classifie un tenseur"""
    if "conv1" in name: return "conv1"
    if "conv2" in name: return "conv2"
    if "lstm" in name: return "lstm"
    if "router" in name: return "router"
    if "fusion" in name: return "fusion"
    if "fc1" in name: return "fc1"
    if "fc2" in name: return "fc2"
    return "other"


def extract_layer_name(name):
    """Extrait le nom de la couche"""
    parts = name.split("_")
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return parts[0]


# ============================================================
# GÉNÉRER parameter_ledger.csv
# ============================================================

def generate_parameter_ledger(tensors):
    """Génère le ledger des paramètres"""
    
    filepath = os.path.join(OUTPUT_DIR, "parameter_ledger.csv")
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            "tensor_name", "layer", "dtype", "n_elements", 
            "bytes_per_element", "total_bytes", 
            "is_weight", "is_bias", "is_scale",
            "trainable", "packed", "exported"
        ])
        
        total_elements = 0
        total_bytes = 0
        
        for t in tensors:
            is_trainable = t["is_weight"] or t["is_bias"]
            is_packed = False
            is_exported = True
            
            writer.writerow([
                t["name"], t["layer"], t["dtype"], t["n_elements"],
                t["bytes_per_element"], t["total_bytes"],
                t["is_weight"], t["is_bias"], t["is_scale"],
                is_trainable, is_packed, is_exported
            ])
            
            if is_trainable:
                total_elements += t["n_elements"]
                total_bytes += t["total_bytes"]
        
        writer.writerow([
            "TOTAL", "", "", total_elements,
            "", total_bytes,
            "", "", "", "", "", ""
        ])
    
    return filepath, total_elements, total_bytes


# ============================================================
# GÉNÉRER memory_ledger.csv
# ============================================================

def generate_memory_ledger(tensors):
    """Génère le ledger mémoire avec provenance"""
    
    filepath = os.path.join(OUTPUT_DIR, "memory_ledger.csv")
    
    weights_bytes = sum(t["total_bytes"] for t in tensors if t["is_weight"] or t["is_bias"])
    
    components = [
        {
            "component": "M_weights",
            "description": "Poids quantifiés (int8_t)",
            "value_bytes": weights_bytes,
            "provenance": "DER_FROM_ARTIFACTS",
            "method": "Somme des arrays depuis model_weights.h",
            "is_peak": False,
            "is_persistent": True,
            "memory_type": "Flash"
        },
        {
            "component": "M_activation_peak",
            "description": "Activations peak (int32_t buffers)",
            "value_bytes": 11014,
            "provenance": "DER",
            "method": "Calcul depuis BUFFER_SIZES",
            "is_peak": True,
            "is_persistent": False,
            "memory_type": "SRAM"
        },
        {
            "component": "M_state",
            "description": "État LSTM + SNN",
            "value_bytes": 792,
            "provenance": "DER",
            "method": "24 (LSTM) + 768 (SNN)",
            "is_peak": False,
            "is_persistent": True,
            "memory_type": "SRAM"
        },
        {
            "component": "M_runtime",
            "description": "Stack + heap + temp",
            "value_bytes": 2560,
            "provenance": "ESTIMATED",
            "method": "Estimation",
            "is_peak": True,
            "is_persistent": False,
            "memory_type": "SRAM"
        },
        {
            "component": "M_code",
            "description": "Code machine (.text + .data)",
            "value_bytes": 12288,
            "provenance": "ESTIMATED",
            "method": "Estimation",
            "is_peak": False,
            "is_persistent": True,
            "memory_type": "Flash"
        },
    ]
    
    flash_total = sum(c["value_bytes"] for c in components if c["memory_type"] == "Flash")
    sram_peak = max(c["value_bytes"] for c in components if c["memory_type"] == "SRAM" and c["is_peak"])
    sram_persistent = sum(c["value_bytes"] for c in components if c["memory_type"] == "SRAM" and not c["is_peak"])
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            "component", "description", "value_bytes", "value_kib",
            "provenance", "method", "is_peak", "is_persistent", "memory_type"
        ])
        
        for c in components:
            writer.writerow([
                c["component"], c["description"], 
                c["value_bytes"], round(c["value_bytes"]/1024, 2),
                c["provenance"], c["method"], 
                c["is_peak"], c["is_persistent"], c["memory_type"]
            ])
        
        writer.writerow([])
        writer.writerow(["=== TOTALS ==="])
        writer.writerow(["M_weights (Flash)", "", weights_bytes, round(weights_bytes/1024, 2)])
        writer.writerow(["M_code (Flash)", "", 12288, round(12288/1024, 2)])
        writer.writerow(["Total Flash", "", flash_total, round(flash_total/1024, 2)])
        writer.writerow([])
        writer.writerow(["SRAM peak", "", sram_peak, round(sram_peak/1024, 2)])
        writer.writerow(["SRAM persistent", "", sram_persistent, round(sram_persistent/1024, 2)])
        writer.writerow(["SRAM total", "", sram_peak + sram_persistent, round((sram_peak + sram_persistent)/1024, 2)])
        writer.writerow([])
        writer.writerow(["NOTE: M_total = Flash + SRAM n'est PAS une somme valide"])
        writer.writerow(["Utiliser M_SRAM_peak et M_Flash séparément"])
    
    return filepath, components, flash_total, sram_peak, sram_persistent


# ============================================================
# RÉCONCILIER LES INCOHÉRENCES
# ============================================================

def reconcile_inconsistencies(tensors):
    """Réconcilie les incohérences identifiées par le directeur"""
    
    print("=" * 70)
    print("🔍 RÉCONCILIATION DES INCOHÉRENCES")
    print("=" * 70)
    
    layer_totals = {}
    for t in tensors:
        if t["is_weight"] or t["is_bias"]:
            cat = t["category"]
            layer_totals[cat] = layer_totals.get(cat, 0) + t["n_elements"]
    
    print("\n📊 Somme par catégorie de couche :")
    total = 0
    for cat, count in sorted(layer_totals.items()):
        print(f"   {cat}: {count:,} paramètres")
        total += count
    print(f"   ─────────────────────────")
    print(f"   TOTAL: {total:,} paramètres")
    
    if total == 7651:
        print(f"\n✅ Total cohérent : {total} = 7,651")
    else:
        print(f"\n❌ INCOHÉRENCE : {total} ≠ 7,651")
        print(f"   Écart : {abs(total - 7651)} paramètres")
    
    scales = [t for t in tensors if t["is_scale"]]
    if scales:
        print(f"\n⚠️ {len(scales)} scales (int32_t) non comptées comme paramètres :")
        for s in scales:
            print(f"   {s['name']}: {s['total_bytes']} bytes")
    
    return layer_totals, total


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("📊 GÉNÉRATION DES LEDGERS")
    print("=" * 70)
    
    # Trouver le fichier
    print("\n🔍 Recherche de model_weights.h...")
    model_weights_h = find_model_weights_file()
    
    if not model_weights_h:
        print("❌ model_weights.h NON TROUVÉ")
        print("\nEmplacements testés :")
        print("   - firmware/model/model_weights.h")
        print("   - llm_nas/model_weights.h")
        print("   - model_weights.h")
        print("   - backend/model_weights.h")
        print("   - hardware/model_weights.h")
        print("\nVeuillez placer model_weights.h dans l'un de ces emplacements.")
        return
    
    print(f"✅ Trouvé : {model_weights_h}")
    
    # Parser
    tensors = parse_model_weights_header(model_weights_h)
    print(f"\n✅ {len(tensors)} tenseurs parsés")
    
    # Générer parameter_ledger.csv
    param_path, total_elements, total_bytes = generate_parameter_ledger(tensors)
    print(f"\n📄 {param_path}")
    print(f"   Total paramètres: {total_elements:,}")
    print(f"   Total bytes: {total_bytes:,}")
    
    # Générer memory_ledger.csv
    mem_path, components, flash_total, sram_peak, sram_persistent = generate_memory_ledger(tensors)
    print(f"\n📄 {mem_path}")
    print(f"   Flash total: {flash_total:,} bytes ({flash_total/1024:.2f} KiB)")
    print(f"   SRAM peak: {sram_peak:,} bytes ({sram_peak/1024:.2f} KiB)")
    print(f"   SRAM persistent: {sram_persistent:,} bytes ({sram_persistent/1024:.2f} KiB)")
    
    # Réconcilier
    reconcile_inconsistencies(tensors)
    
    # Résumé
    print("\n" + "=" * 70)
    print("📝 VALEURS À UTILISER DANS L'ARTICLE")
    print("=" * 70)
    print(f"   TOTAL_PARAMETERS = {total_elements:,}")
    print(f"   M_weights = {total_bytes:,} bytes = {total_bytes/1024:.2f} KiB")
    print(f"   M_Flash = {flash_total:,} bytes = {flash_total/1024:.2f} KiB")
    print(f"   M_SRAM_peak = {sram_peak:,} bytes = {sram_peak/1024:.2f} KiB")
    print(f"   M_SRAM_total = {sram_peak + sram_persistent:,} bytes = {(sram_peak + sram_persistent)/1024:.2f} KiB")
    print(f"\n   ⚠️ NE PAS UTILISER M_total = {flash_total + sram_peak + sram_persistent:,}")
    print(f"      car c'est une somme hétérogène (Flash + SRAM)")
    
    # Rapport
    report_path = os.path.join(OUTPUT_DIR, "ledger_report.md")
    with open(report_path, 'w') as f:
        f.write("# Rapport de Réconciliation des Ledgers\n\n")
        f.write(f"Généré: {datetime.now().isoformat()}\n")
        f.write(f"Source: `{model_weights_h}`\n\n")
        f.write(f"## Paramètres\n")
        f.write(f"- Total: **{total_elements:,}**\n")
        f.write(f"- Bytes: **{total_bytes:,}** ({total_bytes/1024:.2f} KiB)\n\n")
        f.write(f"## Mémoire\n")
        f.write(f"- M_weights: {total_bytes:,} bytes ({total_bytes/1024:.2f} KiB)\n")
        f.write(f"- M_Flash: {flash_total:,} bytes ({flash_total/1024:.2f} KiB)\n")
        f.write(f"- M_SRAM_peak: {sram_peak:,} bytes ({sram_peak/1024:.2f} KiB)\n")
        f.write(f"- M_SRAM_persistent: {sram_persistent:,} bytes ({sram_persistent/1024:.2f} KiB)\n")
        f.write(f"- M_SRAM_total: {sram_peak + sram_persistent:,} bytes ({(sram_peak + sram_persistent)/1024:.2f} KiB)\n\n")
        f.write(f"## ⚠️ Avertissement\n")
        f.write(f"Ne PAS utiliser M_total = Flash + SRAM (somme hétérogène).\n")
        f.write(f"Utiliser M_Flash et M_SRAM_peak séparément.\n")
    
    print(f"\n💾 Rapport: {report_path}")


if __name__ == "__main__":
    main()
