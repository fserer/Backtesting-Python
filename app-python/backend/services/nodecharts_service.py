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
    
    def get_families(self) -> Optional[List[Dict]]:
        """
        Obtiene la lista de families disponibles en NodeCharts.
        
        Returns:
            Lista de families o None si hay error
        """
        try:
            url = f"{self.base_url}/v1/families"
            logger.info(f"Consultando families: {url}")
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Obtenidas {len(data)} families de NodeCharts")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la request a NodeCharts families: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error procesando families de NodeCharts: {str(e)}")
            return None

    def get_metrics_in_family(self, family_id: str) -> Optional[List[Dict]]:
        """
        Obtiene las métricas dentro de una familia específica.
        
        Args:
            family_id: ID de la familia
            
        Returns:
            Lista de métricas o None si hay error
        """
        try:
            # Probar diferentes URLs base y endpoints
            for base_url in self.base_urls:
                endpoints = [
                    f"/api/v1/families/{family_id}/metrics",
                    f"/api/families/{family_id}/metrics",
                    f"/families/{family_id}/metrics",
                    f"/api/v1/metrics?family_id={family_id}",
                    f"/api/metrics?family_id={family_id}"
                ]
                
                for endpoint in endpoints:
                    try:
                        url = f"{base_url}{endpoint}"
                        logger.info(f"Probando endpoint para métricas de familia {family_id}: {url}")
                        
                        response = requests.get(url, headers=self.headers)
                        response.raise_for_status()
                        
                        data = response.json()
                        logger.info(f"Respuesta exitosa del endpoint {endpoint}")
                        logger.info(f"Estructura de respuesta: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
                        
                        # Intentar diferentes estructuras de respuesta
                        if isinstance(data, dict):
                            if 'metrics' in data:
                                metrics = data['metrics']
                                logger.info(f"Obtenidas {len(metrics)} métricas de la familia {family_id}")
                                return metrics
                            elif 'data' in data and isinstance(data['data'], list):
                                metrics = data['data']
                                logger.info(f"Obtenidas {len(metrics)} métricas de la familia {family_id} (en 'data')")
                                return metrics
                        elif isinstance(data, list):
                            logger.info(f"Obtenidas {len(data)} métricas de la familia {family_id} (lista directa)")
                            return data
                            
                    except requests.exceptions.RequestException as e:
                        logger.warning(f"Endpoint {endpoint} falló: {str(e)}")
                        continue
            
            logger.error(f"Ningún endpoint funcionó para obtener métricas de la familia {family_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error procesando métricas de la familia {family_id}: {str(e)}")
            return None

    def find_metric_info(self, dataset_name: str) -> Optional[Dict]:
        """
        Encuentra la información de una métrica basándose en el nombre del dataset.
        Busca tanto en familias como subfamilias de manera automática.
        
        Args:
            dataset_name: Nombre del dataset (ej: "SOPR CP - HOUR")
            
        Returns:
            Diccionario con 'id', 'endpoint', 'interval' o None si no se encuentra
        """
        try:
            families = self.get_families()
            if not families:
                logger.error("No se pudieron obtener las families")
                return None
            
            # Normalizar el nombre del dataset para búsqueda
            # "SOPR CP - HOUR" -> buscar "sopr cp" con intervalo "hour"
            dataset_parts = dataset_name.lower().split(" - ")
            if len(dataset_parts) != 2:
                logger.error(f"Formato de dataset incorrecto: {dataset_name}")
                return None
            
            metric_name = dataset_parts[0].strip()  # "sopr cp"
            # Mapear intervalo a formato esperado por la API
            interval_raw = dataset_parts[1].strip().lower()
            interval_map = {"hour": "Hour", "day": "Day", "block": "Block"}
            interval = interval_map.get(interval_raw, dataset_parts[1])
            
            logger.info(f"Buscando métrica: '{metric_name}' con intervalo '{interval}'")
            
            # Buscar en todas las familias y sus indicadores
            for family in families:
                family_name = str(family.get('name', '')).lower()
                indicators = family.get('indicators', [])
                
                # Buscar en los indicadores de la familia
                for indicator in indicators:
                    indicator_name = str(indicator.get('name', '')).lower()
                    
                    # Verificar coincidencia exacta
                    if indicator_name == metric_name:
                        logger.info(
                            f"✅ Encontrada métrica: {indicator.get('name')} (ID: {indicator.get('id')}, Endpoint: {indicator.get('endpoint')}) en familia {family.get('name')}"
                        )
                        resolutions = indicator.get('resolutions', [])
                        if interval in resolutions:
                            return {
                                'id': str(indicator.get('id')),
                                'endpoint': indicator.get('endpoint'),
                                'interval': interval,
                                'family_name': family.get('name'),
                                'metric_name': indicator.get('name')
                            }
                        else:
                            logger.warning(
                                f"Intervalo '{interval}' no disponible para la métrica {indicator.get('name')}. Disponibles: {resolutions}"
                            )
                
                # Si no encontramos en indicadores, verificar si el nombre de la familia coincide
                if family_name == metric_name and indicators:
                    logger.info(f"Usando métrica de familia: {family.get('name')}")
                    # Tomar el primer indicador de la familia
                    indicator = indicators[0]
                    resolutions = indicator.get('resolutions', [])
                    if interval in resolutions:
                        return {
                            'id': str(indicator.get('id')),
                            'endpoint': indicator.get('endpoint'),
                            'interval': interval,
                            'family_name': family.get('name'),
                            'metric_name': indicator.get('name')
                        }
            
            logger.warning(f"❌ No se encontró métrica para: {dataset_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error buscando métrica {dataset_name}: {str(e)}")
            return None

    def find_metric_id(self, dataset_name: str) -> Optional[str]:
        """
        Encuentra el ID de una métrica basándose en el nombre del dataset.
        
        Args:
            dataset_name: Nombre del dataset (ej: "SOPR CP - HOUR")
            
        Returns:
            ID de la métrica o None si no se encuentra
        """
        metric_info = self.find_metric_info(dataset_name)
        return metric_info['id'] if metric_info else None

    def get_metric_data(self, metric_endpoint: str, from_timestamp: str, interval: str = "Hour") -> Optional[pd.DataFrame]:
        """
        Obtiene datos de una métrica específica desde NodeCharts.
        
        Args:
            metric_endpoint: Endpoint de la métrica (ej: "sopr_short_term")
            from_timestamp: Timestamp desde el cual obtener datos (formato ISO)
            interval: Intervalo de datos ("Hour", "Day", "Block")
            
        Returns:
            DataFrame con los datos o None si hay error
        """
        try:
            # Convertir from_timestamp a Unix timestamp
            import pandas as pd
            from datetime import datetime
            
            # Convertir a datetime si es string
            if isinstance(from_timestamp, str):
                dt = pd.to_datetime(from_timestamp)
            else:
                dt = from_timestamp
            
            # Convertir a Unix timestamp (segundos desde epoch)
            unix_timestamp = int(dt.timestamp())
            
            # Construir URL con el formato correcto: /v1/metric/{endpoint}/{userhash}
            url = f"{self.base_url}/v1/metric/{metric_endpoint}/{self.api_key}"
            
            params = {
                "f": unix_timestamp,  # From timestamp en Unix time
                "i": interval         # Interval (Hour, Day, Block)
            }
            
            logger.info(f"Consultando métrica {metric_endpoint} desde {from_timestamp} con intervalo {interval}")
            logger.info(f"URL: {url}")
            logger.info(f"Parámetros: {params}")
            
            response = requests.get(url, params=params)  # No usamos headers aquí
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Respuesta exitosa del endpoint")
            logger.info(f"Estructura de respuesta: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
            
            # Intentar diferentes estructuras de respuesta
            if isinstance(data, dict):
                if 'data' in data:
                    df_data = data['data']
                elif 'values' in data:
                    df_data = data['values']
                elif 'results' in data:
                    df_data = data['results']
                else:
                    # Si no hay estructura específica, usar los datos directamente
                    df_data = data
            elif isinstance(data, list):
                df_data = data
            else:
                logger.warning(f"Formato de respuesta inesperado para la métrica {metric_endpoint}")
                return None
            
            if not df_data:
                logger.warning(f"No se encontraron datos para la métrica {metric_endpoint}")
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(df_data)
            
            if df.empty:
                logger.warning(f"DataFrame vacío para la métrica {metric_endpoint}")
                return None
            
            # Renombrar columnas para que coincidan con nuestro formato
            column_mapping = {}
            if 'timestamp' in df.columns:
                column_mapping['timestamp'] = 't'
            if 'value' in df.columns:
                column_mapping['value'] = 'v'
            if 'price' in df.columns:
                column_mapping['price'] = 'usd'
            
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            # Convertir timestamp a datetime si existe la columna 't'
            if 't' in df.columns:
                # Si viene como número (unix seconds), indicar unit='s' para evitar 1970
                if pd.api.types.is_numeric_dtype(df['t']):
                    df['t'] = pd.to_datetime(df['t'], unit='s', utc=True)
                else:
                    df['t'] = pd.to_datetime(df['t'], utc=True)
                # Ordenar por timestamp
                df = df.sort_values('t')
            
            logger.info(f"Obtenidos {len(df)} registros para la métrica {metric_endpoint}")
            logger.info(f"Columnas del DataFrame: {list(df.columns)}")
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
        Ahora se hace automáticamente basándose en el nombre del dataset.
        
        Returns:
            Diccionario con el mapeo de datasets
        """
        return {
            # Los IDs se obtienen automáticamente de la API de NodeCharts
            # basándose en el nombre del dataset
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
            
            # Buscar la información de la métrica automáticamente
            metric_info = self.find_metric_info(dataset_name)
            if not metric_info:
                logger.error(f"No se pudo encontrar la información de la métrica para {dataset_name}")
                return False, 0
            
            metric_id = metric_info['id']
            metric_endpoint = metric_info['endpoint']
            interval = metric_info['interval']
            
            logger.info(f"Información de métrica encontrada para {dataset_name}:")
            logger.info(f"  - ID: {metric_id}")
            logger.info(f"  - Endpoint: {metric_endpoint}")
            logger.info(f"  - Intervalo: {interval}")
            
            # Obtener última fecha disponible
            last_date = self.get_last_available_date(dataset_name, db_client)
            if not last_date:
                logger.error(f"No se pudo obtener la última fecha para {dataset_name}")
                return False, 0
            
            # Calcular from_timestamp exclusivo (last_date + 1 unidad de intervalo)
            if interval == "Hour":
                exclusive_from = last_date + timedelta(hours=1)
            elif interval == "Day":
                exclusive_from = last_date + timedelta(days=1)
            else:
                # Por defecto, añadir 1 segundo
                exclusive_from = last_date + timedelta(seconds=1)
            
            # Convertir a formato ISO para pasarlo (internamente se convierte a UNIX)
            from_timestamp = exclusive_from.isoformat()
            
            logger.info(f"Actualizando {dataset_name} desde {from_timestamp} con intervalo {interval}")
            
            # Obtener datos nuevos
            new_data = self.get_metric_data(metric_endpoint, from_timestamp, interval)
            if new_data is None or new_data.empty:
                logger.info(f"No hay datos nuevos para {dataset_name}")
                return True, 0
            
            # Seguridad: filtrar por si el proveedor devuelve el punto inicial inclusivo
            try:
                last_date_utc = pd.to_datetime(last_date, utc=True)
                if 't' in new_data.columns:
                    new_data = new_data[new_data['t'] > last_date_utc]
            except Exception:
                pass
            
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
        Actualiza automáticamente todos los datasets disponibles que pueden ser mapeados con NodeCharts.
        
        Args:
            db_client: Cliente de base de datos
            
        Returns:
            Diccionario con resultados por dataset
        """
        try:
            # Importar funciones de SQLite
            from services.sqlite_client import get_all_datasets
            
            # Obtener todos los datasets disponibles
            all_datasets = get_all_datasets()
            logger.info(f"Encontrados {len(all_datasets)} datasets para procesar")
            
            results = {}
            
            for dataset in all_datasets:
                dataset_name = dataset['name']
                logger.info(f"🔍 Procesando dataset: {dataset_name}")
                
                # Intentar encontrar métrica para este dataset
                metric_info = self.find_metric_info(dataset_name)
                
                if metric_info:
                    logger.info(f"✅ Métrica encontrada para {dataset_name}: {metric_info['metric_name']} (Endpoint: {metric_info['endpoint']})")
                    success, rows_added = self.update_dataset(dataset_name, db_client)
                    results[dataset_name] = {
                        'success': success,
                        'rows_added': rows_added,
                        'metric_info': metric_info
                    }
                else:
                    logger.warning(f"❌ No se pudo mapear el dataset: {dataset_name}")
                    results[dataset_name] = {
                        'success': False,
                        'rows_added': 0,
                        'error': 'No se encontró métrica correspondiente'
                    }
                
                # Pausa entre requests para no sobrecargar la API
                time.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"Error en actualización masiva: {str(e)}")
            return {}
