#!/bin/bash

# Script de backup para la base de datos unificada
# Usa bind mount: ./backend/data/backtesting.db

# Configuración
BACKUP_DIR="/opt/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backup_${DATE}.db"

# Crear directorio de backup si no existe
mkdir -p $BACKUP_DIR

# Encontrar el contenedor del backend
CONTAINER_NAME=$(docker ps --filter "ancestor=app-python-backend" --format "{{.Names}}")

if [ -z "$CONTAINER_NAME" ]; then
    echo "Error: No se encontró el contenedor del backend"
    exit 1
fi

echo "Contenedor encontrado: $CONTAINER_NAME"

# Crear backup
echo "Creando backup: $BACKUP_FILE"
docker exec $CONTAINER_NAME sqlite3 /app/data/backtesting.db ".backup '/tmp/$BACKUP_FILE'"

# Copiar backup al host
echo "Copiando backup al host..."
docker cp $CONTAINER_NAME:/tmp/$BACKUP_FILE $BACKUP_DIR/$BACKUP_FILE

# Limpiar archivo temporal del contenedor
docker exec $CONTAINER_NAME rm /tmp/$BACKUP_FILE

# Mantener solo los últimos 7 días de backups
echo "Limpiando backups antiguos (más de 7 días)..."
find $BACKUP_DIR -name "backup_*.db" -mtime +7 -delete

echo "Backup completado: $BACKUP_DIR/$BACKUP_FILE"
echo "Backups disponibles:"
ls -la $BACKUP_DIR/backup_*.db 2>/dev/null || echo "No hay backups disponibles"
