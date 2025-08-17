import psycopg2
import pandas as pd
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PostgreSQLClient:
    def __init__(self, database_url: str = None):
        """Inicializa el cliente PostgreSQL."""
        self.database_url = database_url or os.getenv('DATABASE_URL', 'postgresql://backtesting_user:backtesting_password@localhost:5432/backtesting')
        logger.info("Cliente PostgreSQL inicializado")
    
    @contextmanager
    def get_connection(self):
        """Obtiene una conexión a la base de datos PostgreSQL."""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {str(e)}")
            raise e
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Inicializa las tablas de la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar que TimescaleDB está habilitado
                cursor.execute("SELECT * FROM pg_extension WHERE extname = 'timescaledb';")
                if not cursor.fetchone():
                    logger.warning("TimescaleDB no está habilitado. Algunas funciones pueden no estar disponibles.")
                
                # Verificar que las tablas existen
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('datasets', 'ticks');
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                if len(tables) < 2:
                    logger.warning("Algunas tablas no existen. Ejecuta setup_database.sql primero.")
                
                conn.commit()
                logger.info("Base de datos PostgreSQL verificada correctamente")
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {str(e)}")
            raise e

# Instancia global del cliente
postgres_client = PostgreSQLClient()

def create_dataset(name: str, description: str = None) -> Dict[str, Any]:
    """Crea un nuevo dataset."""
    try:
        with postgres_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO datasets (name, description) VALUES (%s, %s) RETURNING id, created_at, updated_at',
                (name, description)
            )
            dataset_id, created_at, updated_at = cursor.fetchone()
            conn.commit()
            
            logger.info(f"Dataset creado: {name} (ID: {dataset_id})")
            return {
                'id': dataset_id,
                'name': name,
                'description': description,
                'row_count': 0,
                'created_at': created_at.isoformat(),
                'updated_at': updated_at.isoformat()
            }
    except psycopg2.IntegrityError:
        raise ValueError(f"Ya existe un dataset con el nombre '{name}'")
    except Exception as e:
        logger.error(f"Error creando dataset: {str(e)}")
        raise e

def get_all_datasets() -> List[Dict[str, Any]]:
    """Obtiene todos los datasets."""
    try:
        with postgres_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, row_count, created_at, updated_at
                FROM datasets
                ORDER BY created_at DESC
            ''')
            
            datasets = []
            for row in cursor.fetchall():
                datasets.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'row_count': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'updated_at': row[5].isoformat() if row[5] else None
                })
            
            logger.info(f"Obtenidos {len(datasets)} datasets")
            return datasets
    except Exception as e:
        logger.error(f"Error obteniendo datasets: {str(e)}")
        raise e

def get_dataset_by_id(dataset_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un dataset por ID."""
    try:
        with postgres_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, row_count, created_at, updated_at
                FROM datasets
                WHERE id = %s
            ''', (dataset_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'row_count': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'updated_at': row[5].isoformat() if row[5] else None
                }
            return None
    except Exception as e:
        logger.error(f"Error obteniendo dataset {dataset_id}: {str(e)}")
        raise e

def update_dataset(dataset_id: int, name: str, description: str = None) -> Dict[str, Any]:
    """Actualiza un dataset."""
    try:
        with postgres_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE datasets 
                SET name = %s, description = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (name, description, dataset_id))
            
            if cursor.rowcount == 0:
                raise ValueError(f"Dataset con ID {dataset_id} no encontrado")
            
            conn.commit()
            
            logger.info(f"Dataset actualizado: {name} (ID: {dataset_id})")
            return get_dataset_by_id(dataset_id)
    except Exception as e:
        logger.error(f"Error actualizando dataset {dataset_id}: {str(e)}")
        raise e

def delete_dataset(dataset_id: int):
    """Elimina un dataset y todos sus datos."""
    try:
        with postgres_client.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que existe
            cursor.execute('SELECT name FROM datasets WHERE id = %s', (dataset_id,))
            if not cursor.fetchone():
                raise ValueError(f"Dataset con ID {dataset_id} no encontrado")
            
            # Eliminar (CASCADE eliminará automáticamente los ticks)
            cursor.execute('DELETE FROM datasets WHERE id = %s', (dataset_id,))
            conn.commit()
            
            logger.info(f"Dataset eliminado: ID {dataset_id}")
    except Exception as e:
        logger.error(f"Error eliminando dataset {dataset_id}: {str(e)}")
        raise e

def save_ticks(dataset_id: int, df: pd.DataFrame) -> int:
    """Guarda los ticks en la base de datos PostgreSQL."""
    try:
        with postgres_client.get_connection() as conn:
            cursor = conn.cursor()
            
            # Preparar datos para inserción usando COPY (más eficiente)
            data_to_insert = []
            for _, row in df.iterrows():
                # Convertir timestamp a string ISO para PostgreSQL
                timestamp_str = row['t'].isoformat() if hasattr(row['t'], 'isoformat') else str(row['t'])
                data_to_insert.append((
                    dataset_id,
                    timestamp_str,
                    float(row['v']),
                    float(row['usd'])
                ))
            
            # Usar executemany para inserción en lotes
            cursor.executemany(
                'INSERT INTO ticks (dataset_id, t, v, usd) VALUES (%s, %s, %s, %s)',
                data_to_insert
            )
            
            conn.commit()
            
            rows_inserted = len(data_to_insert)
            logger.info(f"Guardados {rows_inserted} registros en dataset {dataset_id}")
            return rows_inserted
    except Exception as e:
        logger.error(f"Error guardando ticks: {str(e)}")
        raise e

def load_ticks_by_dataset(dataset_id: int) -> pd.DataFrame:
    """Carga todos los ticks de un dataset específico."""
    try:
        with postgres_client.get_connection() as conn:
            query = '''
                SELECT t, v, usd
                FROM ticks
                WHERE dataset_id = %s
                ORDER BY t ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(dataset_id,))
            
            # Convertir columna 't' a datetime
            try:
                df['t'] = pd.to_datetime(df['t'])
            except Exception as e:
                logger.warning(f"Error convirtiendo fechas, usando formato original: {str(e)}")
                df['t'] = pd.to_datetime(df['t'], errors='coerce')
            
            logger.info(f"Cargados {len(df)} registros del dataset {dataset_id}")
            return df
    except Exception as e:
        logger.error(f"Error cargando ticks del dataset {dataset_id}: {str(e)}")
        raise e

def get_dataset_stats(dataset_id: int) -> Dict[str, Any]:
    """Obtiene estadísticas de un dataset usando la función de PostgreSQL."""
    try:
        with postgres_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM get_dataset_stats(%s)', (dataset_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_rows': row[0],
                    'date_range': str(row[1]) if row[1] else None,
                    'min_price': float(row[2]) if row[2] else None,
                    'max_price': float(row[3]) if row[3] else None,
                    'avg_price': float(row[4]) if row[4] else None
                }
            return {}
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del dataset {dataset_id}: {str(e)}")
        return {}
