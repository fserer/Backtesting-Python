import logging
from typing import Dict, Any, Optional, List
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import asyncio

logger = logging.getLogger(__name__)

class HyperliquidTradingService:
    def __init__(self):
        self.info_client = None
        self.exchange_client = None
        self.is_connected = False
    
    def connect(self, account_address: str, secret_key: str):
        """Conecta con Hyperliquid usando las credenciales del usuario"""
        try:
            # Configurar cliente de información (solo para lectura de datos)
            self.info_client = Info(constants.MAINNET_API_URL)
            
            # Guardar las credenciales para uso futuro
            self.account_address = account_address
            self.secret_key = secret_key
            
            self.is_connected = True
            logger.info(f"Conectado a Hyperliquid con cuenta: {account_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a Hyperliquid: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Desconecta de Hyperliquid"""
        self.info_client = None
        self.exchange_client = None
        self.account_address = None
        self.secret_key = None
        self.is_connected = False
        logger.info("Desconectado de Hyperliquid")
    
    def get_user_state(self, account_address: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado del usuario en Hyperliquid"""
        try:
            if not self.info_client:
                return None
            
            user_state = self.info_client.user_state(account_address)
            return user_state
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del usuario: {e}")
            return None
    
    def get_positions(self, account_address: str) -> List[Dict[str, Any]]:
        """Obtiene las posiciones abiertas del usuario"""
        try:
            if not self.info_client:
                return []
            
            user_state = self.get_user_state(account_address)
            if not user_state:
                return []
            
            positions = []
            if 'assetPositions' in user_state:
                for pos in user_state['assetPositions']:
                    if pos.get('position', 0) != 0:  # Solo posiciones no vacías
                        positions.append({
                            'coin': pos.get('coin', 'UNKNOWN'),
                            'size': float(pos.get('position', 0)),
                            'entryPx': float(pos.get('entryPx', 0)),
                            'unrealizedPnl': float(pos.get('unrealizedPnl', 0)),
                            'liquidationPx': float(pos.get('liquidationPx', 0)),
                            'side': 'long' if float(pos.get('position', 0)) > 0 else 'short'
                        })
            
            return positions
            
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []
    
    def get_balances(self, account_address: str) -> List[Dict[str, Any]]:
        """Obtiene los balances de monedas del usuario"""
        try:
            if not self.info_client:
                return []
            
            user_state = self.get_user_state(account_address)
            if not user_state:
                return []
            
            balances = []
            if 'marginSummary' in user_state:
                margin_summary = user_state['marginSummary']
                balances.append({
                    'coin': 'USD',
                    'free': float(margin_summary.get('freeCollateral', 0)),
                    'total': float(margin_summary.get('accountValue', 0)),
                    'usdValue': float(margin_summary.get('accountValue', 0))
                })
            
            return balances
            
        except Exception as e:
            logger.error(f"Error obteniendo balances: {e}")
            return []
    
    def get_open_orders(self, account_address: str) -> List[Dict[str, Any]]:
        """Obtiene las órdenes abiertas del usuario"""
        try:
            if not self.info_client:
                return []
            
            open_orders = self.info_client.open_orders(account_address)
            if not open_orders:
                return []
            
            orders = []
            for order in open_orders:
                orders.append({
                    'id': str(order.get('oid', '')),
                    'coin': order.get('coin', 'UNKNOWN'),
                    'side': 'buy' if order.get('isBuy', False) else 'sell',
                    'size': float(order.get('sz', 0)),
                    'price': float(order.get('limitPx', 0)),
                    'orderType': 'LIMIT' if float(order.get('limitPx', 0)) > 0 else 'MARKET',
                    'status': 'pending',
                    'timestamp': int(order.get('time', 0)),
                    'date': self._format_timestamp(int(order.get('time', 0))),
                    'time': self._format_time(int(order.get('time', 0)))
                })
            
            return orders
            
        except Exception as e:
            logger.error(f"Error obteniendo órdenes abiertas: {e}")
            return []
    
    def get_trade_history(self, account_address: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtiene el historial de trades del usuario"""
        try:
            if not self.info_client:
                return []
            
            user_fills = self.info_client.user_fills(account_address)
            if not user_fills:
                return []
            
            trades = []
            for fill in user_fills[:limit]:
                size = abs(float(fill.get('sz', 0)))
                price = float(fill.get('px', 0))
                volume = size * price
                fee = float(fill.get('fee', 0))
                
                trades.append({
                    'id': str(fill.get('id', '')),
                    'coin': fill.get('coin', 'UNKNOWN'),
                    'side': 'buy' if fill.get('side') == 'B' else 'sell',
                    'size': size,
                    'price': price,
                    'volume': volume,
                    'fee': fee,
                    'feePercentage': (fee / volume * 100) if volume > 0 else 0,
                    'orderType': 'maker' if (fee / volume * 100) <= 0.015 else 'taker',
                    'timestamp': int(fill.get('time', 0)),
                    'date': self._format_timestamp(int(fill.get('time', 0))),
                    'time': self._format_time(int(fill.get('time', 0)))
                })
            
            return trades
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de trades: {e}")
            return []
    
    def place_order(self, coin: str, side: str, size: float, order_type: str = 'MARKET', limit_price: float = 0) -> Dict[str, Any]:
        """Coloca una orden en Hyperliquid"""
        try:
            if not self.exchange_client:
                return {'success': False, 'error': 'No conectado a Hyperliquid'}
            
            # Obtener el índice del asset
            meta = self.info_client.meta()
            asset_index = None
            for i, asset in enumerate(meta['universe']):
                if asset['name'].upper() == coin.upper():
                    asset_index = i
                    break
            
            if asset_index is None:
                return {'success': False, 'error': f'Asset {coin} no encontrado'}
            
            # Preparar la orden
            is_buy = side.lower() == 'buy'
            
            if order_type == 'MARKET':
                # Para órdenes de mercado, usar precio 0
                order_price = 0
            else:
                order_price = limit_price
            
            order = {
                'a': asset_index,
                'b': is_buy,
                'p': str(order_price),
                's': str(size),
                'r': False,  # reduceOnly
                't': {
                    'limit': {
                        'tif': 'Ioc' if order_type == 'MARKET' else 'Gtc'
                    }
                }
            }
            
            # Enviar la orden
            result = self.exchange_client.order(order)
            
            if result and result.get('status') == 'ok':
                return {'success': True, 'orderId': str(result.get('response', {}).get('data', {}).get('statuses', [{}])[0].get('oid', ''))}
            else:
                return {'success': False, 'error': 'Error al colocar la orden'}
                
        except Exception as e:
            logger.error(f"Error colocando orden: {e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, coin: str, order_id: str) -> Dict[str, Any]:
        """Cancela una orden en Hyperliquid"""
        try:
            if not self.exchange_client:
                return {'success': False, 'error': 'No conectado a Hyperliquid'}
            
            # Obtener el índice del asset
            meta = self.info_client.meta()
            asset_index = None
            for i, asset in enumerate(meta['universe']):
                if asset['name'].upper() == coin.upper():
                    asset_index = i
                    break
            
            if asset_index is None:
                return {'success': False, 'error': f'Asset {coin} no encontrado'}
            
            # Preparar la cancelación
            cancel = {
                'a': asset_index,
                'o': int(order_id)
            }
            
            # Enviar la cancelación
            result = self.exchange_client.cancel(cancel)
            
            if result and result.get('status') == 'ok':
                return {'success': True}
            else:
                return {'success': False, 'error': 'Error al cancelar la orden'}
                
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_timestamp(self, timestamp: int) -> str:
        """Formatea un timestamp a fecha"""
        try:
            from datetime import datetime
            return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
        except:
            return ''
    
    def _format_time(self, timestamp: int) -> str:
        """Formatea un timestamp a hora"""
        try:
            from datetime import datetime
            return datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M:%S')
        except:
            return ''

# Instancia global del servicio
hyperliquid_trading_service = HyperliquidTradingService()
