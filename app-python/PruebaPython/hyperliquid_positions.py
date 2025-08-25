#!/usr/bin/env python3
"""
Script para obtener posiciones abiertas en Hyperliquid
Usa el SDK oficial de Hyperliquid para conectarse y mostrar el detalle de posiciones
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


def get_user_state(info, address):
    """Obtener el estado del usuario"""
    try:
        user_state = info.user_state(address)
        return user_state
    except Exception as e:
        print(f"❌ Error al obtener el estado del usuario: {e}")
        return None


def display_positions(user_state):
    """Mostrar las posiciones abiertas de forma detallada"""
    if not user_state:
        print("❌ No se pudo obtener el estado del usuario")
        return
    
    print("\n" + "="*60)
    print("📊 ESTADO DE LA CUENTA")
    print("="*60)
    
    # Mostrar resumen de margen
    margin_summary = user_state.get("marginSummary", {})
    account_value = float(margin_summary.get("accountValue", 0))
    total_margin_used = float(margin_summary.get("totalMarginUsed", 0))
    total_raw_usd = float(margin_summary.get("totalRawUsd", 0))
    withdrawable = float(user_state.get("withdrawable", 0))
    
    print(f"💰 Valor de la cuenta: ${account_value:,.2f}")
    print(f"📈 Margen total usado: ${total_margin_used:,.2f}")
    print(f"💵 Total USD: ${total_raw_usd:,.2f}")
    print(f"💸 Fondos retirables: ${withdrawable:,.2f}")
    
    # Calcular colateral libre
    free_collateral = account_value - total_margin_used
    if free_collateral > 0:
        print(f"✅ Colateral libre: ${free_collateral:,.2f}")
    
    # Mostrar posiciones abiertas
    positions = user_state.get("assetPositions", [])
    
    print("\n" + "="*60)
    print("📈 POSICIONES ABIERTAS")
    print("="*60)
    
    if len(positions) == 0:
        print("✅ No hay posiciones abiertas")
        return
    
    for i, position_data in enumerate(positions, 1):
        position = position_data.get("position", {})
        
        coin = position.get("coin", "N/A")
        entry_px = float(position.get("entryPx", 0))
        position_value = float(position.get("positionValue", 0))
        unrealized_pnl = float(position.get("unrealizedPnl", 0))
        size = float(position.get("szi", 0))  # Cambiado de "size" a "szi"
        leverage = position.get("leverage", {})
        leverage_value = leverage.get("value", 0)
        
        # Determinar si es long o short
        side = "🟢 LONG" if size > 0 else "🔴 SHORT"
        
        print(f"\n{i}. {coin} {side}")
        print(f"   📊 Tamaño: {abs(size):.6f}")
        print(f"   ⚡ Leverage: {leverage_value}x")
        print(f"   💰 Precio de entrada: ${entry_px:,.2f}")
        print(f"   💵 Valor de posición: ${position_value:,.2f}")
        print(f"   📈 PnL no realizado: ${unrealized_pnl:,.2f}")
        
        # Calcular porcentaje de PnL
        if position_value > 0:
            pnl_percentage = (unrealized_pnl / position_value) * 100
            pnl_symbol = "📈" if pnl_percentage >= 0 else "📉"
            print(f"   {pnl_symbol} PnL %: {pnl_percentage:+.2f}%")


def get_spot_balances(info, address):
    """Obtener balances spot"""
    try:
        spot_user_state = info.spot_user_state(address)
        return spot_user_state
    except Exception as e:
        print(f"❌ Error al obtener balances spot: {e}")
        return None


def display_spot_balances(spot_user_state):
    """Mostrar balances spot"""
    if not spot_user_state:
        return
    
    balances = spot_user_state.get("balances", [])
    
    print("\n" + "="*60)
    print("💎 BALANCES SPOT")
    print("="*60)
    
    if len(balances) == 0:
        print("✅ No hay balances spot disponibles")
        print("   💡 Los balances spot aparecen cuando tienes tokens en el trading spot de Hyperliquid")
        return
    
    for balance in balances:
        coin = balance.get("coin", "N/A")
        free = float(balance.get("free", 0))
        total = float(balance.get("total", 0))
        
        if total > 0:
            print(f"   {coin}: {total:.6f} (libre: {free:.6f})")


def main():
    """Función principal"""
    print("🚀 Iniciando consulta de posiciones en Hyperliquid...")
    
    # Cargar configuración
    config = load_config()
    
    # Configurar conexión
    address, info, exchange = setup_connection(config)
    
    # Obtener estado del usuario
    user_state = get_user_state(info, address)
    
    # Mostrar posiciones
    display_positions(user_state)
    
    # Obtener y mostrar balances spot
    spot_user_state = get_spot_balances(info, address)
    display_spot_balances(spot_user_state)
    
    print("\n" + "="*60)
    print("✅ Consulta completada")
    print("="*60)


if __name__ == "__main__":
    main() 