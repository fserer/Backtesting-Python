#!/usr/bin/env python3
"""
Actualiza automáticamente todos los datasets desde NodeCharts usando la API del backend.
"""

import sys
import os
import requests
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def get_all_datasets_from_api():
    """Obtiene todos los datasets desde la API del backend"""
    try:
        response = requests.get('http://localhost:8000/api/datasets')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datasets desde la API: {e}")
        return []

def update_dataset_via_api(dataset_id):
    """Actualiza un dataset usando la API del backend"""
    try:
        url = f'http://localhost:8000/api/datasets/{dataset_id}/update'
        response = requests.post(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error actualizando dataset ID {dataset_id}: {e}")
        return None

def main():
    print("🚀 Iniciando actualización automática de todos los datasets...")
    print()
    
    # Obtener todos los datasets desde la API
    all_datasets = get_all_datasets_from_api()
    print(f"📊 Datasets encontrados: {len(all_datasets)}")
    print()
    
    if not all_datasets:
        print("❌ No se encontraron datasets. Verifica que el backend esté corriendo.")
        return
    
    # Actualizar cada dataset
    success_count = 0
    failed_count = 0
    
    for i, dataset in enumerate(all_datasets, 1):
        dataset_name = dataset['name']
        dataset_id = dataset['id']
        print(f"🔄 [{i}/{len(all_datasets)}] Actualizando: {dataset_name} (ID: {dataset_id})")
        
        try:
            # Actualizar usando la API del backend
            result = update_dataset_via_api(dataset_id)
            
            if result and 'rows_added' in result:
                rows_added = result.get('rows_added', 0)
                print(f"  ✅ Actualización exitosa: {rows_added} registros añadidos")
                success_count += 1
            else:
                error_msg = result.get('detail', 'Error desconocido') if result else 'Sin respuesta'
                print(f"  ❌ Error en actualización: {error_msg}")
                failed_count += 1
                
        except Exception as e:
            print(f"  ❌ Error en actualización: {e}")
            failed_count += 1
        
        # Pausa entre actualizaciones para no sobrecargar la API
        if i < len(all_datasets):
            print(f"  ⏳ Esperando 2 segundos...")
            time.sleep(2)
        
        print()
    
    # Resumen final
    print("📋 RESUMEN DE ACTUALIZACIÓN:")
    print("=" * 60)
    print(f"📊 Total: {len(all_datasets)} datasets")
    print(f"✅ Exitosos: {success_count}")
    print(f"❌ Fallidos: {failed_count}")
    
    if len(all_datasets) > 0:
        print(f"📈 Tasa de éxito: {(success_count/len(all_datasets)*100):.1f}%")
    
    print("=" * 60)
    print("🎉 ¡Actualización completada!")

if __name__ == "__main__":
    main()
