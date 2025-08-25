#!/bin/bash

# Script para abrir nuevas posiciones en Hyperliquid
# Este script activa el entorno virtual y ejecuta el script de apertura de posiciones

echo "🚀 Activando entorno virtual y ejecutando apertura de nuevas posiciones..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script de apertura de posiciones
python hyperliquid_open_position.py

echo ""
echo "✅ Script de apertura completado" 