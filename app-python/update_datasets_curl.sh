#!/bin/bash

# Script para actualizar automáticamente todos los datasets desde NodeCharts
# Uso: ./update_datasets_curl.sh
# Para cron: */25 * * * * /ruta/completa/update_datasets_curl.sh

# Configuración
BACKEND_URL="http://localhost:8000"
LOG_FILE="/tmp/dataset_update.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 🚀 Iniciando actualización automática de datasets..." >> $LOG_FILE

# Realizar la actualización
RESPONSE=$(curl -s -X POST \
  "$BACKEND_URL/api/datasets/update-all" \
  -H "Content-Type: application/json" \
  -w "\nHTTP_STATUS:%{http_code}")

# Extraer el código de estado HTTP
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d':' -f2)
JSON_RESPONSE=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

if [ "$HTTP_STATUS" = "200" ]; then
    # Parsear la respuesta JSON para obtener estadísticas
    TOTAL_DATASETS=$(echo "$JSON_RESPONSE" | grep -o '"success":true' | wc -l)
    TOTAL_ROWS=$(echo "$JSON_RESPONSE" | grep -o '"rows_added":[0-9]*' | sed 's/"rows_added"://' | awk '{sum+=$1} END {print sum}')
    
    echo "[$DATE] ✅ Actualización exitosa - $TOTAL_DATASETS datasets procesados, $TOTAL_ROWS registros añadidos" >> $LOG_FILE
    
    # Mostrar detalles por dataset
    echo "[$DATE] 📋 Detalles por dataset:" >> $LOG_FILE
    echo "$JSON_RESPONSE" | grep -o '"[^"]*":\s*{[^}]*}' | while read -r line; do
        DATASET_NAME=$(echo "$line" | grep -o '"[^"]*":' | head -1 | sed 's/"//g' | sed 's/://')
        SUCCESS=$(echo "$line" | grep -o '"success":true' | wc -l)
        ROWS=$(echo "$line" | grep -o '"rows_added":[0-9]*' | sed 's/"rows_added"://')
        
        if [ "$SUCCESS" -eq 1 ]; then
            echo "[$DATE]   ✅ $DATASET_NAME: $ROWS registros" >> $LOG_FILE
        else
            echo "[$DATE]   ❌ $DATASET_NAME: Error" >> $LOG_FILE
        fi
    done
else
    echo "[$DATE] ❌ Error en actualización - HTTP Status: $HTTP_STATUS" >> $LOG_FILE
    echo "[$DATE] 📄 Respuesta: $JSON_RESPONSE" >> $LOG_FILE
fi

echo "[$DATE] 🎉 Actualización completada" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE
