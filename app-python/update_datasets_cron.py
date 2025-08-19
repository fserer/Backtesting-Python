#!/usr/bin/env python3
"""
Script para actualizar automáticamente todos los datasets desde NodeCharts.
Diseñado para ejecutarse desde cron.

Uso: python3 update_datasets_cron.py
Para cron: */25 * * * * /usr/bin/python3 /ruta/completa/update_datasets_cron.py
"""

import sys
import os
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configuración
BACKEND_URL = "http://localhost:8000"
LOG_FILE = "/tmp/dataset_update.log"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def update_datasets() -> bool:
    """
    Actualiza todos los datasets desde NodeCharts.
    
    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario
    """
    try:
        logger.info("🚀 Iniciando actualización automática de datasets...")
        
        # Realizar la actualización
        response = requests.post(
            f"{BACKEND_URL}/api/datasets/update-all",
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutos de timeout
        )
        
        if response.status_code != 200:
            logger.error(f"❌ Error en actualización - HTTP Status: {response.status_code}")
            logger.error(f"📄 Respuesta: {response.text}")
            return False
        
        # Parsear la respuesta
        data = response.json()
        results = data.get('results', {})
        
        # Calcular estadísticas
        total_datasets = len(results)
        success_count = sum(1 for r in results.values() if r.get('success', False))
        total_rows = sum(r.get('rows_added', 0) for r in results.values())
        
        logger.info(f"✅ Actualización exitosa - {success_count}/{total_datasets} datasets exitosos")
        logger.info(f"📊 Total de registros añadidos: {total_rows}")
        
        # Mostrar detalles por dataset
        logger.info("📋 Detalles por dataset:")
        for dataset_name, result in results.items():
            if result.get('success'):
                rows = result.get('rows_added', 0)
                logger.info(f"   ✅ {dataset_name}: {rows} registros añadidos")
            else:
                error = result.get('error', 'Error desconocido')
                logger.info(f"   ❌ {dataset_name}: {error}")
        
        logger.info("🎉 Actualización completada exitosamente")
        return True
        
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout en la actualización (más de 5 minutos)")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Error de conexión con el backend")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        return False

def main():
    """Función principal del script"""
    try:
        # Verificar que el backend esté disponible
        try:
            response = requests.get(f"{BACKEND_URL}/api/datasets", timeout=10)
            if response.status_code != 200:
                logger.error("❌ Backend no disponible")
                sys.exit(1)
        except Exception as e:
            logger.error(f"❌ No se puede conectar al backend: {e}")
            sys.exit(1)
        
        # Ejecutar actualización
        success = update_datasets()
        
        if success:
            logger.info("✅ Script completado exitosamente")
            sys.exit(0)
        else:
            logger.error("❌ Script completado con errores")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️  Script interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
