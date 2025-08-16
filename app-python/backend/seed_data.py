#!/usr/bin/env python3
"""
Script para cargar datos de ejemplo a Supabase.
Uso: python seed_data.py
"""

import asyncio
import pandas as pd
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.supabase_client import save_ticks, clear_ticks
from services.csv_ingest import process_csv_upload
from fastapi import UploadFile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    """Carga datos de ejemplo desde samples/data.csv a Supabase."""
    try:
        # Ruta al archivo de datos de ejemplo
        sample_file_path = "../samples/data.csv"
        
        if not os.path.exists(sample_file_path):
            logger.error(f"Archivo no encontrado: {sample_file_path}")
            return False
        
        # Leer el archivo CSV
        with open(sample_file_path, 'rb') as f:
            content = f.read()
        
        # Crear objeto UploadFile simulado
        class MockUploadFile:
            def __init__(self, content):
                self.content = content
                self.filename = "data.csv"
            
            async def read(self):
                return self.content
        
        mock_file = MockUploadFile(content)
        
        # Procesar el CSV
        logger.info("Procesando archivo CSV...")
        df, freq_detected, rows_count = await process_csv_upload(mock_file)
        
        # Limpiar datos existentes
        logger.info("Limpiando datos existentes...")
        await clear_ticks()
        
        # Guardar en Supabase
        logger.info(f"Guardando {rows_count} filas en Supabase...")
        success = await save_ticks(df)
        
        if success:
            logger.info(f"✅ Datos cargados exitosamente!")
            logger.info(f"   - Filas: {rows_count}")
            logger.info(f"   - Frecuencia: {freq_detected}")
            return True
        else:
            logger.error("❌ Error al guardar datos en Supabase")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error durante la carga de datos: {str(e)}")
        return False

if __name__ == "__main__":
    print("🌱 Cargando datos de ejemplo a Supabase...")
    print("=" * 50)
    
    success = asyncio.run(seed_data())
    
    if success:
        print("=" * 50)
        print("✅ Datos de ejemplo cargados correctamente!")
        print("   Puedes ahora usar la aplicación para hacer backtests.")
    else:
        print("=" * 50)
        print("❌ Error al cargar datos de ejemplo.")
        print("   Verifica tu configuración de Supabase.")
        sys.exit(1)
