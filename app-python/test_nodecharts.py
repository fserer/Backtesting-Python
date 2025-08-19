#!/usr/bin/env python3
"""
Script de prueba para encontrar el ID de métricas en NodeCharts.
"""

import sys
import os
import json
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
    
    # Buscar familia SOPR y mostrar sus detalles completos
    sopr_family = None
    for fam in families:
        name = (fam.get('name') or '').lower()
        if name == 'sopr':
            sopr_family = fam
            break
    
    if sopr_family:
        print("📂 Familia SOPR encontrada. Claves disponibles:", list(sopr_family.keys()))
        # Mostrar JSON completo para inspeccionar estructura
        print(json.dumps(sopr_family, ensure_ascii=False, indent=2))
    else:
        print("❌ No se encontró la familia SOPR exacta")
    
    print()
    print("🔍 Explorando métricas dentro de la familia SOPR (ID: 121)...")
    
    # Obtener métricas de la familia SOPR
    sopr_metrics = service.get_metrics_in_family("121")
    if not sopr_metrics:
        print("❌ No se pudieron obtener las métricas de la familia SOPR")
    else:
        print(f"✅ Obtenidas {len(sopr_metrics)} métricas de la familia SOPR")
        print()
        
        # Buscar específicamente "SOPR CP"
        print("🔍 Buscando métrica 'SOPR CP'...")
        sopr_cp_found = False
        
        for metric in sopr_metrics:
            if 'name' in metric and 'id' in metric:
                metric_name = metric['name']
                metric_id = metric['id']
                print(f"  📊 {metric_name} (ID: {metric_id})")
                
                # Buscar específicamente "SOPR CP"
                if 'sopr cp' in metric_name.lower():
                    print(f"  🎯 ¡ENCONTRADO! SOPR CP: {metric_name} (ID: {metric_id})")
                    sopr_cp_found = True
        
        if not sopr_cp_found:
            print("❌ No se encontró la métrica 'SOPR CP'")

if __name__ == "__main__":
    main()
