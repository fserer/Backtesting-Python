#!/usr/bin/env python3
"""
Script para abrir nuevas posiciones en Hyperliquid
"""

import json
import sys
import time
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


def get_available_coins(info):
    """Obtener lista de coins disponibles"""
    try:
        # Obtener información del universo de trading
        meta = info.meta()
        universe = meta.get("universe", [])
        
        available_coins = []
        for asset in universe:
            coin_name = asset.get("name", "")
            if coin_name:
                available_coins.append(coin_name)
        
        return sorted(available_coins)
        
    except Exception as e:
        print(f"❌ Error al obtener coins disponibles: {e}")
        # Lista de coins comunes como fallback
        return ["BTC", "ETH", "SOL", "MATIC", "AVAX", "BNB", "ARB", "OP", "LTC", "DYDX"]


def display_available_coins(coins):
    """Mostrar coins disponibles"""
    print("\n" + "="*60)
    print("🪙 COINS DISPONIBLES PARA TRADING")
    print("="*60)
    
    # Mostrar en columnas para mejor visualización
    cols = 4
    for i in range(0, len(coins), cols):
        row = coins[i:i+cols]
        row_str = "  ".join(f"{j+1+i:2d}. {coin}" for j, coin in enumerate(row))
        print(f"   {row_str}")
    
    return True


def get_user_balance(info, address):
    """Obtener balance del usuario"""
    try:
        user_state = info.user_state(address)
        margin_summary = user_state.get("marginSummary", {})
        account_value = float(margin_summary.get("accountValue", 0))
        withdrawable = float(user_state.get("withdrawable", 0))
        
        return account_value, withdrawable
        
    except Exception as e:
        print(f"❌ Error al obtener balance: {e}")
        return 0, 0


def open_new_position(exchange, coin, is_buy, size, leverage=5):
    """Abrir una nueva posición"""
    try:
        side = "LONG" if is_buy else "SHORT"
        action = "COMPRA" if is_buy else "VENTA"
        
        print(f"\n🚀 Abriendo nueva posición {coin} {side}...")
        print(f"📋 Ejecutando {action} de {size:.6f} {coin} a market price...")
        print(f"⚡ Leverage: {leverage}x")
        
        # Mostrar el payload que se va a enviar
        print("\n" + "="*60)
        print("📤 PAYLOAD QUE SE ENVIARÁ A LA API DE HYPERLIQUID")
        print("="*60)
        
        # Usar la función común para mostrar el payload
        from hyperliquid_utils import show_payload
        show_payload(coin, is_buy, size, reduce_only=False)
        
        # Usar market_open para abrir la posición
        order_result = exchange.market_open(coin, is_buy, size, None, 0.01)
        
        if order_result["status"] == "ok":
            print("✅ Orden ejecutada exitosamente!")
            
            for status in order_result["response"]["data"]["statuses"]:
                try:
                    filled = status["filled"]
                    oid = filled["oid"]
                    total_sz = filled["totalSz"]
                    avg_px = filled["avgPx"]
                    
                    print(f"📊 Orden #{oid} ejecutada:")
                    print(f"   📈 Cantidad: {total_sz} {coin}")
                    print(f"   💰 Precio promedio: ${avg_px}")
                    
                    # Calcular el valor total de la transacción
                    total_value = float(total_sz) * float(avg_px)
                    print(f"   💵 Valor total: ${total_value:,.2f}")
                    
                    # Calcular el margen requerido
                    margin_required = total_value / leverage
                    print(f"   💸 Margen requerido: ${margin_required:,.2f}")
                    
                except KeyError as e:
                    if "error" in status:
                        print(f"❌ Error en la orden: {status['error']}")
                    else:
                        print(f"❌ Error inesperado: {e}")
        else:
            print(f"❌ Error al ejecutar la orden: {order_result}")
            
    except Exception as e:
        print(f"❌ Error al abrir la posición: {e}")


