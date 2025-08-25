#!/bin/bash

# Script para cerrar posiciones en Hyperliquid
# Este script activa el entorno virtual y ejecuta el script de cierre de posiciones

echo "🚀 Activando entorno virtual y ejecutando cierre de posiciones..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script de cierre de posiciones
python hyperliquid_close_position.py

echo ""
echo "✅ Script de cierre completado" 