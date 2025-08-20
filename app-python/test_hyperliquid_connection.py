#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a Hyperliquid
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from hyperliquid.info import Info
from hyperliquid.utils import constants
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hyperliquid_connection():
    """Prueba la conexión a Hyperliquid con los datos del usuario"""
    
    # Datos del usuario
    main_wallet = "0xFc9f61267Def9B40987F18693f1EbA82C2DdD472"
    hyperliquid_wallet = "0x16A08e4078604836f8F5eE90638e0F93941C0AcD"
    api_secret_key = "0x05c60a5172000b9d36c674abed74bb49620b3ff8650aeb37891237331f720ec6"
    
    print(f"URL de la API: {constants.MAINNET_API_URL}")
    print(f"Main Wallet: {main_wallet}")
    print(f"Hyperliquid Wallet: {hyperliquid_wallet}")
    print(f"API Secret Key: {api_secret_key[:10]}...")
    print("-" * 50)
    
    try:
        # 1. Probar Info client
        print("1. Probando Info client...")
        info_client = Info(constants.MAINNET_API_URL)
        print("✅ Info client creado exitosamente")
        
        # 2. Probar obtener estado del usuario
        print("2. Probando obtener estado del usuario...")
        user_state = info_client.user_state(main_wallet)
        print(f"✅ Estado del usuario obtenido: {type(user_state)}")
        print(f"   Keys disponibles: {list(user_state.keys()) if user_state else 'None'}")
        
        # 3. Probar obtener posiciones
        print("3. Probando obtener posiciones...")
        if 'assetPositions' in user_state:
            positions = []
            for pos in user_state['assetPositions']:
                if pos.get('position', 0) != 0:
                    positions.append({
                        'coin': pos.get('coin', 'UNKNOWN'),
                        'size': float(pos.get('position', 0)),
                        'entryPx': float(pos.get('entryPx', 0)),
                        'unrealizedPnl': float(pos.get('unrealizedPnl', 0)),
                        'side': 'long' if float(pos.get('position', 0)) > 0 else 'short'
                    })
            print(f"✅ Posiciones obtenidas: {len(positions)} posiciones")
            for pos in positions:
                print(f"   - {pos['coin']}: {pos['size']} ({pos['side']}) - PnL: ${pos['unrealizedPnl']:.2f}")
        else:
            print("❌ No se encontraron posiciones en el estado del usuario")
        
        # 4. Probar obtener balances
        print("4. Probando obtener balances...")
        if 'marginSummary' in user_state:
            margin_summary = user_state['marginSummary']
            print(f"✅ Balance obtenido:")
            print(f"   - Free Collateral: ${float(margin_summary.get('freeCollateral', 0)):.2f}")
            print(f"   - Account Value: ${float(margin_summary.get('accountValue', 0)):.2f}")
        else:
            print("❌ No se encontró información de balance")
        
        # 5. Probar obtener órdenes abiertas (si existe el método)
        print("5. Probando obtener órdenes abiertas...")
        try:
            # Intentar obtener órdenes abiertas
            open_orders = info_client.open_orders(main_wallet)
            print(f"✅ Órdenes abiertas obtenidas: {len(open_orders) if open_orders else 0} órdenes")
        except Exception as e:
            print(f"⚠️  No se pudo obtener órdenes abiertas: {e}")
        
        # 6. Probar obtener historial de trades (si existe el método)
        print("6. Probando obtener historial de trades...")
        try:
            # Intentar obtener historial de trades
            trades = info_client.user_fills(main_wallet)
            print(f"✅ Historial de trades obtenido: {len(trades) if trades else 0} trades")
        except Exception as e:
            print(f"⚠️  No se pudo obtener historial de trades: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Probando conexión a Hyperliquid...")
    success = test_hyperliquid_connection()
    if success:
        print("\n✅ Prueba completada exitosamente")
    else:
        print("\n❌ Prueba falló")
