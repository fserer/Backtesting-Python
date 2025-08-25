#!/bin/bash

# Script para reducir posiciones en Hyperliquid
# Este script activa el entorno virtual y ejecuta el script de reducción de posiciones

echo "🚀 Activando entorno virtual y ejecutando reducción de posiciones..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script de reducción de posiciones
python hyperliquid_reduce_position.py

echo ""
echo "✅ Script de reducción completado" 