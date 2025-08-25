#!/bin/bash

# Script para ampliar posiciones en Hyperliquid
# Este script activa el entorno virtual y ejecuta el script de ampliación de posiciones

echo "🚀 Activando entorno virtual y ejecutando ampliación de posiciones..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script de ampliación de posiciones
python hyperliquid_increase_position.py

echo ""
echo "✅ Script de ampliación completado" 