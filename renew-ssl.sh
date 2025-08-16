#!/bin/bash

# Script para renovar certificados SSL automáticamente
# Ejecutar con: sudo bash renew-ssl.sh

echo "🔄 Renovando certificados SSL..."

# Renovar certificados
certbot renew --quiet

# Verificar si la renovación fue exitosa
if [ $? -eq 0 ]; then
    echo "✅ Certificados renovados exitosamente"
    
    # Crear directorio ssl si no existe
    mkdir -p ssl
    
    # Copiar certificados renovados
    cp /etc/letsencrypt/live/backtest.bitcoinrocket.com/fullchain.pem ssl/
    cp /etc/letsencrypt/live/backtest.bitcoinrocket.com/privkey.pem ssl/
    
    # Ajustar permisos
    chmod 644 ssl/fullchain.pem
    chmod 600 ssl/privkey.pem
    
    echo "📁 Certificados copiados a directorio ssl/"
    
    # Reiniciar contenedor nginx
    docker restart backtesting-nginx
    
    echo "🔄 Contenedor nginx reiniciado"
else
    echo "❌ Error al renovar certificados"
    exit 1
fi

echo "✅ Proceso de renovación completado"
