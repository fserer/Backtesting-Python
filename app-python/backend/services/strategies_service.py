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
                    strategy_type TEXT NOT NULL,
                    configuration TEXT NOT NULL,
                    results TEXT NOT NULL,
                    comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Añadir columna comments si no existe (para compatibilidad con tablas existentes)
            try:
                cursor.execute("ALTER TABLE strategies ADD COLUMN comments TEXT")
                logger.info("Columna comments añadida a la tabla strategies")
            except sqlite3.OperationalError:
                # La columna ya existe
                pass
            
            # Eliminar columna strategy_name si existe (para compatibilidad con tablas existentes)
            try:
                cursor.execute("ALTER TABLE strategies DROP COLUMN strategy_name")
                logger.info("Columna strategy_name eliminada de la tabla strategies")
            except sqlite3.OperationalError:
                # La columna no existe o no se puede eliminar
                pass
            
            conn.commit()
            conn.close()
            logger.info("Tabla de estrategias inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando tabla de estrategias: {e}")
            raise
    
    def save_strategy(self, user_id: int, username: str, strategy_type: str, 
                     configuration: Dict[str, Any], results: Dict[str, Any], 
                     comments: Optional[str] = None, dataset_name: Optional[str] = None) -> Dict[str, Any]:
        """Guarda una nueva estrategia"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Añadir el nombre del dataset a la configuración si se proporciona
            config_with_dataset_name = configuration.copy()
            if dataset_name:
                config_with_dataset_name['dataset_name'] = dataset_name
            
            # Convertir configuración y resultados a JSON
            config_json = json.dumps(config_with_dataset_name, ensure_ascii=False)
            results_json = json.dumps(results, ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO strategies (user_id, username, strategy_type, configuration, results, comments)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, strategy_type, config_json, results_json, comments))
            
            strategy_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Estrategia guardada exitosamente por {username}")
            return {
                "id": strategy_id,
                "user_id": user_id,
                "username": username,
                "strategy_type": strategy_type,
                "comments": comments,
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
                SELECT id, user_id, username, strategy_type, 
                       configuration, results, comments, created_at
                FROM strategies 
                ORDER BY created_at DESC
            """)
            
            strategies = []
            for row in cursor.fetchall():
                strategy_id, user_id, username, strategy_type, \
                config_json, results_json, comments, created_at = row
                
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
                
                # Obtener configuración formateada para mostrar
                formatted_config = self._format_configuration_for_display(configuration)
                
                strategies.append({
                    "id": strategy_id,
                    "user_id": user_id,
                    "username": username,
                    "strategy_type": strategy_type,
                    "configuration": configuration,
                    "results": results,
                    "created_at": created_at,
                    "comments": comments,
                    "num_trades": num_trades,
                    "total_pnl": total_pnl,
                    "total_costs": total_costs,
                    "net_pnl": net_pnl,
                    "formatted_config": formatted_config
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
                SELECT id, user_id, username, strategy_type, 
                       configuration, results, comments, created_at
                FROM strategies 
                WHERE id = ?
            """, (strategy_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            strategy_id, user_id, username, strategy_type, \
            config_json, results_json, comments, created_at = row
            
            # Parsear JSON
            try:
                configuration = json.loads(config_json)
                results = json.loads(results_json)
            except json.JSONDecodeError:
                logger.error(f"Error parseando JSON para estrategia {strategy_id}")
                return None
            
            # Obtener configuración formateada para mostrar
            formatted_config = self._format_configuration_for_display(configuration)
            
            return {
                "id": strategy_id,
                "user_id": user_id,
                "username": username,
                "strategy_type": strategy_type,
                "configuration": configuration,
                "results": results,
                "created_at": created_at,
                "comments": comments,
                "formatted_config": formatted_config
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
                SELECT id, user_id, username, strategy_type, 
                       configuration, results, comments, created_at
                FROM strategies 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            strategies = []
            for row in cursor.fetchall():
                strategy_id, user_id, username, strategy_type, \
                config_json, results_json, comments, created_at = row
                
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
                    "strategy_type": strategy_type,
                    "configuration": configuration,
                    "results": results,
                    "created_at": created_at,
                    "comments": comments
                })
            
            conn.close()
            return strategies
            
        except Exception as e:
            logger.error(f"Error obteniendo estrategias del usuario {user_id}: {e}")
            return []
    
    def _get_strategy_type_description(self, strategy_type: str, configuration: Dict[str, Any]) -> str:
        """Obtiene una descripción detallada del tipo de estrategia"""
        if strategy_type == "threshold":
            return "Estrategia de Umbrales"
        elif strategy_type == "crossover":
            crossover = configuration.get('crossover_strategy', {})
            entry_type = crossover.get('entry_type', 'SMA').upper()
            exit_type = crossover.get('exit_type', 'SMA').upper()
            entry_fast = crossover.get('entry_fast_period', 0)
            entry_slow = crossover.get('entry_slow_period', 0)
            exit_fast = crossover.get('exit_fast_period', 0)
            exit_slow = crossover.get('exit_slow_period', 0)
            return f"Cruce de Medias ({entry_type} {entry_fast}/{entry_slow} - {exit_type} {exit_fast}/{exit_slow})"
        elif strategy_type == "multi_dataset_crossover":
            return "Cruce Multi-Dataset"
        else:
            return strategy_type
    
    def _get_dataset_name(self, dataset_id: int, configuration: Dict[str, Any] = None) -> str:
        """Obtiene el nombre del dataset por su ID o desde la configuración guardada"""
        # Primero intentar obtener desde la configuración guardada
        if configuration and 'dataset_name' in configuration:
            return configuration['dataset_name']
        
        # Si no está en la configuración, intentar desde la base de datos SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM datasets WHERE id = ?", (dataset_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else f"Dataset {dataset_id}"
        except Exception as e:
            logger.error(f"Error obteniendo nombre del dataset {dataset_id}: {e}")
            return f"Dataset {dataset_id}"
    
    def _get_detailed_configuration(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene una configuración detallada con información descriptiva"""
        detailed_config = {
            "dataset": {
                "id": configuration.get('dataset_id'),
                "name": self._get_dataset_name(configuration.get('dataset_id', 0), configuration)
            },
            "strategy_type": {
                "internal": configuration.get('strategy_type'),
                "description": self._get_strategy_type_description(
                    configuration.get('strategy_type'), configuration
                )
            },
            "period": configuration.get('period'),
            "fees": configuration.get('fees'),
            "slippage": configuration.get('slippage'),
            "init_cash": configuration.get('init_cash'),
            "apply_to": configuration.get('apply_to'),
            "transformations": configuration.get('transform', {}),
            "thresholds": {
                "entry": configuration.get('threshold_entry'),
                "exit": configuration.get('threshold_exit')
            },
            "crossover_strategy": configuration.get('crossover_strategy'),
            "multi_dataset_crossover_strategy": configuration.get('multi_dataset_crossover_strategy')
        }
        return detailed_config
    
    def _format_configuration_for_display(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea la configuración para mostrar en la interfaz"""
        detailed_config = self._get_detailed_configuration(configuration)
        
        # Formatear transformaciones
        transform = detailed_config.get('transformations', {})
        transform_text = []
        if transform.get('v', {}).get('type') != 'none':
            v_transform = transform.get('v', {})
            transform_text.append(f"Indicador: {v_transform.get('type', '').upper()} {v_transform.get('period', '')}")
        if transform.get('usd', {}).get('type') != 'none':
            usd_transform = transform.get('usd', {})
            transform_text.append(f"Precio: {usd_transform.get('type', '').upper()} {usd_transform.get('period', '')}")
        
        # Formatear estrategia de cruce
        crossover_text = ""
        if detailed_config.get('strategy_type', {}).get('internal') == 'crossover':
            crossover = detailed_config.get('crossover_strategy', {})
            if crossover:
                crossover_text = f"Entrada: {crossover.get('entry_type', '').upper()} {crossover.get('entry_fast_period', '')}/{crossover.get('entry_slow_period', '')} | Salida: {crossover.get('exit_type', '').upper()} {crossover.get('exit_fast_period', '')}/{crossover.get('exit_slow_period', '')}"
        
        return {
            "dataset_name": detailed_config.get('dataset', {}).get('name'),
            "strategy_description": detailed_config.get('strategy_type', {}).get('description'),
            "period": detailed_config.get('period'),
            "fees_percentage": f"{detailed_config.get('fees', 0) * 100:.3f}%",
            "init_cash_formatted": f"${detailed_config.get('init_cash', 0):,.0f}",
            "transformations": transform_text,
            "thresholds": detailed_config.get('thresholds'),
            "crossover_details": crossover_text,
            "apply_to": detailed_config.get('apply_to'),
            "raw_configuration": configuration  # Configuración completa para referencia
        }
    
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
