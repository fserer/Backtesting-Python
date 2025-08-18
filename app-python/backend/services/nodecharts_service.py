import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

logger = logging.getLogger(__name__)

class NodeChartsService:
    """
    Servicio para actualizar datasets desde la API de NodeCharts.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.nodecharts.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_metric_data(self, metric_id: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Obtiene datos de una métrica específica desde NodeCharts.
        
        Args:
            metric_id: ID de la métrica en NodeCharts
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)
            
        Returns:
            DataFrame con los datos o None si hay error
        """
        try:
            url = f"{self.base_url}/api/v1/metrics/{metric_id}/data"
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "interval": "1h"  # Para datos horarios
            }
            
            logger.info(f"Consultando métrica {metric_id} desde {start_date} hasta {end_date}")
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or 'data' not in data:
                logger.warning(f"No se encontraron datos para la métrica {metric_id}")
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(data['data'])
            
            if df.empty:
                logger.warning(f"DataFrame vacío para la métrica {metric_id}")
                return None
            
            # Renombrar columnas para que coincidan con nuestro formato
            df = df.rename(columns={
                'timestamp': 't',
                'value': 'v',
                'price': 'usd'  # Asumiendo que hay una columna de precio
            })
            
            # Convertir timestamp a datetime
            df['t'] = pd.to_datetime(df['t'])
            
            # Ordenar por timestamp
            df = df.sort_values('t')
            
            logger.info(f"Obtenidos {len(df)} registros para la métrica {metric_id}")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la request a NodeCharts: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error procesando datos de NodeCharts: {str(e)}")
            return None
    
    def get_dataset_mapping(self) -> Dict[str, Dict]:
        """
        Mapeo de nuestros datasets a métricas de NodeCharts.
        
        Returns:
            Diccionario con el mapeo de datasets
        """
        return {
            "SOPR CP - HOUR": {
                "metric_id": "sopr_cp_hour",
                "description": "SOPR de corto plazo, periodicidad horaria",
                "interval": "1h"
            }
            # Añadir más mapeos según sea necesario
        }
    
    def get_last_available_date(self, dataset_name: str, db_client) -> Optional[datetime]:
        """
        Obtiene la última fecha disponible en nuestro dataset.
        
        Args:
            dataset_name: Nombre del dataset
            db_client: Cliente de base de datos
            
        Returns:
            Última fecha disponible o None si no hay datos
        """
        try:
            # Importar funciones de SQLite
            from services.sqlite_client import get_dataset_by_name, get_last_tick
            
            # Obtener el dataset
            dataset = get_dataset_by_name(dataset_name)
            if not dataset:
                logger.warning(f"Dataset {dataset_name} no encontrado")
                return None
            
            # Obtener la última fecha de los ticks
            last_tick = get_last_tick(dataset['id'])
            if not last_tick:
                logger.warning(f"No hay ticks para el dataset {dataset_name}")
                return None
            
            return pd.to_datetime(last_tick['t'])
            
        except Exception as e:
            logger.error(f"Error obteniendo última fecha para {dataset_name}: {str(e)}")
            return None
    
    def update_dataset(self, dataset_name: str, db_client) -> Tuple[bool, int]:
        """
        Actualiza un dataset con datos nuevos desde NodeCharts.
        
        Args:
            dataset_name: Nombre del dataset a actualizar
            db_client: Cliente de base de datos
            
        Returns:
            Tuple (éxito, número de registros añadidos)
        """
        try:
            # Importar funciones de SQLite
            from services.sqlite_client import get_dataset_by_name, save_ticks, update_dataset_row_count
            
            # Obtener mapeo
            mapping = self.get_dataset_mapping()
            if dataset_name not in mapping:
                logger.error(f"No hay mapeo para el dataset {dataset_name}")
                return False, 0
            
            metric_config = mapping[dataset_name]
            metric_id = metric_config["metric_id"]
            
            # Obtener última fecha disponible
            last_date = self.get_last_available_date(dataset_name, db_client)
            if not last_date:
                logger.error(f"No se pudo obtener la última fecha para {dataset_name}")
                return False, 0
            
            # Calcular fechas para la consulta
            start_date = (last_date + timedelta(hours=1)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            logger.info(f"Actualizando {dataset_name} desde {start_date} hasta {end_date}")
            
            # Obtener datos nuevos
            new_data = self.get_metric_data(metric_id, start_date, end_date)
            if new_data is None or new_data.empty:
                logger.info(f"No hay datos nuevos para {dataset_name}")
                return True, 0
            
            # Obtener el dataset
            dataset = get_dataset_by_name(dataset_name)
            if not dataset:
                logger.error(f"Dataset {dataset_name} no encontrado")
                return False, 0
            
            # Guardar datos nuevos
            rows_added = save_ticks(dataset['id'], new_data)
            
            # Actualizar contador de filas del dataset
            update_dataset_row_count(dataset['id'])
            
            logger.info(f"Dataset {dataset_name} actualizado: {rows_added} registros añadidos")
            return True, rows_added
            
        except Exception as e:
            logger.error(f"Error actualizando dataset {dataset_name}: {str(e)}")
            return False, 0
    
    def update_all_datasets(self, db_client) -> Dict[str, Tuple[bool, int]]:
        """
        Actualiza todos los datasets que tienen mapeo con NodeCharts.
        
        Args:
            db_client: Cliente de base de datos
            
        Returns:
            Diccionario con resultados por dataset
        """
        results = {}
        mapping = self.get_dataset_mapping()
        
        for dataset_name in mapping.keys():
            logger.info(f"Actualizando dataset: {dataset_name}")
            success, rows_added = self.update_dataset(dataset_name, db_client)
            results[dataset_name] = (success, rows_added)
            
            # Pausa entre requests para no sobrecargar la API
            time.sleep(1)
        
        return results
