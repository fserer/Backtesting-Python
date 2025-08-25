#!/usr/bin/env python3
"""
Script para reducir la exposición de posiciones existentes en Hyperliquid
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


def get_open_positions(info, address):
    """Obtener posiciones abiertas"""
    try:
        user_state = info.user_state(address)
        positions = user_state.get("assetPositions", [])
        
        open_positions = []
        for position_data in positions:
            position = position_data.get("position", {})
            size = float(position.get("szi", 0))
            
            if size != 0:  # Solo posiciones con tamaño diferente de 0
                open_positions.append(position)
        
        return open_positions
        
    except Exception as e:
        print(f"❌ Error al obtener posiciones: {e}")
        return []


def display_positions(positions):
    """Mostrar posiciones disponibles para reducir"""
    if len(positions) == 0:
        print("✅ No hay posiciones abiertas para reducir")
        return False
    
    print("\n" + "="*60)
    print("📈 POSICIONES DISPONIBLES PARA REDUCIR")
    print("="*60)
    
    for i, position in enumerate(positions, 1):
        coin = position.get("coin", "N/A")
        size = float(position.get("szi", 0))
        entry_px = float(position.get("entryPx", 0))
        position_value = float(position.get("positionValue", 0))
        unrealized_pnl = float(position.get("unrealizedPnl", 0))
        leverage = position.get("leverage", {})
        leverage_value = leverage.get("value", 0)
        
        side = "🟢 LONG" if size > 0 else "🔴 SHORT"
        
        print(f"\n{i}. {coin} {side}")
        print(f"   📊 Tamaño actual: {abs(size):.6f}")
        print(f"   ⚡ Leverage: {leverage_value}x")
        print(f"   💰 Precio de entrada: ${entry_px:,.2f}")
        print(f"   💵 Valor de posición: ${position_value:,.2f}")
        print(f"   📈 PnL no realizado: ${unrealized_pnl:,.2f}")
        
        if position_value > 0:
            pnl_percentage = (unrealized_pnl / position_value) * 100
            pnl_symbol = "📈" if pnl_percentage >= 0 else "📉"
            print(f"   {pnl_symbol} PnL %: {pnl_percentage:+.2f}%")
    
    return True


def reduce_position(exchange, coin, current_size, reduce_size):
    """Reducir una posición existente"""
    try:
        print(f"\n🚀 Reduciendo posición {coin} en {reduce_size:.6f}...")
        
        # Para reducir, necesitamos hacer lo opuesto de la posición actual
        # Si es SHORT (size < 0), necesitamos COMPRAR (is_buy = True) para reducir
        # Si es LONG (size > 0), necesitamos VENDER (is_buy = False) para reducir
        is_buy = current_size < 0  # Si size es negativo (SHORT), compramos para reducir
        
        action = "COMPRA" if is_buy else "VENTA"
        print(f"📋 Ejecutando {action} de {reduce_size:.6f} {coin} a market price...")
        
        # Mostrar el payload que se va a enviar
        print("\n" + "="*60)
        print("📤 PAYLOAD QUE SE ENVIARÁ A LA API DE HYPERLIQUID")
        print("="*60)
        
        # Usar la función común para mostrar el payload
        from hyperliquid_utils import show_payload
        show_payload(coin, is_buy, reduce_size, reduce_only=False)
        
        # Usar market_open para reducir la posición
        order_result = exchange.market_open(coin, is_buy, reduce_size, None, 0.01)
        
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
                    
                    # Calcular el nuevo tamaño total
                    new_total_size = abs(current_size) - float(total_sz)
                    print(f"   📊 Nuevo tamaño total: {new_total_size:.6f} {coin}")
                    
                except KeyError as e:
                    if "error" in status:
                        print(f"❌ Error en la orden: {status['error']}")
                    else:
                        print(f"❌ Error inesperado: {e}")
        else:
            print(f"❌ Error al ejecutar la orden: {order_result}")
            
    except Exception as e:
        print(f"❌ Error al reducir la posición: {e}")


def main():
    """Función principal"""
    print("🚀 Iniciando reducción de posiciones en Hyperliquid...")
    
    # Cargar configuración
    config = load_config()
    
    # Configurar conexión
    address, info, exchange = setup_connection(config)
    
    # Obtener posiciones abiertas
    positions = get_open_positions(info, address)
    
    # Mostrar posiciones disponibles
    if not display_positions(positions):
        return
    
    # Preguntar al usuario qué posición reducir
    print(f"\n🔍 Selecciona la posición que quieres reducir (1-{len(positions)}):")
    
    try:
        choice = int(input("Número de posición: ")) - 1
        
        if choice < 0 or choice >= len(positions):
            print("❌ Selección inválida")
            return
        
        selected_position = positions[choice]
        coin = selected_position.get("coin", "N/A")
        current_size = float(selected_position.get("szi", 0))
        
        # Preguntar cuánto reducir
        print(f"\n📊 Posición actual: {abs(current_size):.6f} {coin}")
        print("💡 Ingresa la cantidad que quieres reducir:")
        print("💡 (Para cerrar completamente, ingresa el tamaño actual)")
        
        try:
            reduce_size = float(input("Cantidad a reducir: "))
            
            if reduce_size <= 0:
                print("❌ La cantidad debe ser mayor a 0")
                return
            
            if reduce_size > abs(current_size):
                print("❌ No puedes reducir más del tamaño actual")
                return
            
            # Confirmar la acción
            side = "LONG" if current_size > 0 else "SHORT"
            action = "VENDER" if current_size > 0 else "COMPRAR"
            new_total = abs(current_size) - reduce_size
            
            if new_total == 0:
                print(f"\n⚠️  ¿Estás seguro de que quieres CERRAR COMPLETAMENTE tu posición {coin} {side}?")
                print(f"   📊 Tamaño actual: {abs(current_size):.6f} {coin}")
                print(f"   📋 Acción: {action} todo a market price")
            else:
                print(f"\n⚠️  ¿Estás seguro de que quieres reducir tu posición {coin} {side}?")
                print(f"   📊 Tamaño actual: {abs(current_size):.6f} {coin}")
                print(f"   📉 Reduciendo: {reduce_size:.6f} {coin}")
                print(f"   📊 Nuevo tamaño total: {new_total:.6f} {coin}")
                print(f"   📋 Acción: {action} a market price")
            
            confirm = input("\nEscribe 'SI' para confirmar: ")
            
            if confirm.upper() == "SI":
                reduce_position(exchange, coin, current_size, reduce_size)
                
                # Esperar un momento y mostrar el estado actualizado
                print("\n⏳ Esperando 3 segundos para verificar la reducción...")
                time.sleep(3)
                
                # Verificar el estado actualizado
                updated_positions = get_open_positions(info, address)
                if len(updated_positions) == 0 and new_total == 0:
                    print("✅ ¡Posición cerrada completamente!")
                elif len(updated_positions) > 0:
                    print("✅ ¡Posición reducida exitosamente!")
                    print(f"📊 Estado actualizado - {len(updated_positions)} posiciones activas")
                else:
                    print("❌ Error: No se encontraron posiciones después de la reducción")
                    
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