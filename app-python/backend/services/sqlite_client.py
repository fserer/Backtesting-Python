import sqlite3
import pandas as pd
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class SQLiteClient:
    def __init__(self, db_path: str = "data/backtesting.db"):
        """Inicializa el cliente SQLite."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos."""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa las tablas de la base de datos."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Crear tabla datasets
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    row_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear tabla ticks_new
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticks_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    t TIMESTAMP NOT NULL,
                    v REAL NOT NULL,
                    usd REAL NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
                )
            ''')
            
            # Crear índices para mejor rendimiento
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticks_dataset_id ON ticks_new (dataset_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticks_t ON ticks_new (t)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticks_dataset_t ON ticks_new (dataset_id, t)')
            
            conn.commit()
            logger.info("Base de datos SQLite inicializada correctamente")

# Instancia global del cliente
sqlite_client = SQLiteClient()

def create_dataset(name: str, description: str = None) -> Dict[str, Any]:
    """Crea un nuevo dataset."""
    try:
        with sqlite_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO datasets (name, description) VALUES (?, ?)',
                (name, description)
            )
            dataset_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Dataset creado: {name} (ID: {dataset_id})")
            return {
                'id': dataset_id,
                'name': name,
                'description': description,
                'row_count': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
    except sqlite3.IntegrityError:
        raise ValueError(f"Ya existe un dataset con el nombre '{name}'")
    except Exception as e:
        logger.error(f"Error creando dataset: {str(e)}")
        raise e

def get_all_datasets() -> List[Dict[str, Any]]:
    """Obtiene todos los datasets."""
    try:
        with sqlite_client.get_connection() as conn:
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
                    'created_at': row[4],
                    'updated_at': row[5]
                })
            
            logger.info(f"Obtenidos {len(datasets)} datasets")
            return datasets
    except Exception as e:
        logger.error(f"Error obteniendo datasets: {str(e)}")
        raise e

def get_dataset_by_id(dataset_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un dataset por ID."""
    try:
        with sqlite_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, row_count, created_at, updated_at
                FROM datasets
                WHERE id = ?
            ''', (dataset_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'row_count': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            return None
    except Exception as e:
        logger.error(f"Error obteniendo dataset {dataset_id}: {str(e)}")
        raise e

def update_dataset(dataset_id: int, name: str, description: str = None) -> Dict[str, Any]:
    """Actualiza un dataset."""
    try:
        with sqlite_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE datasets 
                SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
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
        with sqlite_client.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que existe
            cursor.execute('SELECT name FROM datasets WHERE id = ?', (dataset_id,))
            if not cursor.fetchone():
                raise ValueError(f"Dataset con ID {dataset_id} no encontrado")
            
            # Eliminar (CASCADE eliminará automáticamente los ticks)
            cursor.execute('DELETE FROM datasets WHERE id = ?', (dataset_id,))
            conn.commit()
            
            logger.info(f"Dataset eliminado: ID {dataset_id}")
    except Exception as e:
        logger.error(f"Error eliminando dataset {dataset_id}: {str(e)}")
        raise e

def save_ticks(dataset_id: int, df: pd.DataFrame) -> int:
    """Guarda los ticks en la base de datos."""
    try:
        with sqlite_client.get_connection() as conn:
            cursor = conn.cursor()
            
            # Preparar datos para inserción
            data_to_insert = []
            for _, row in df.iterrows():
                # Convertir timestamp a string ISO para SQLite
                timestamp_str = row['t'].isoformat() if hasattr(row['t'], 'isoformat') else str(row['t'])
                data_to_insert.append((
                    dataset_id,
                    timestamp_str,
                    float(row['v']),
                    float(row['usd'])
                ))
            
            # Insertar en lotes para mejor rendimiento
            cursor.executemany(
                'INSERT INTO ticks_new (dataset_id, t, v, usd) VALUES (?, ?, ?, ?)',
                data_to_insert
            )
            
            # Actualizar contador de registros
            cursor.execute('''
                UPDATE datasets 
                SET row_count = (SELECT COUNT(*) FROM ticks_new WHERE dataset_id = ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (dataset_id, dataset_id))
            
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
        with sqlite_client.get_connection() as conn:
            query = '''
                SELECT t, v, usd
                FROM ticks_new
                WHERE dataset_id = ?
                ORDER BY t ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(dataset_id,))
            
            # Convertir columna 't' a datetime con manejo de errores
            try:
                df['t'] = pd.to_datetime(df['t'])
            except Exception as e:
                logger.warning(f"Error convirtiendo fechas, usando formato original: {str(e)}")
                # Si falla, intentar con diferentes formatos
                df['t'] = pd.to_datetime(df['t'], errors='coerce')
            
            logger.info(f"Cargados {len(df)} registros del dataset {dataset_id}")
            return df
    except Exception as e:
        logger.error(f"Error cargando ticks del dataset {dataset_id}: {str(e)}")
        raise e

def update_dataset_row_count(dataset_id: int):
    """Actualiza el contador de registros de un dataset."""
    try:
        with sqlite_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE datasets 
                SET row_count = (SELECT COUNT(*) FROM ticks_new WHERE dataset_id = ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (dataset_id, dataset_id))
            conn.commit()
    except Exception as e:
        logger.error(f"Error actualizando contador de registros: {str(e)}")
        raise e

def get_dataset_by_name(dataset_name: str) -> Optional[Dict[str, Any]]:
    """Obtiene un dataset por su nombre."""
    try:
        with sqlite_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, row_count, created_at, updated_at
                FROM datasets
                WHERE name = ?
            ''', (dataset_name,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'row_count': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            return None
    except Exception as e:
        logger.error(f"Error obteniendo dataset {dataset_name}: {str(e)}")
        return None

def get_last_tick(dataset_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene el último tick de un dataset."""
    try:
        with sqlite_client.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, dataset_id, t, v, usd
                FROM ticks_new
                WHERE dataset_id = ?
                ORDER BY t DESC
                LIMIT 1
            ''', (dataset_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'dataset_id': row[1],
                    't': row[2],
                    'v': row[3],
                    'usd': row[4]
                }
            return None
    except Exception as e:
        logger.error(f"Error obteniendo último tick para dataset {dataset_id}: {str(e)}")
        return None
