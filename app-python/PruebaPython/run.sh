#!/bin/bash

# Script para ejecutar el checker de posiciones de Hyperliquid
# Este script activa el entorno virtual y ejecuta el script de Python

echo "🚀 Activando entorno virtual y ejecutando Hyperliquid Positions Checker..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script
python hyperliquid_positions.py

echo ""
echo "✅ Script completado" 