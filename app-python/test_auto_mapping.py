#!/usr/bin/env python3
"""
Prueba el mapeo automático de todos los datasets con NodeCharts.
"""

import sys
import os
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.nodecharts_service import NodeChartsService

def get_all_datasets_from_api():
    """Obtiene todos los datasets desde la API del backend"""
    try:
        response = requests.get('http://localhost:8000/api/datasets')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datasets desde la API: {e}")
        return []

def main():
    # API key de NodeCharts
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdG9yZSI6MCwidXNlcmlkIjoyNTUyLCJjcmVhdGlvbnRpbWUiOjE3MTM3Nzc0NTJ9.bFd4Y_134nmvUjboy8CZRkMRc8WngTA9_zDx18qAkXE"
    
    # Inicializar servicio
    service = NodeChartsService(api_key)
    
    print("🔍 Probando mapeo automático de todos los datasets...")
    print()
    
    # Obtener todos los datasets desde la API
    all_datasets = get_all_datasets_from_api()
    print(f"📊 Datasets encontrados: {len(all_datasets)}")
    print()
    
    if not all_datasets:
        print("❌ No se encontraron datasets. Verifica que el backend esté corriendo.")
        return
    
    # Probar mapeo para cada dataset
    results = {}
    
    for dataset in all_datasets:
        dataset_name = dataset['name']
        print(f"🔍 Procesando: {dataset_name}")
        
        # Intentar encontrar métrica
        metric_info = service.find_metric_info(dataset_name)
        
        if metric_info:
            print(f"  ✅ Mapeado exitoso:")
            print(f"     - Métrica: {metric_info['metric_name']}")
            print(f"     - Endpoint: {metric_info['endpoint']}")
            print(f"     - Intervalo: {metric_info['interval']}")
            print(f"     - Familia: {metric_info['family_name']}")
            results[dataset_name] = {
                'status': 'SUCCESS',
                'metric_info': metric_info
            }
        else:
            print(f"  ❌ No se pudo mapear")
            results[dataset_name] = {
                'status': 'FAILED',
                'error': 'No se encontró métrica correspondiente'
            }
        
        print()
    
    # Resumen final
    print("📋 RESUMEN DE MAPEO:")
    print("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    for dataset_name, result in results.items():
        if result['status'] == 'SUCCESS':
            success_count += 1
            print(f"✅ {dataset_name} -> {result['metric_info']['metric_name']} ({result['metric_info']['endpoint']})")
        else:
            failed_count += 1
            print(f"❌ {dataset_name} -> {result['error']}")
    
    print("=" * 60)
    print(f"📊 Total: {len(results)} datasets")
    print(f"✅ Exitosos: {success_count}")
    print(f"❌ Fallidos: {failed_count}")
    
    if len(results) > 0:
        print(f"📈 Tasa de éxito: {(success_count/len(results)*100):.1f}%")

if __name__ == "__main__":
    main()
