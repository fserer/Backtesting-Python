#!/bin/bash

# Script para ejecutar la demostración de payloads de Hyperliquid
# Este script muestra los payloads que se enviarían a la API sin ejecutar órdenes reales

echo "🚀 Ejecutando demostración de payloads de Hyperliquid..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el script de demostración
python hyperliquid_demo_payloads.py

echo ""
echo "✅ Demostración completada"
echo "💡 Revisa los payloads mostrados arriba" 