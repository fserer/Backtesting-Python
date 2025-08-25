#!/usr/bin/env python3
"""
Script de demostración para mostrar los payloads que se enviarían a la API de Hyperliquid
sin ejecutar órdenes reales. Útil para entender la estructura de las órdenes.
"""

import json
import sys
import os

# Agregar el directorio del SDK al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'hyperliquid-python-sdk'))

from hyperliquid.utils.signing import order_request_to_order_wire, order_wires_to_order_action

def show_demo_payloads():
    """Mostrar ejemplos de payloads para diferentes tipos de órdenes"""
    
    print("🚀 DEMOSTRACIÓN DE PAYLOADS DE HYPERLIQUID")
    print("="*60)
    print("📋 Este script muestra los payloads que se enviarían a la API")
    print("🔒 NO se ejecutan órdenes reales - solo demostración")
    print("="*60)
    
    # Ejemplo 1: Abrir posición LONG en ETH
    print("\n" + "="*60)
    print("📈 EJEMPLO 1: ABRIR POSICIÓN LONG EN ETH")
    print("="*60)
    
    order_request = {
        "coin": "ETH",
        "is_buy": True,  # LONG
        "sz": 0.01,      # 0.01 ETH (float, no string)
        "limit_px": 0.0, # Market price (float, no string)
        "reduce_only": False,
        "order_type": {"limit": {"tif": "Ioc"}}
    }
    
    print("📦 OrderRequest:")
    print(json.dumps(order_request, indent=2))
    
    # Convertir a OrderWire (necesita el ID del activo)
    # ETH tiene ID 1 según la lista de activos
    order_wire = order_request_to_order_wire(order_request, 1)  # ETH = ID 1
    print("\n📦 OrderWire:")
    print(json.dumps(order_wire, indent=2))
    
    # Convertir a OrderAction (payload final)
    order_action = order_wires_to_order_action([order_wire])
    print("\n📦 OrderAction (Payload final):")
    print(json.dumps(order_action, indent=2))
    
    print("\n🔗 URL: https://api.hyperliquid.xyz/exchange")
    print("📋 Método: POST")
    
    # Ejemplo 2: Abrir posición SHORT en BTC
    print("\n" + "="*60)
    print("📉 EJEMPLO 2: ABRIR POSICIÓN SHORT EN BTC")
    print("="*60)
    
    order_request_2 = {
        "coin": "BTC",
        "is_buy": False,  # SHORT
        "sz": 0.001,      # 0.001 BTC (float, no string)
        "limit_px": 0.0,  # Market price (float, no string)
        "reduce_only": False,
        "order_type": {"limit": {"tif": "Ioc"}}
    }
    
    print("📦 OrderRequest:")
    print(json.dumps(order_request_2, indent=2))
    
    # Convertir a OrderWire (necesita el ID del activo)
    # BTC tiene ID 0 según la lista de activos
    order_wire_2 = order_request_to_order_wire(order_request_2, 0)  # BTC = ID 0
    print("\n📦 OrderWire:")
    print(json.dumps(order_wire_2, indent=2))
    
    # Convertir a OrderAction (payload final)
    order_action_2 = order_wires_to_order_action([order_wire_2])
    print("\n📦 OrderAction (Payload final):")
    print(json.dumps(order_action_2, indent=2))
    
    print("\n🔗 URL: https://api.hyperliquid.xyz/exchange")
    print("📋 Método: POST")
    
    # Ejemplo 3: Cerrar posición (reduce_only = True)
    print("\n" + "="*60)
    print("🔒 EJEMPLO 3: CERRAR POSICIÓN (REDUCE_ONLY)")
    print("="*60)
    
    order_request_3 = {
        "coin": "ETH",
        "is_buy": True,   # Comprar para cerrar SHORT
        "sz": 0.01,       # 0.01 ETH (float, no string)
        "limit_px": 0.0,  # Market price (float, no string)
        "reduce_only": True,  # Solo reducir posición
        "order_type": {"limit": {"tif": "Ioc"}}
    }
    
    print("📦 OrderRequest:")
    print(json.dumps(order_request_3, indent=2))
    
    # Convertir a OrderWire (necesita el ID del activo)
    # ETH tiene ID 1 según la lista de activos
    order_wire_3 = order_request_to_order_wire(order_request_3, 1)  # ETH = ID 1
    print("\n📦 OrderWire:")
    print(json.dumps(order_wire_3, indent=2))
    
    # Convertir a OrderAction (payload final)
    order_action_3 = order_wires_to_order_action([order_wire_3])
    print("\n📦 OrderAction (Payload final):")
    print(json.dumps(order_action_3, indent=2))
    
    print("\n🔗 URL: https://api.hyperliquid.xyz/exchange")
    print("📋 Método: POST")
    
    # Ejemplo 4: Orden con precio límite
    print("\n" + "="*60)
    print("💰 EJEMPLO 4: ORDEN CON PRECIO LÍMITE")
    print("="*60)
    
    order_request_4 = {
        "coin": "SOL",
        "is_buy": True,   # LONG
        "sz": 1.0,        # 1 SOL (float, no string)
        "limit_px": 100.50,  # Precio límite (float, no string)
        "reduce_only": False,
        "order_type": {"limit": {"tif": "Gtc"}}  # Good Till Cancel
    }
    
    print("📦 OrderRequest:")
    print(json.dumps(order_request_4, indent=2))
    
    # Convertir a OrderWire (necesita el ID del activo)
    # SOL tiene ID 5 según la lista de activos
    order_wire_4 = order_request_to_order_wire(order_request_4, 5)  # SOL = ID 5
    print("\n📦 OrderWire:")
    print(json.dumps(order_wire_4, indent=2))
    
    # Convertir a OrderAction (payload final)
    order_action_4 = order_wires_to_order_action([order_wire_4])
    print("\n📦 OrderAction (Payload final):")
    print(json.dumps(order_action_4, indent=2))
    
    print("\n🔗 URL: https://api.hyperliquid.xyz/exchange")
    print("📋 Método: POST")
    
    # Explicación de los campos
    print("\n" + "="*60)
    print("📚 EXPLICACIÓN DE LOS CAMPOS")
    print("="*60)
    
    print("""
🔹 OrderRequest (formato Python):
   - coin: Símbolo del activo (ej: "ETH", "BTC")
   - is_buy: True = compra (LONG), False = venta (SHORT)
   - sz: Tamaño de la orden como string
   - limit_px: Precio límite como string ("0" = market)
   - reduce_only: True = solo cerrar, False = abrir/cerrar
   - order_type: Tipo de orden (limit, trigger, etc.)

🔹 OrderWire (formato interno):
   - a: ID del activo (número)
   - b: is_buy (boolean)
   - s: size (string)
   - p: price (string)
   - r: reduce_only (boolean)
   - t: order_type (object)

🔹 OrderAction (payload final):
   - type: "order"
   - orders: Lista de OrderWire
   - grouping: "na" (normal)

🔹 Tipos de orden (tif):
   - "Ioc": Immediate or Cancel
   - "Gtc": Good Till Cancel
   - "Alo": All or Nothing
    """)
    
    print("\n" + "="*60)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("💡 Ahora puedes ver exactamente qué payloads se envían")
    print("🔗 Documentación: https://hyperliquid.gitbook.io/hyperliquid/")
    print("="*60)

def main():
    """Función principal"""
    try:
        show_demo_payloads()
    except Exception as e:
        print(f"❌ Error en la demostración: {e}")
        print("💡 Asegúrate de que el SDK esté disponible en hyperliquid-python-sdk/")

if __name__ == "__main__":
    main() 