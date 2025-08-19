#!/usr/bin/env python3
"""
Script de prueba para actualizar el dataset SOPR CP - HOUR desde NodeCharts.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.nodecharts_service import NodeChartsService
from services.sqlite_client import get_dataset_by_name, get_last_tick

def main():
    # API key de NodeCharts
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdG9yZSI6MCwidXNlcmlkIjoyNTUyLCJjcmVhdGlvbnRpbWUiOjE3MTM3Nzc0NTJ9.bFd4Y_134nmvUjboy8CZRkMRc8WngTA9_zDx18qAkXE"
    
    # Inicializar servicio
    service = NodeChartsService(api_key)
    
    dataset_name = "SOPR CP - HOUR"
    
    print(f"🔍 Probando actualización del dataset: {dataset_name}")
    print()
    
    # Buscar información de la métrica
    print("🔍 Buscando información de la métrica...")
    metric_info = service.find_metric_info(dataset_name)
    
    if not metric_info:
        print("❌ No se pudo encontrar la información de la métrica")
        return
    
    print("✅ Información de métrica encontrada:")
    print(f"  - ID: {metric_info['id']}")
    print(f"  - Endpoint: {metric_info['endpoint']}")
    print(f"  - Intervalo: {metric_info['interval']}")
    print()
    
    # Verificar si el dataset existe en nuestra base de datos
    print("🔍 Verificando dataset en base de datos...")
    dataset = get_dataset_by_name(dataset_name)
    
    if not dataset:
        print(f"❌ Dataset '{dataset_name}' no encontrado en la base de datos")
        print("💡 Asegúrate de que el dataset existe antes de actualizarlo")
        return
    
    print(f"✅ Dataset encontrado: {dataset['name']} (ID: {dataset['id']})")
    print()
    
    # Obtener último tick disponible
    print("🔍 Obteniendo último tick disponible...")
    last_tick = get_last_tick(dataset['id'])
    
    if not last_tick:
        print("❌ No hay ticks disponibles para este dataset")
        return
    
    print(f"✅ Último tick: {last_tick['t']} (v: {last_tick['v']})")
    print()
    
    # Probar obtención de datos nuevos
    print("🔍 Probando obtención de datos nuevos...")
    from_timestamp = last_tick['t']
    
    new_data = service.get_metric_data(
        metric_info['endpoint'], 
        from_timestamp, 
        metric_info['interval']
    )
    
    if new_data is None:
        print("❌ No se pudieron obtener datos nuevos")
        return
    
    if new_data.empty:
        print("✅ No hay datos nuevos disponibles")
    else:
        print(f"✅ Datos nuevos obtenidos: {len(new_data)} registros")
        print("📊 Primeros registros:")
        print(new_data.head())
        print()
        print("📊 Últimos registros:")
        print(new_data.tail())

if __name__ == "__main__":
    main()
