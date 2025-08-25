#!/usr/bin/env python3
"""
Script para obtener órdenes abiertas en Hyperliquid
Usa el SDK oficial de Hyperliquid para conectarse y mostrar las órdenes pendientes
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


def show_open_orders_payload(address):
    """Mostrar el payload que se envía para obtener órdenes abiertas"""
    payload = {
        "type": "openOrders",
        "user": address
    }
    
    print("\n" + "="*60)
    print("🔗 PAYLOAD PARA OBTENER ÓRDENES ABIERTAS")
    print("="*60)
    print("URL: https://api.hyperliquid.xyz/info")
    print("Método: POST")
    print("Payload:")
    print(json.dumps(payload, indent=2))
    print("="*60)


def show_frontend_open_orders_payload(address):
    """Mostrar el payload que se envía para obtener órdenes abiertas con info frontend"""
    payload = {
        "type": "frontendOpenOrders",
        "user": address
    }
    
    print("\n" + "="*60)
    print("🔗 PAYLOAD PARA OBTENER ÓRDENES ABIERTAS (FRONTEND)")
    print("="*60)
    print("URL: https://api.hyperliquid.xyz/info")
    print("Método: POST")
    print("Payload:")
    print(json.dumps(payload, indent=2))
    print("="*60)


def get_open_orders(info, address):
    """Obtener órdenes abiertas básicas"""
    try:
        open_orders = info.open_orders(address)
        return open_orders
    except Exception as e:
        print(f"❌ Error al obtener órdenes abiertas: {e}")
        return []


def get_frontend_open_orders(info, address):
    """Obtener órdenes abiertas con información frontend"""
    try:
        frontend_orders = info.frontend_open_orders(address)
        return frontend_orders
    except Exception as e:
        print(f"❌ Error al obtener órdenes frontend: {e}")
        return []


def display_open_orders(open_orders):
    """Mostrar las órdenes abiertas básicas"""
    print("\n" + "="*60)
    print("📋 ÓRDENES ABIERTAS (BÁSICAS)")
    print("="*60)
    
    if not open_orders or len(open_orders) == 0:
        print("✅ No hay órdenes abiertas")
        return
    
    print(f"📊 Total de órdenes abiertas: {len(open_orders)}")
    
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


def display_frontend_open_orders(frontend_orders):
    """Mostrar las órdenes abiertas con información frontend"""
    print("\n" + "="*60)
    print("📋 ÓRDENES ABIERTAS (DETALLADAS)")
    print("="*60)
    
    if not frontend_orders or len(frontend_orders) == 0:
        print("✅ No hay órdenes abiertas")
        return
    
    print(f"📊 Total de órdenes abiertas: {len(frontend_orders)}")
    
    for i, order in enumerate(frontend_orders, 1):
        coin = order.get("coin", "N/A")
        side = order.get("side", "N/A")
        size = float(order.get("sz", 0))
        orig_size = float(order.get("origSz", 0))
        limit_px = float(order.get("limitPx", 0))
        oid = order.get("oid", "N/A")
        timestamp = order.get("timestamp", 0)
        order_type = order.get("orderType", "N/A")
        tif = order.get("tif", "N/A")
        reduce_only = order.get("reduceOnly", False)
        is_trigger = order.get("isTrigger", False)
        is_position_tpsl = order.get("isPositionTpsl", False)
        
        # Determinar lado de la orden
        side_emoji = "🟢" if side == "B" else "🔴"
        side_text = "COMPRA" if side == "B" else "VENTA"
        
        print(f"\n{i}. {coin} {side_emoji} {side_text}")
        print(f"   📊 Tamaño actual: {size:.6f}")
        print(f"   📊 Tamaño original: {orig_size:.6f}")
        print(f"   💰 Precio límite: ${limit_px:,.2f}")
        print(f"   🆔 Order ID: {oid}")
        print(f"   📋 Tipo de orden: {order_type}")
        print(f"   ⏰ TIF: {tif}")
        print(f"   🔄 Reduce only: {'Sí' if reduce_only else 'No'}")
        print(f"   🎯 Es trigger: {'Sí' if is_trigger else 'No'}")
        print(f"   📈 Es TP/SL: {'Sí' if is_position_tpsl else 'No'}")
        print(f"   ⏰ Timestamp: {timestamp}")
        
        # Mostrar información de trigger si existe
        if is_trigger:
            trigger_condition = order.get("triggerCondition", "N/A")
            trigger_px = order.get("triggerPx", "N/A")
            print(f"   🎯 Condición trigger: {trigger_condition}")
            print(f"   💰 Precio trigger: {trigger_px}")
        
        # Mostrar children si existen
        children = order.get("children", [])
        if children:
            print(f"   👶 Órdenes hijas: {len(children)}")


def main():
    """Función principal"""
    print("🚀 Iniciando consulta de órdenes abiertas en Hyperliquid...")
    
    # Cargar configuración
    config = load_config()
    
    # Configurar conexión
    address, info, exchange = setup_connection(config)
    
    # Mostrar payloads que se envían a la API
    show_open_orders_payload(address)
    show_frontend_open_orders_payload(address)
    
    # Obtener órdenes abiertas básicas
    open_orders = get_open_orders(info, address)
    
    # Obtener órdenes abiertas con información frontend
    frontend_orders = get_frontend_open_orders(info, address)
    
    # Mostrar órdenes abiertas básicas
    display_open_orders(open_orders)
    
    # Mostrar órdenes abiertas detalladas
    display_frontend_open_orders(frontend_orders)
    
    print("\n" + "="*60)
    print("✅ Consulta de órdenes abiertas completada")
    print("="*60)


if __name__ == "__main__":
    main()


