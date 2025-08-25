#!/bin/bash

# Script para ejecutar el checker detallado de posiciones de Hyperliquid
# Este script activa el entorno virtual y ejecuta el script detallado de Python

echo "🚀 Activando entorno virtual y ejecutando Hyperliquid Detailed Info..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script detallado
python hyperliquid_detailed_info.py

echo ""
echo "✅ Script detallado completado" 