def main():
    """Función principal"""
    print("🚀 Iniciando apertura de nuevas posiciones en Hyperliquid...")
    
    # Cargar configuración
    config = load_config()
    
    # Configurar conexión
    address, info, exchange = setup_connection(config)
    
    # Obtener balance del usuario
    account_value, withdrawable = get_user_balance(info, address)
    
    print(f"\n💰 Balance de la cuenta:")
    print(f"   💵 Valor total: ${account_value:,.2f}")
    print(f"   💸 Fondos retirables: ${withdrawable:,.2f}")
    
    # Obtener coins disponibles
    available_coins = get_available_coins(info)
    
    # Mostrar coins disponibles
    display_available_coins(available_coins)
    
    try:
        # Seleccionar coin
        print(f"\n🔍 Selecciona el coin que quieres operar (1-{len(available_coins)}):")
        coin_choice = int(input("Número de coin: ")) - 1
        
        if coin_choice < 0 or coin_choice >= len(available_coins):
            print("❌ Selección inválida")
            return
        
        selected_coin = available_coins[coin_choice]
        print(f"✅ Coin seleccionado: {selected_coin}")
        
        # Seleccionar dirección (LONG/SHORT)
        print(f"\n📈 ¿Qué tipo de posición quieres abrir?")
        print("   1. 🟢 LONG (Comprar - esperas que suba)")
        print("   2. 🔴 SHORT (Vender - esperas que baje)")
        
        side_choice = input("Selecciona (1 o 2): ")
        
        if side_choice not in ["1", "2"]:
            print("❌ Selección inválida")
            return
        
        is_buy = side_choice == "1"
        side = "LONG" if is_buy else "SHORT"
        action = "COMPRAR" if is_buy else "VENDER"
        
        print(f"✅ Dirección seleccionada: {side}")
        
        # Ingresar tamaño de la posición
        print(f"\n📊 Ingresa el tamaño de la posición en {selected_coin}:")
        print("💡 Ejemplo: 0.01 para 0.01 ETH")
        
        try:
            size = float(input("Tamaño: "))
            
            if size <= 0:
                print("❌ El tamaño debe ser mayor a 0")
                return
            
            # Seleccionar leverage
            print(f"\n⚡ Selecciona el leverage:")
            print("   1. 2x (Más seguro)")
            print("   2. 5x (Estándar)")
            print("   3. 10x (Más riesgo)")
            print("   4. 20x (Alto riesgo)")
            
            leverage_choice = input("Selecciona (1-4): ")
            
            leverage_map = {"1": 2, "2": 5, "3": 10, "4": 20}
            if leverage_choice not in leverage_map:
                print("❌ Selección inválida, usando 5x por defecto")
                leverage = 5
            else:
                leverage = leverage_map[leverage_choice]
            
            print(f"✅ Leverage seleccionado: {leverage}x")
            
            # Confirmar la acción
            print(f"\n⚠️  ¿Estás seguro de que quieres abrir una nueva posición?")
            print(f"   🪙 Coin: {selected_coin}")
            print(f"   📈 Dirección: {side}")
            print(f"   📊 Tamaño: {size:.6f} {selected_coin}")
            print(f"   ⚡ Leverage: {leverage}x")
            print(f"   📋 Acción: {action} a market price")
            
            confirm = input("\nEscribe 'SI' para confirmar: ")
            
            if confirm.upper() == "SI":
                open_new_position(exchange, selected_coin, is_buy, size, leverage)
                
                # Esperar un momento y mostrar el estado actualizado
                print("\n⏳ Esperando 3 segundos para verificar la apertura...")
                time.sleep(3)
                
                # Verificar el estado actualizado
                user_state = info.user_state(address)
                positions = user_state.get("assetPositions", [])
                
                open_positions = []
                for position_data in positions:
                    position = position_data.get("position", {})
                    pos_size = float(position.get("szi", 0))
                    if pos_size != 0:
                        open_positions.append(position)
                
                if len(open_positions) > 0:
                    print("✅ ¡Posición abierta exitosamente!")
                    print(f"📊 Estado actualizado - {len(open_positions)} posiciones activas")
                else:
                    print("❌ Error: No se encontraron posiciones después de la apertura")
                    
            else:
                print("❌ Operación cancelada")
                
        except ValueError:
            print("❌ Por favor ingresa un número válido")
            
    except ValueError:
        print("❌ Por favor ingresa un número válido")
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 