#!/bin/bash

# Script para ejecutar el script de órdenes abiertas en Hyperliquid

echo "🚀 Ejecutando script de órdenes abiertas en Hyperliquid..."

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    echo "📦 Activando entorno virtual..."
    source venv/bin/activate
fi

# Ejecutar el script
python3 hyperliquid_open_orders.py

echo "✅ Script completado"


