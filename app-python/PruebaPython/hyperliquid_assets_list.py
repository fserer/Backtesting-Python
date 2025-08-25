#!/usr/bin/env python3
"""
Script para obtener la lista completa de activos disponibles en Hyperliquid
con sus IDs para uso en órdenes API independientemente del lenguaje.
"""

import requests
import json
from typing import List, Dict

def get_hyperliquid_assets() -> List[Dict]:
    """
    Obtiene la lista completa de activos disponibles en Hyperliquid
    desde la API pública de información.
    """
    try:
        # URL de la API de información de Hyperliquid
        url = "https://api.hyperliquid.xyz/info"
        
        # Payload para obtener la información de todos los activos
        payload = {
            "type": "meta"
        }
        
        print("🔗 Conectando a la API de Hyperliquid...")
        
        # Realizar la petición POST
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"🔍 Respuesta de la API recibida. Estructura: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
        
        # Verificar diferentes estructuras posibles de respuesta
        if "data" in data:
            if "universe" in data["data"]:
                return data["data"]["universe"]
            elif "meta" in data["data"]:
                return data["data"]["meta"].get("universe", [])
        
        # Si no encontramos la estructura esperada, mostrar la respuesta completa
        print(f"📋 Respuesta completa de la API:")
        print(json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data)) > 1000 else json.dumps(data, indent=2))
        
        # Intentar extraer universe de diferentes ubicaciones
        if "universe" in data:
            return data["universe"]
        elif "meta" in data and "universe" in data["meta"]:
            return data["meta"]["universe"]
        
        raise Exception("No se pudo encontrar la lista de activos en la respuesta")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []
    except Exception as e:
        print(f"❌ Error al obtener activos: {e}")
        return []

def display_assets_table(assets: List[Dict]):
    """
    Muestra la tabla de activos en formato legible
    """
    if not assets:
        print("❌ No se pudieron obtener los activos")
        return
    
    print("\n" + "="*80)
    print("🪙 LISTA COMPLETA DE ACTIVOS EN HYPERLIQUID")
    print("="*80)
    print(f"📊 Total de activos disponibles: {len(assets)}")
    print("="*80)
    
    # Encabezados de la tabla
    print(f"{'ID':<4} {'Símbolo':<12} {'Nombre':<20} {'Tipo':<8} {'Estado':<10}")
    print("-" * 80)
    
    # Mostrar cada activo
    for i, asset in enumerate(assets):
        # Intentar diferentes campos posibles para el ID
        asset_id = asset.get("asset", asset.get("id", i))
        symbol = asset.get("name", asset.get("symbol", "N/A"))
        display_name = asset.get("displayName", asset.get("display_name", symbol))
        asset_type = asset.get("type", "PERP")
        status = "ACTIVO" if asset.get("enabled", asset.get("active", True)) else "INACTIVO"
        
        print(f"{asset_id:<4} {symbol:<12} {display_name:<20} {asset_type:<8} {status:<10}")
    
    print("-" * 80)

def export_assets_json(assets: List[Dict], filename: str = "hyperliquid_assets.json"):
    """
    Exporta la lista de activos a un archivo JSON
    """
    try:
        # Crear estructura más útil para programación
        assets_data = {
            "metadata": {
                "total_assets": len(assets),
                "export_date": "2024-12-19",
                "source": "Hyperliquid API",
                "description": "Lista completa de activos disponibles en Hyperliquid para uso en órdenes API"
            },
            "assets": []
        }
        
        for i, asset in enumerate(assets):
            asset_data = {
                "id": asset.get("asset", asset.get("id", i)),
                "symbol": asset.get("name", asset.get("symbol", "")),
                "display_name": asset.get("displayName", asset.get("display_name", "")),
                "type": asset.get("type", "PERP"),
                "enabled": asset.get("enabled", asset.get("active", True)),
                "status": "ACTIVE" if asset.get("enabled", asset.get("active", True)) else "INACTIVE",
                "raw_data": asset  # Incluir datos originales para referencia
            }
            assets_data["assets"].append(asset_data)
        
        # Guardar en archivo JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(assets_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Lista exportada a: {filename}")
        print(f"📊 Total de activos exportados: {len(assets)}")
        
    except Exception as e:
        print(f"❌ Error al exportar JSON: {e}")

