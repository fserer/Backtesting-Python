#!/usr/bin/env python3
"""
Script simple para encontrar y probar la métrica SOPR CP.
"""

import sys
import os
import json
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.nodecharts_service import NodeChartsService

def main():
    # API key de NodeCharts
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdG9yZSI6MCwidXNlcmlkIjoyNTUyLCJjcmVhdGlvbnRpbWUiOjE3MTM3Nzc0NTJ9.bFd4Y_134nmvUjboy8CZRkMRc8WngTA9_zDx18qAkXE"
    
    # Inicializar servicio
    service = NodeChartsService(api_key)
    
    print("🔍 Buscando families de NodeCharts...")
    
    # Obtener todas las families
    families = service.get_families()
    if not families:
        print("❌ No se pudieron obtener las families")
        return
    
    print(f"✅ Obtenidas {len(families)} families")
    print()
    
    # Buscar familia SOPR
    sopr_family = None
    for fam in families:
        if fam.get('name', '').lower() == 'sopr':
            sopr_family = fam
            break
    
    if not sopr_family:
        print("❌ No se encontró la familia SOPR")
        return
    
    print("📂 Familia SOPR encontrada:")
    print(f"  - ID: {sopr_family['id']}")
    print(f"  - Nombre: {sopr_family['name']}")
    print()
    
    # Buscar métrica "SOPR CP" en los indicators
    if 'indicators' not in sopr_family:
        print("❌ No hay indicators en la familia SOPR")
        return
    
    print("🔍 Buscando métrica 'SOPR CP' en los indicators...")
    sopr_cp_metric = None
    
    for indicator in sopr_family['indicators']:
        name = indicator.get('name', '')
        print(f"  📊 Verificando: {name}")
        
        if name.lower() == 'sopr cp':
            sopr_cp_metric = indicator
            break
    
    if not sopr_cp_metric:
        print("❌ No se encontró la métrica 'SOPR CP'")
        print("📋 Indicators disponibles:")
        for indicator in sopr_family['indicators']:
            print(f"  - {indicator.get('name', 'N/A')} (ID: {indicator.get('id', 'N/A')})")
        return
    
    print("✅ Métrica 'SOPR CP' encontrada:")
    print(f"  - ID: {sopr_cp_metric['id']}")
    print(f"  - Nombre: {sopr_cp_metric['name']}")
    print(f"  - Endpoint: {sopr_cp_metric['endpoint']}")
    print(f"  - Resoluciones: {sopr_cp_metric.get('resolutions', [])}")
    print()
    
    # Probar obtención de datos con diferentes intervalos
    print("🔍 Probando obtención de datos...")
    from_timestamp = "2024-12-01T00:00:00Z"  # Fecha más reciente para prueba
    
    # Probar con "Hour"
    print("📊 Probando con intervalo 'Hour'...")
    new_data_hour = service.get_metric_data(
        sopr_cp_metric['endpoint'],
        from_timestamp,
        "Hour"
    )
    
    if new_data_hour is not None and not new_data_hour.empty:
        print(f"✅ Datos con 'Hour': {len(new_data_hour)} registros")
        print("📊 Primeros registros (Hour):")
        print(new_data_hour.head())
        print()
        
        # Verificar si hay datos de diferentes horas
        if 't' in new_data_hour.columns:
            new_data_hour['t'] = pd.to_datetime(new_data_hour['t'])
            print("📅 Rango de fechas (Hour):")
            print(f"  Desde: {new_data_hour['t'].min()}")
            print(f"  Hasta: {new_data_hour['t'].max()}")
            print(f"  Diferencia: {new_data_hour['t'].max() - new_data_hour['t'].min()}")
    
    print()
    
    # Probar con "hour" (minúscula)
    print("📊 Probando con intervalo 'hour' (minúscula)...")
    new_data_hour_lower = service.get_metric_data(
        sopr_cp_metric['endpoint'],
        from_timestamp,
        "hour"
    )
    
    if new_data_hour_lower is not None and not new_data_hour_lower.empty:
        print(f"✅ Datos con 'hour': {len(new_data_hour_lower)} registros")
        print("📊 Primeros registros (hour):")
        print(new_data_hour_lower.head())
    
    print()
    
    # Probar con "Day" para comparar
    print("📊 Probando con intervalo 'Day' para comparar...")
    new_data_day = service.get_metric_data(
        sopr_cp_metric['endpoint'],
        from_timestamp,
        "Day"
    )
    
    if new_data_day is not None and not new_data_day.empty:
        print(f"✅ Datos con 'Day': {len(new_data_day)} registros")
        print("📊 Primeros registros (Day):")
        print(new_data_day.head())
    
    # Resumen final
    print("📋 Resumen de pruebas:")
    print(f"  - 'Hour': {len(new_data_hour) if new_data_hour is not None and not new_data_hour.empty else 0} registros")
    print(f"  - 'hour': {len(new_data_hour_lower) if new_data_hour_lower is not None and not new_data_hour_lower.empty else 0} registros")
    print(f"  - 'Day': {len(new_data_day) if new_data_day is not None and not new_data_day.empty else 0} registros")

if __name__ == "__main__":
    main()
