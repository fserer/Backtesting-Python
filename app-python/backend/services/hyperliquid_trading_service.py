import logging
from typing import Dict, Any, Optional, List
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import eth_account
from eth_account.signers.local import LocalAccount
import asyncio
import requests
import json
import concurrent.futures
import time

logger = logging.getLogger(__name__)

class HyperliquidTradingService:
    def __init__(self):
        self.info_client = None
        self.exchange_client = None
        self.is_connected = False
    
    def connect(self, main_wallet_address: str, api_private_key: str):
        """Conecta con Hyperliquid usando main wallet para leer y api private key para operar"""
        try:
            # Configurar cliente de información (solo para lectura de datos)
            self.info_client = Info(constants.MAINNET_API_URL)
            
            # Crear el objeto account usando eth_account para operaciones
            account: LocalAccount = eth_account.Account.from_key(api_private_key)
            
            # Configurar cliente de exchange (para trading)
            self.exchange_client = Exchange(
                account, 
                constants.MAINNET_API_URL
            )
            
            # Guardar las credenciales para uso futuro
            self.account_address = main_wallet_address  # Usar la main wallet para consultas
            self.secret_key = api_private_key
            
            self.is_connected = True
            logger.info(f"Conectado a Hyperliquid - Main wallet para leer: {main_wallet_address}")
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
                logger.error("Info client no está disponible en get_user_state")
                return None
            
            logger.info(f"Obteniendo estado del usuario para: {account_address}")
            # Usar el método correcto del SDK
            user_state = self.info_client.user_state(account_address)
            logger.info(f"Estado del usuario obtenido de la API: {user_state}")
            return user_state
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del usuario: {e}")
            return None
    
    def get_positions(self, account_address: str) -> List[Dict[str, Any]]:
        """Obtiene las posiciones abiertas del usuario"""
        try:
            if not self.info_client:
                logger.error("Info client no está disponible")
                return []
            
            user_state = self.get_user_state(account_address)
            if not user_state:
                logger.error(f"No se pudo obtener el estado del usuario para {account_address}")
                return []
            
            logger.info(f"Estado del usuario obtenido: {user_state}")
            
            positions = []
            if 'assetPositions' in user_state:
                logger.info(f"Asset positions encontradas: {user_state['assetPositions']}")
                for pos in user_state['assetPositions']:
                    # La estructura es: {'type': 'oneWay', 'position': {...}}
                    if 'position' in pos and pos['position']:
                        position_data = pos['position']
                        position_size = float(position_data.get('szi', 0))
                        logger.info(f"Posición {position_data.get('coin', 'UNKNOWN')}: {position_size}")
                        
                        if position_size != 0:  # Solo posiciones no vacías
                            positions.append({
                                'coin': position_data.get('coin', 'UNKNOWN'),
                                'size': position_size,
                                'entryPx': float(position_data.get('entryPx', 0)),
                                'unrealizedPnl': float(position_data.get('unrealizedPnl', 0)),
                                'liquidationPx': float(position_data.get('liquidationPx', 0)) if position_data.get('liquidationPx') else 0,
                                'side': 'long' if position_size > 0 else 'short'
                            })
            else:
                logger.warning("No se encontró 'assetPositions' en el estado del usuario")
            
            logger.info(f"Posiciones procesadas: {positions}")
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
    
    def place_order(self, coin: str, is_buy: bool, sz: float, limit_px: float = None, reduce_only: bool = False, order_type: str = "MARKET") -> Dict[str, Any]:
        """Coloca una orden en Hyperliquid"""
        try:
            logger.info(f"Intentando colocar orden: coin={coin}, is_buy={is_buy}, sz={sz}, limit_px={limit_px}, order_type={order_type}")
            logger.info(f"Estado de conexión: exchange_client={self.exchange_client is not None}, is_connected={self.is_connected}")
            
            if not self.exchange_client:
                logger.error("Exchange client no está disponible")
                return {'success': False, 'error': 'No conectado a Hyperliquid'}
            
            meta = self.info_client.meta()
            asset_index = None
            for i, asset in enumerate(meta['universe']):
                if asset['name'].upper() == coin.upper():
                    asset_index = i
                    break
            
            if asset_index is None:
                return {'success': False, 'error': f'Asset {coin} no encontrado'}
            
            # Determinar el tipo de orden y precio
            if order_type == "LIMIT" and limit_px and limit_px > 0:
                # Orden límite
                logger.info(f"Colocando orden límite: coin={coin}, is_buy={is_buy}, sz={sz}, limit_px={limit_px}")
                
                # Usar el método order del SDK para órdenes límite
                result = self.exchange_client.order(coin, is_buy, sz, limit_px, {"limit": {"tif": "Gtc"}})
                
                logger.info(f"Resultado de order (límite): {result}")
                
                if result and result.get('status') == 'ok':
                    # Extraer información de la respuesta
                    response_data = result.get('response', {}).get('data', {})
                    statuses = response_data.get('statuses', [])
                    
                    # Verificar si hay errores en los statuses
                    for status in statuses:
                        if 'error' in status:
                            error_msg = status['error']
                            logger.error(f"Error en orden límite: {error_msg}")
                            translated_error = self._translate_error(error_msg)
                            return {'success': False, 'error': translated_error}
                    
                    if statuses:
                        # Mostrar detalles de la orden
                        for status in statuses:
                            if 'resting' in status:
                                resting = status['resting']
                                oid = resting.get('oid', 'unknown')
                                logger.info(f"Orden límite #{oid} colocada en el libro de órdenes")
                            elif 'filled' in status:
                                filled = status['filled']
                                oid = filled.get('oid', 'unknown')
                                total_sz = filled.get('totalSz', 0)
                                avg_px = filled.get('avgPx', 0)
                                logger.info(f"Orden límite #{oid} ejecutada: {total_sz} {coin} a ${avg_px}")
                    
                    return {'success': True, 'orderId': 'limit_order_placed'}
                else:
                    logger.error(f"Error en order (límite): {result}")
                    return {'success': False, 'error': f'Limit Order Error: {result}'}
                    
            else:
                # Orden de mercado
                logger.info(f"Colocando orden de mercado: coin={coin}, is_buy={is_buy}, sz={sz}")
                
                # Usar market_open para órdenes de mercado
                result = self.exchange_client.market_open(coin, is_buy, sz, None, 0.01)
                
                logger.info(f"Resultado de market_open: {result}")
                
                if result and result.get('status') == 'ok':
                    # Extraer información de la respuesta
                    response_data = result.get('response', {}).get('data', {})
                    statuses = response_data.get('statuses', [])
                    
                    # Verificar si hay errores en los statuses
                    for status in statuses:
                        if 'error' in status:
                            error_msg = status['error']
                            logger.error(f"Error en orden de mercado: {error_msg}")
                            translated_error = self._translate_error(error_msg)
                            return {'success': False, 'error': translated_error}
                    
                    if statuses:
                        # Mostrar detalles de la orden ejecutada
                        for status in statuses:
                            if 'filled' in status:
                                filled = status['filled']
                                oid = filled.get('oid', 'unknown')
                                total_sz = filled.get('totalSz', 0)
                                avg_px = filled.get('avgPx', 0)
                                logger.info(f"Orden de mercado #{oid} ejecutada: {total_sz} {coin} a ${avg_px}")
                    
                    return {'success': True, 'orderId': 'market_order_placed'}
                else:
                    logger.error(f"Error en market_open: {result}")
                    return {'success': False, 'error': f'Market Order Error: {result}'}
                    
        except Exception as e:
            logger.error(f"Error colocando orden: {e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, coin: str, order_id: str) -> Dict[str, Any]:
        """Cancela una orden en Hyperliquid"""
        try:
            # Verificar que el Exchange client esté disponible
            if not self.exchange_client:
                logger.error("Exchange client no está disponible")
                return {'success': False, 'error': 'No conectado a Hyperliquid'}
            
            logger.info(f"Cancelando orden: coin={coin}, order_id={order_id}")
            
            # Usar el método cancel del SDK con argumentos posicionales correctos
            # Como en hyperliquid_cancel_orders.py: exchange.cancel(coin, oid)
            result = self.exchange_client.cancel(coin, int(order_id))
            
            logger.info(f"Resultado de cancel: {result}")
            
            if result and result.get('status') == 'ok':
                return {'success': True}
            else:
                logger.error(f"Error en cancel: {result}")
                return {'success': False, 'error': f'Cancel Error: {result}'}
                
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

    def _translate_error(self, error_msg: str) -> str:
        """Traduce errores comunes de Hyperliquid a español"""
        error_lower = error_msg.lower()
        
        # Mapeo de errores comunes
        error_translations = {
            'order must have minimum value of $10': 'La orden debe tener un valor mínimo de $10',
            'order has invalid size': 'Tamaño de la posición muy pequeño',
            'insufficient balance': 'Saldo insuficiente',
            'position size too small': 'Tamaño de la posición muy pequeño',
            'invalid leverage': 'Apalancamiento inválido',
            'leverage too high': 'Apalancamiento demasiado alto',
            'leverage too low': 'Apalancamiento demasiado bajo',
            'price out of range': 'Precio fuera de rango',
            'order size too large': 'Tamaño de la orden demasiado grande',
            'market closed': 'Mercado cerrado',
            'trading suspended': 'Trading suspendido',
            'invalid order type': 'Tipo de orden inválido',
            'order not found': 'Orden no encontrada',
            'order already filled': 'Orden ya ejecutada',
            'order already cancelled': 'Orden ya cancelada',
            'rate limit exceeded': 'Límite de velocidad excedido',
            'maintenance mode': 'Modo mantenimiento',
            'invalid asset': 'Activo inválido',
            'asset not found': 'Activo no encontrado',
            'position not found': 'Posición no encontrada',
            'insufficient margin': 'Margen insuficiente',
            'margin call': 'Llamada de margen',
            'liquidation': 'Liquidación',
            'account frozen': 'Cuenta congelada',
            'withdrawal suspended': 'Retiros suspendidos',
            'deposit suspended': 'Depósitos suspendidos',
            'api key invalid': 'Clave API inválida',
            'api key expired': 'Clave API expirada',
            'signature invalid': 'Firma inválida',
            'timestamp expired': 'Timestamp expirado',
            'nonce invalid': 'Nonce inválido',
            'request too large': 'Solicitud demasiado grande',
            'invalid json': 'JSON inválido',
            'missing required field': 'Campo requerido faltante',
            'field validation failed': 'Validación de campo fallida',
            'internal server error': 'Error interno del servidor',
            'service unavailable': 'Servicio no disponible',
            'gateway timeout': 'Timeout del gateway',
            'bad request': 'Solicitud incorrecta',
            'unauthorized': 'No autorizado',
            'forbidden': 'Prohibido',
            'not found': 'No encontrado',
            'method not allowed': 'Método no permitido',
            'conflict': 'Conflicto',
            'too many requests': 'Demasiadas solicitudes',
            'unprocessable entity': 'Entidad no procesable'
        }
        
        # Buscar coincidencias exactas primero
        for english_error, spanish_error in error_translations.items():
            if english_error in error_lower:
                return spanish_error
        
        # Si no hay coincidencia, devolver el error original pero con contexto
        return f"Error de Hyperliquid: {error_msg}"

    def get_all_data_parallel(self, account_address: str) -> Dict[str, Any]:
        """Obtiene todos los datos en paralelo para mayor velocidad"""
        try:
            logger.info(f"Obteniendo todos los datos en paralelo para: {account_address}")
            start_time = time.time()
            
            # Crear un pool de workers para ejecutar las llamadas en paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                # Lanzar todas las llamadas en paralelo
                positions_future = executor.submit(self.get_positions, account_address)
                balances_future = executor.submit(self.get_balances, account_address)
                orders_future = executor.submit(self.get_open_orders, account_address)
                trades_future = executor.submit(self.get_trade_history, account_address, 20)
                
                # Esperar a que todas terminen
                positions = positions_future.result()
                balances = balances_future.result()
                orders = orders_future.result()
                trades = trades_future.result()
            
            end_time = time.time()
            logger.info(f"Datos obtenidos en paralelo en {end_time - start_time:.2f} segundos")
            
            return {
                'positions': positions,
                'balances': balances,
                'orders': orders,
                'trades': trades
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos en paralelo: {e}")
            return {
                'positions': [],
                'balances': [],
                'orders': [],
                'trades': []
            }

# Instancia global del servicio
hyperliquid_trading_service = HyperliquidTradingService()