def export_assets_csv(assets: List[Dict], filename: str = "hyperliquid_assets.csv"):
    """
    Exporta la lista de activos a un archivo CSV
    """
    try:
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escribir encabezados
            writer.writerow(['ID', 'Symbol', 'DisplayName', 'Type', 'Status', 'Enabled'])
            
            # Escribir datos
            for i, asset in enumerate(assets):
                asset_id = asset.get("asset", asset.get("id", i))
                symbol = asset.get("name", asset.get("symbol", ""))
                display_name = asset.get("displayName", asset.get("display_name", ""))
                asset_type = asset.get("type", "PERP")
                enabled = asset.get("enabled", asset.get("active", True))
                status = "ACTIVE" if enabled else "INACTIVE"
                
                writer.writerow([asset_id, symbol, display_name, asset_type, status, enabled])
        
        print(f"💾 Lista exportada a: {filename}")
        
    except Exception as e:
        print(f"❌ Error al exportar CSV: {e}")

def show_api_usage_examples(assets: List[Dict]):
    """
    Muestra ejemplos de cómo usar los IDs en diferentes APIs
    """
    if not assets:
        return
    
    # Tomar algunos ejemplos
    examples = assets[:5]  # Primeros 5 activos como ejemplo
    
    print("\n" + "="*80)
    print("📚 EJEMPLOS DE USO EN DIFERENTES APIs")
    print("="*80)
    
    print("\n🔹 Ejemplo 1: Orden de mercado (Market Order)")
    print("POST https://api.hyperliquid.xyz/exchange")
    print("Payload:")
    example_asset = examples[0]
    example_payload = {
        "type": "order",
        "orders": [{
            "a": example_asset.get("asset", example_asset.get("id", 0)),  # ID del activo
            "b": True,  # is_buy
            "p": "0",   # limit_px (0 para market)
            "s": "0.01", # size
            "r": False, # reduce_only
            "t": {      # order_type
                "limit": {
                    "tif": "Ioc"  # Immediate or Cancel
                }
            }
        }],
        "grouping": "na"
    }
    print(json.dumps(example_payload, indent=2))
    
    print(f"\n🔹 Ejemplo 2: Consulta de información del activo")
    print("POST https://api.hyperliquid.xyz/info")
    print("Payload:")
    info_payload = {
        "type": "l2Book",
        "coin": example_asset.get("name", example_asset.get("symbol", "BTC"))  # Símbolo del activo
    }
    print(json.dumps(info_payload, indent=2))
    
    print(f"\n🔹 Ejemplo 3: Consulta de posiciones del usuario")
    print("POST https://api.hyperliquid.xyz/info")
    print("Payload:")
    user_state_payload = {
        "type": "clearinghouseState",
        "user": "0xTuDireccionAqui"
    }
    print(json.dumps(user_state_payload, indent=2))

def main():
    """
    Función principal del script
    """
    print("🚀 Obteniendo lista de activos de Hyperliquid...")
    print("📊 Esto puede tomar unos segundos...")
    
    # Obtener activos
    assets = get_hyperliquid_assets()
    
    if not assets:
        print("❌ No se pudieron obtener los activos. Verifica tu conexión a internet.")
        return
    
    # Mostrar tabla
    display_assets_table(assets)
    
    # Exportar a JSON
    export_assets_json(assets)
    
    # Exportar a CSV
    export_assets_csv(assets)
    
    # Mostrar ejemplos de uso
    show_api_usage_examples(assets)
    
    print("\n" + "="*80)
    print("✅ Lista de activos obtenida exitosamente")
    print("💡 Usa los archivos JSON/CSV generados para integrar en tu aplicación")
    print("🔗 Documentación oficial: https://hyperliquid.gitbook.io/hyperliquid/")
    print("="*80)

if __name__ == "__main__":
    main() 