#!/usr/bin/env python3
"""
Script detallado para obtener información completa de Hyperliquid
Incluye posiciones, órdenes abiertas, historial de trades y más
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

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
        sys.exit(1)
    
    with open(config_path) as f:
        config = json.load(f)
    
    return config


def setup_connection(config):
    """Configurar la conexión con Hyperliquid"""
    try:
        account: LocalAccount = eth_account.Account.from_key(config["secret_key"])
        address = config["account_address"]
        
        if address == "":
            address = account.address
        
        print(f"🔗 Conectando con cuenta: {address}")
        
        info = Info(constants.MAINNET_API_URL, skip_ws=True)
        exchange = Exchange(account, constants.MAINNET_API_URL, account_address=address)
        
        return address, info, exchange
        
    except Exception as e:
        print(f"❌ Error al configurar la conexión: {e}")
        sys.exit(1)


def display_user_state(info, address):
    """Mostrar estado completo del usuario"""
    try:
        user_state = info.user_state(address)
        
        print("\n" + "="*60)
        print("📊 ESTADO COMPLETO DE LA CUENTA")
        print("="*60)
        
        margin_summary = user_state.get("marginSummary", {})
        account_value = float(margin_summary.get("accountValue", 0))
        total_margin_used = float(margin_summary.get("totalMarginUsed", 0))
        total_raw_usd = float(margin_summary.get("totalRawUsd", 0))
        withdrawable = float(user_state.get("withdrawable", 0))
        
        print(f"💰 Valor de la cuenta: ${account_value:,.2f}")
        print(f"📈 Margen total usado: ${total_margin_used:,.2f}")
        print(f"💵 Total USD: ${total_raw_usd:,.2f}")
        print(f"💸 Fondos retirables: ${withdrawable:,.2f}")
        
        # Calcular colateral libre y ratio de margen
        free_collateral = account_value - total_margin_used
        if free_collateral > 0:
            print(f"✅ Colateral libre: ${free_collateral:,.2f}")
        
        if total_margin_used > 0:
            margin_ratio = (free_collateral / total_margin_used) * 100
            print(f"📊 Ratio de margen: {margin_ratio:.2f}%")
        
        return user_state
        
    except Exception as e:
        print(f"❌ Error al obtener estado del usuario: {e}")
        return None


def display_positions_detailed(user_state):
    """Mostrar posiciones con información detallada"""
    if not user_state:
        return
    
    positions = user_state.get("assetPositions", [])
    
    print("\n" + "="*60)
    print("📈 POSICIONES ABIERTAS (DETALLADO)")
    print("="*60)
    
    if len(positions) == 0:
        print("✅ No hay posiciones abiertas")
        return
    
    total_pnl = 0
    total_position_value = 0
    
    for i, position_data in enumerate(positions, 1):
        position = position_data.get("position", {})
        
        coin = position.get("coin", "N/A")
        entry_px = float(position.get("entryPx", 0))
        position_value = float(position.get("positionValue", 0))
        unrealized_pnl = float(position.get("unrealizedPnl", 0))
        size = float(position.get("szi", 0))  # Cambiado de "size" a "szi"
        liquidation_px = float(position.get("liquidationPx", 0))
        leverage = position.get("leverage", {})
        leverage_value = leverage.get("value", 0)
        
        side = "🟢 LONG" if size > 0 else "🔴 SHORT"
        
        print(f"\n{i}. {coin} {side}")
        print(f"   📊 Tamaño: {abs(size):.6f}")
        print(f"   ⚡ Leverage: {leverage_value}x")
        print(f"   💰 Precio de entrada: ${entry_px:,.2f}")
        print(f"   💵 Valor de posición: ${position_value:,.2f}")
        print(f"   📈 PnL no realizado: ${unrealized_pnl:,.2f}")
        
        if position_value > 0:
            pnl_percentage = (unrealized_pnl / position_value) * 100
            pnl_symbol = "📈" if pnl_percentage >= 0 else "📉"
            print(f"   {pnl_symbol} PnL %: {pnl_percentage:+.2f}%")
        
        if liquidation_px > 0:
            print(f"   ⚠️  Precio de liquidación: ${liquidation_px:,.2f}")
        
        total_pnl += unrealized_pnl
        total_position_value += position_value
    
    print(f"\n📊 RESUMEN DE POSICIONES:")
    print(f"   💵 Valor total de posiciones: ${total_position_value:,.2f}")
    print(f"   📈 PnL total no realizado: ${total_pnl:,.2f}")
    if total_position_value > 0:
        total_pnl_percentage = (total_pnl / total_position_value) * 100
        print(f"   📊 PnL total %: {total_pnl_percentage:+.2f}%")


def display_open_orders(info, address):
    """Mostrar órdenes abiertas"""
    try:
        open_orders = info.open_orders(address)
        
        print("\n" + "="*60)
        print("📋 ÓRDENES ABIERTAS")
        print("="*60)
        
        if not open_orders or len(open_orders) == 0:
            print("✅ No hay órdenes abiertas")
            return
        
        for i, order in enumerate(open_orders, 1):
            coin = order.get("coin", "N/A")
            side = order.get("side", "N/A")
            size = float(order.get("sz", 0))
            price = float(order.get("px", 0))
            order_type = order.get("orderType", "N/A")
            oid = order.get("oid", "N/A")
            
            side_emoji = "🟢" if side == "B" else "🔴"
            side_text = "COMPRA" if side == "B" else "VENTA"
            
            print(f"\n{i}. {coin} {side_emoji} {side_text}")
            print(f"   📊 Tamaño: {size:.6f}")
            print(f"   💰 Precio: ${price:,.2f}")
            print(f"   📋 Tipo: {order_type}")
            print(f"   🆔 ID: {oid}")
            
    except Exception as e:
        print(f"❌ Error al obtener órdenes abiertas: {e}")


def display_recent_trades(info, address):
    """Mostrar trades recientes"""
    try:
        # Obtener trades de las últimas 24 horas
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
        
        fills = info.user_fills(address)
        
        print("\n" + "="*60)
        print("🔄 TRADES RECIENTES (Últimas 24h)")
        print("="*60)
        
        if not fills or len(fills) == 0:
            print("✅ No hay trades en las últimas 24 horas")
            return
        
        total_volume = 0
        total_fees = 0
        
        for i, fill in enumerate(fills[:10], 1):  # Mostrar solo los últimos 10
            coin = fill.get("coin", "N/A")
            side = fill.get("side", "N/A")
            size = float(fill.get("sz", 0))
            price = float(fill.get("px", 0))
            fee = float(fill.get("fee", 0))
            time = int(fill.get("time", 0))
            
            # Convertir timestamp a hora legible
            trade_time = datetime.fromtimestamp(time / 1000).strftime("%H:%M:%S")
            
            side_emoji = "🟢" if side == "B" else "🔴"
            side_text = "COMPRA" if side == "B" else "VENTA"
            
            volume = size * price
            
            print(f"\n{i}. {coin} {side_emoji} {side_text} - {trade_time}")
            print(f"   📊 Tamaño: {size:.6f}")
            print(f"   💰 Precio: ${price:,.2f}")
            print(f"   💵 Volumen: ${volume:,.2f}")
            print(f"   💸 Fee: ${fee:,.4f}")
            
            total_volume += volume
            total_fees += fee
        
        print(f"\n📊 RESUMEN DE TRADES:")
        print(f"   💵 Volumen total: ${total_volume:,.2f}")
        print(f"   💸 Fees totales: ${total_fees:,.4f}")
        
    except Exception as e:
        print(f"❌ Error al obtener trades recientes: {e}")


def display_spot_balances_detailed(info, address):
    """Mostrar balances spot detallados"""
    try:
        spot_user_state = info.spot_user_state(address)
        balances = spot_user_state.get("balances", [])
        
        print("\n" + "="*60)
        print("💎 BALANCES SPOT (DETALLADO)")
        print("="*60)
        
        if len(balances) == 0:
            print("✅ No hay balances spot disponibles")
            print("   💡 Los balances spot aparecen cuando tienes tokens en el trading spot de Hyperliquid")
            return
        
        total_value = 0
        
        for balance in balances:
            coin = balance.get("coin", "N/A")
            free = float(balance.get("free", 0))
            total = float(balance.get("total", 0))
            locked = total - free
            
            if total > 0:
                print(f"\n   {coin}:")
                print(f"      💰 Total: {total:.6f}")
                print(f"      ✅ Libre: {free:.6f}")
                if locked > 0:
                    print(f"      🔒 Bloqueado: {locked:.6f}")
                
                # Aquí podrías agregar el valor en USD si tienes precios
                # Por ahora solo mostramos las cantidades
        
    except Exception as e:
        print(f"❌ Error al obtener balances spot: {e}")


def main():
    """Función principal"""
    print("🚀 Iniciando consulta detallada de Hyperliquid...")
    
    # Cargar configuración
    config = load_config()
    
    # Configurar conexión
    address, info, exchange = setup_connection(config)
    
    # Obtener y mostrar estado del usuario
    user_state = display_user_state(info, address)
    
    # Mostrar posiciones detalladas
    display_positions_detailed(user_state)
    
    # Mostrar órdenes abiertas
    display_open_orders(info, address)
    
    # Mostrar trades recientes
    display_recent_trades(info, address)
    
    # Mostrar balances spot detallados
    display_spot_balances_detailed(info, address)
    
    print("\n" + "="*60)
    print("✅ Consulta detallada completada")
    print("="*60)


if __name__ == "__main__":
    main() 