#!/usr/bin/env python3
"""
Script para cancelar órdenes abiertas en Hyperliquid
Usa el SDK oficial de Hyperliquid para conectarse y cancelar órdenes pendientes
"""

import json
import sys
import os
from pathlib import Path

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import eth_account
from eth_account.signers.local import LocalAccount


def load_config():
    """Cargar configuración desde config.json"""
    config_path = Path(__file__).parent / "config.json"
    
    if not config_path.exists():
        print("❌ Error: No se encontró el archivo config.json")
        print("Por favor, crea el archivo config.json con tu secret_key y account_address")
        sys.exit(1)
    
    with open(config_path) as f:
        config = json.load(f)
    
    return config


def setup_connection(config):
    """Configurar la conexión con Hyperliquid"""
    try:
        # Crear cuenta desde la secret key
        account: LocalAccount = eth_account.Account.from_key(config["secret_key"])
        address = config["account_address"]
        
        if address == "":
            address = account.address
        
        print(f"🔗 Conectando con cuenta: {address}")
        
        # Crear instancia de Info para consultas
        info = Info(constants.MAINNET_API_URL, skip_ws=True)
        
        # Crear instancia de Exchange para operaciones
        exchange = Exchange(account, constants.MAINNET_API_URL, account_address=address)
        
        return address, info, exchange
        
    except Exception as e:
        print(f"❌ Error al configurar la conexión: {e}")
        sys.exit(1)


def get_open_orders(info, address):
    """Obtener órdenes abiertas"""
    try:
        open_orders = info.open_orders(address)
        return open_orders
    except Exception as e:
        print(f"❌ Error al obtener órdenes abiertas: {e}")
        return []


def display_open_orders(open_orders):
    """Mostrar las órdenes abiertas para selección"""
    print("\n" + "="*60)
    print("📋 ÓRDENES ABIERTAS DISPONIBLES")
    print("="*60)
    
    if not open_orders or len(open_orders) == 0:
        print("✅ No hay órdenes abiertas para cancelar")
        return None
    
    print(f"📊 Total de órdenes abiertas: {len(open_orders)}")
    
    orders_list = []
    for i, order in enumerate(open_orders, 1):
        coin = order.get("coin", "N/A")
        side = order.get("side", "N/A")
        size = float(order.get("sz", 0))
        limit_px = float(order.get("limitPx", 0))
        oid = order.get("oid", "N/A")
        timestamp = order.get("timestamp", 0)
        
        # Determinar lado de la orden
        side_emoji = "🟢" if side == "B" else "🔴"
        side_text = "COMPRA" if side == "B" else "VENTA"
        
        print(f"\n{i}. {coin} {side_emoji} {side_text}")
        print(f"   📊 Tamaño: {size:.6f}")
        print(f"   💰 Precio límite: ${limit_px:,.2f}")
        print(f"   🆔 Order ID: {oid}")
        print(f"   ⏰ Timestamp: {timestamp}")
        
        # Guardar la orden para selección
        orders_list.append({
            "index": i,
            "coin": coin,
            "side": side,
            "size": size,
            "limit_px": limit_px,
            "oid": oid,
            "timestamp": timestamp
        })
    
    return orders_list


def show_cancel_payload(coin, oid):
    """Mostrar el payload que se envía para cancelar una orden"""
    payload = {
        "type": "cancel",
        "cancels": [
            {
                "coin": coin,
                "oid": oid
            }
        ]
    }
    
    print("\n" + "="*60)
    print("🔗 PAYLOAD PARA CANCELAR ORDEN")
    print("="*60)
    print("URL: https://api.hyperliquid.xyz/exchange")
    print("Método: POST")
    print("Payload:")
    print(json.dumps(payload, indent=2))
    print("="*60)


def cancel_order(exchange, coin, oid):
    """Cancelar una orden específica"""
    try:
        print(f"\n🔄 Cancelando orden {oid} para {coin}...")
        
        # Cancelar la orden
        result = exchange.cancel(coin, oid)
        
        if result.get("status") == "ok":
            print("✅ Orden cancelada exitosamente")
            return True
        else:
            print(f"❌ Error al cancelar orden: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error al cancelar orden: {e}")
        return False


def select_order_to_cancel(orders_list):
    """Permitir al usuario seleccionar una orden para cancelar"""
    if not orders_list:
        return None
    
    while True:
        try:
            print(f"\n📝 Selecciona el número de orden a cancelar (1-{len(orders_list)}) o 'q' para salir:")
            selection = input("> ").strip()
            
            if selection.lower() == 'q':
                print("❌ Operación cancelada")
                return None
            
            order_index = int(selection)
            if 1 <= order_index <= len(orders_list):
                selected_order = orders_list[order_index - 1]
                return selected_order
            else:
                print(f"❌ Por favor selecciona un número entre 1 y {len(orders_list)}")
                
        except ValueError:
            print("❌ Por favor ingresa un número válido")
        except KeyboardInterrupt:
            print("\n❌ Operación cancelada por el usuario")
            return None


def confirm_cancellation(selected_order):
    """Confirmar la cancelación de la orden"""
    print(f"\n⚠️  ¿Estás seguro de que quieres cancelar esta orden?")
    print(f"   {selected_order['coin']} {'🟢 COMPRA' if selected_order['side'] == 'B' else '🔴 VENTA'}")
    print(f"   📊 Tamaño: {selected_order['size']:.6f}")
    print(f"   💰 Precio: ${selected_order['limit_px']:,.2f}")
    print(f"   🆔 Order ID: {selected_order['oid']}")
    
    confirm = input("\nEscribe 'SI' para confirmar: ").strip()
    return confirm.upper() == "SI"


def main():
    """Función principal"""
    print("🚀 Iniciando script de cancelación de órdenes en Hyperliquid...")
    
    # Cargar configuración
    config = load_config()
    
    # Configurar conexión
    address, info, exchange = setup_connection(config)
    
    # Obtener órdenes abiertas
    open_orders = get_open_orders(info, address)
    
    # Mostrar órdenes disponibles
    orders_list = display_open_orders(open_orders)
    
    if not orders_list:
        print("\n" + "="*60)
        print("✅ No hay órdenes para cancelar")
        print("="*60)
        return
    
    # Seleccionar orden para cancelar
    selected_order = select_order_to_cancel(orders_list)
    
    if not selected_order:
        return
    
    # Confirmar cancelación
    if confirm_cancellation(selected_order):
        # Mostrar payload que se enviará
        show_cancel_payload(selected_order['coin'], selected_order['oid'])
        
        # Cancelar la orden
        success = cancel_order(exchange, selected_order['coin'], selected_order['oid'])
        
        if success:
            print("\n" + "="*60)
            print("✅ Orden cancelada exitosamente")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ Error al cancelar la orden")
            print("="*60)
    else:
        print("\n❌ Cancelación abortada")


if __name__ == "__main__":
    main()


