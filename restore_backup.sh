#!/bin/bash

# Script de restore para la base de datos unificada
# Usa bind mount: ./backend/data/backtesting.db

# Verificar argumento
if [ $# -eq 0 ]; then
    echo "Uso: $0 <archivo_backup.db>"
    echo "Ejemplo: $0 backup_20250826_020001.db"
    exit 1
fi

BACKUP_FILE=$1
BACKUP_DIR="/opt/backups"
FULL_BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Verificar que el archivo existe
if [ ! -f "$FULL_BACKUP_PATH" ]; then
    echo "Error: El archivo de backup no existe: $FULL_BACKUP_PATH"
    echo "Backups disponibles:"
    ls -la $BACKUP_DIR/backup_*.db 2>/dev/null || echo "No hay backups disponibles"
    exit 1
fi

# Encontrar el contenedor del backend
CONTAINER_NAME=$(docker ps --filter "ancestor=app-python-backend" --format "{{.Names}}")

if [ -z "$CONTAINER_NAME" ]; then
    echo "Error: No se encontró el contenedor del backend"
    exit 1
fi

echo "Contenedor encontrado: $CONTAINER_NAME"
echo "Restaurando desde: $FULL_BACKUP_PATH"

# Parar el backend para evitar conflictos
echo "Parando el backend..."
docker-compose -f docker-compose.prod.yml stop backend

# Copiar backup al contenedor
echo "Copiando backup al contenedor..."
docker cp "$FULL_BACKUP_PATH" $CONTAINER_NAME:/tmp/backup.db

# Restaurar la base de datos
echo "Restaurando base de datos..."
docker exec $CONTAINER_NAME sqlite3 /app/data/backtesting.db ".restore '/tmp/backup.db'"

# Limpiar archivo temporal
docker exec $CONTAINER_NAME rm /tmp/backup.db

# Reiniciar el backend
echo "Reiniciando el backend..."
docker-compose -f docker-compose.prod.yml up -d backend

echo "Restore completado exitosamente!"
echo "Verificando datos..."
docker exec $CONTAINER_NAME sqlite3 /app/data/backtesting.db "SELECT 'Tablas:' as info, COUNT(*) as count FROM sqlite_master WHERE type='table';"
