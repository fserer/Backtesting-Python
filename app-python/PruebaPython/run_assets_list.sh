#!/bin/bash

# Script para obtener la lista completa de activos de Hyperliquid
# Este script activa el entorno virtual y ejecuta el script de activos

echo "🚀 Obteniendo lista de activos de Hyperliquid..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script de activos
python hyperliquid_assets_list.py

echo ""
echo "✅ Lista de activos obtenida"
echo "📁 Archivos generados:"
echo "   - hyperliquid_assets.json (formato JSON)"
echo "   - hyperliquid_assets.csv (formato CSV)" 