"""
Servicio para manejar estrategias de backtesting guardadas.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class StrategiesService:
    def __init__(self, db_path: str = "data/backtesting.db"):
        self.db_path = db_path
        self._init_strategies_table()
    
    def _init_strategies_table(self):
        """Inicializa la tabla de estrategias si no existe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    strategy_type TEXT NOT NULL,
                    configuration TEXT NOT NULL,
                    results TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Tabla de estrategias inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando tabla de estrategias: {e}")
            raise
    
    def save_strategy(self, user_id: int, username: str, strategy_name: str, 
                     strategy_type: str, configuration: Dict[str, Any], 
                     results: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda una nueva estrategia"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convertir configuración y resultados a JSON
            config_json = json.dumps(configuration, ensure_ascii=False)
            results_json = json.dumps(results, ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO strategies (user_id, username, strategy_name, strategy_type, configuration, results)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, strategy_name, strategy_type, config_json, results_json))
            
            strategy_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Estrategia guardada exitosamente: {strategy_name} por {username}")
            return {
                "id": strategy_id,
                "user_id": user_id,
                "username": username,
                "strategy_name": strategy_name,
                "strategy_type": strategy_type,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error guardando estrategia: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Obtiene todas las estrategias de todos los usuarios"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, username, strategy_name, strategy_type, 
                       configuration, results, created_at
                FROM strategies 
                ORDER BY created_at DESC
            """)
            
            strategies = []
            for row in cursor.fetchall():
                strategy_id, user_id, username, strategy_name, strategy_type, \
                config_json, results_json, created_at = row
                
                # Parsear JSON
                try:
                    configuration = json.loads(config_json)
                    results = json.loads(results_json)
                except json.JSONDecodeError:
                    logger.error(f"Error parseando JSON para estrategia {strategy_id}")
                    continue
                
                # Extraer métricas clave de los resultados
                trades = results.get('trades', [])
                num_trades = len(trades)
                
                # Calcular P&L total
                total_pnl = sum(trade.get('pnl', 0) for trade in trades)
                
                # Calcular costes (comisiones + funding)
                total_fees = results.get('total_fees', 0)
                funding_cost = results.get('funding_cost', {}).get('totalFundingCost', 0)
                total_costs = total_fees + funding_cost
                
                # P&L Neto
                net_pnl = total_pnl - total_costs
                
                strategies.append({
                    "id": strategy_id,
                    "user_id": user_id,
                    "username": username,
                    "strategy_name": strategy_name,
                    "strategy_type": strategy_type,
                    "configuration": configuration,
                    "results": results,
                    "created_at": created_at,
                    "num_trades": num_trades,
                    "total_pnl": total_pnl,
                    "total_costs": total_costs,
                    "net_pnl": net_pnl
                })
            
            conn.close()
            return strategies
            
        except Exception as e:
            logger.error(f"Error obteniendo estrategias: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    def get_strategy_by_id(self, strategy_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una estrategia específica por ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, username, strategy_name, strategy_type, 
                       configuration, results, created_at
                FROM strategies 
                WHERE id = ?
            """, (strategy_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            strategy_id, user_id, username, strategy_name, strategy_type, \
            config_json, results_json, created_at = row
            
            # Parsear JSON
            try:
                configuration = json.loads(config_json)
                results = json.loads(results_json)
            except json.JSONDecodeError:
                logger.error(f"Error parseando JSON para estrategia {strategy_id}")
                return None
            
            return {
                "id": strategy_id,
                "user_id": user_id,
                "username": username,
                "strategy_name": strategy_name,
                "strategy_type": strategy_type,
                "configuration": configuration,
                "results": results,
                "created_at": created_at
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estrategia {strategy_id}: {e}")
            return None
    
    def get_strategies_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las estrategias de un usuario específico"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, username, strategy_name, strategy_type, 
                       configuration, results, created_at
                FROM strategies 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            strategies = []
            for row in cursor.fetchall():
                strategy_id, user_id, username, strategy_name, strategy_type, \
                config_json, results_json, created_at = row
                
                # Parsear JSON
                try:
                    configuration = json.loads(config_json)
                    results = json.loads(results_json)
                except json.JSONDecodeError:
                    logger.error(f"Error parseando JSON para estrategia {strategy_id}")
                    continue
                
                strategies.append({
                    "id": strategy_id,
                    "user_id": user_id,
                    "username": username,
                    "strategy_name": strategy_name,
                    "strategy_type": strategy_type,
                    "configuration": configuration,
                    "results": results,
                    "created_at": created_at
                })
            
            conn.close()
            return strategies
            
        except Exception as e:
            logger.error(f"Error obteniendo estrategias del usuario {user_id}: {e}")
            return []
    
    def delete_strategy(self, strategy_id: int, user_id: int) -> bool:
        """Elimina una estrategia (solo el propietario puede eliminarla)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar que la estrategia pertenece al usuario
            cursor.execute("""
                SELECT id FROM strategies 
                WHERE id = ? AND user_id = ?
            """, (strategy_id, user_id))
            
            if not cursor.fetchone():
                conn.close()
                return False
            
            # Eliminar la estrategia
            cursor.execute("DELETE FROM strategies WHERE id = ?", (strategy_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Estrategia {strategy_id} eliminada por usuario {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando estrategia {strategy_id}: {e}")
            return False
