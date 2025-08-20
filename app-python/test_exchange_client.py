#!/usr/bin/env python3
"""
Script para probar la inicialización del Exchange client de Hyperliquid
"""

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_exchange_client():
    """Prueba la inicialización del Exchange client"""
    
    # Credenciales de prueba
    main_wallet = "0xFc9f61267Def9B40987F18693f1EbA82C2DdD472"
    api_secret_key = "tu_clave_secreta_aqui"  # Reemplazar con la clave real
    
    print("🧪 Probando inicialización del Exchange client")
    print("-" * 50)
    
    try:
        print("1. Probando Info client...")
        info_client = Info(constants.MAINNET_API_URL)
        print("✅ Info client creado exitosamente")
        
        print("2. Probando Exchange client...")
        print(f"   URL: {constants.MAINNET_API_URL}")
        print(f"   Wallet: {main_wallet}")
        print(f"   Secret Key: {api_secret_key[:10]}...")
        
        # Intentar diferentes formas de inicialización
        try:
            exchange_client = Exchange(
                constants.MAINNET_API_URL,
                main_wallet,
                api_secret_key
            )
            print("✅ Exchange client creado exitosamente")
            
            # Probar obtener meta
            print("3. Probando obtener meta...")
            meta = info_client.meta()
            print(f"✅ Meta obtenida: {len(meta.get('universe', []))} assets")
            
            # Buscar ETH
            eth_index = None
            for i, asset in enumerate(meta['universe']):
                if asset['name'].upper() == 'ETH':
                    eth_index = i
                    break
            
            if eth_index is not None:
                print(f"✅ ETH encontrado en índice: {eth_index}")
                
                # Probar crear una orden (sin enviarla)
                print("4. Probando crear orden (sin enviar)...")
                order = {
                    'a': eth_index,
                    'b': True,  # buy
                    'p': '0',   # market price
                    's': '0.001',  # size
                    'r': False,  # reduce only
                    't': {
                        'limit': {
                            'tif': 'Ioc'
                        }
                    }
                }
                print(f"✅ Orden creada: {order}")
            else:
                print("❌ ETH no encontrado en universe")
                
        except Exception as e:
            print(f"❌ Error creando Exchange client: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            
            # Intentar con diferentes parámetros
            print("5. Probando con diferentes parámetros...")
            try:
                # Intentar sin secret_key
                exchange_client = Exchange(constants.MAINNET_API_URL)
                print("✅ Exchange client creado sin secret_key")
            except Exception as e2:
                print(f"❌ Error sin secret_key: {e2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_exchange_client()
