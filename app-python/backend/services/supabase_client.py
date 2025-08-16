import pandas as pd
import numpy as np
from supabase import create_client, Client
from core.config import settings
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Crear cliente de Supabase
supabase: Client = create_client(settings.supabase_url, settings.supabase_anon_key)

async def create_dataset(name: str, description: Optional[str] = None) -> int:
    """
    Crea un nuevo dataset.
    
    Args:
        name: Nombre del dataset
        description: Descripción opcional
    
    Returns:
        int: ID del dataset creado
    """
    try:
        result = supabase.table('datasets').insert({
            'name': name,
            'description': description
        }).execute()
        
        if not result.data:
            raise Exception("No se pudo crear el dataset")
        
        dataset_id = result.data[0]['id']
        logger.info(f"Dataset creado: {name} (ID: {dataset_id})")
        return dataset_id
        
    except Exception as e:
        logger.error(f"Error creando dataset: {str(e)}")
        raise e

async def save_ticks(df: pd.DataFrame, dataset_id: int) -> bool:
    """
    Guarda los datos de ticks en Supabase para un dataset específico.
    
    Args:
        df: DataFrame con columnas 't', 'v', 'usd'
        dataset_id: ID del dataset
    
    Returns:
        bool: True si se guardó correctamente
    """
    try:
        # Preparar datos para inserción
        data_to_insert = []
        for _, row in df.iterrows():
            data_to_insert.append({
                'dataset_id': dataset_id,
                't': row['t'].isoformat() if hasattr(row['t'], 'isoformat') else str(row['t']),
                'v': float(row['v']),
                'usd': float(row['usd'])
            })
        
        # Insertar en lotes de 1000 para evitar límites
        batch_size = 1000
        for i in range(0, len(data_to_insert), batch_size):
            batch = data_to_insert[i:i + batch_size]
            result = supabase.table('ticks_new').insert(batch).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Error insertando lote {i//batch_size + 1}: {result.error}")
                return False
        
        # Actualizar el conteo de filas en el dataset
        await update_dataset_row_count(dataset_id, len(data_to_insert))
        
        logger.info(f"Guardados {len(data_to_insert)} registros en dataset {dataset_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error guardando en Supabase: {str(e)}")
        raise e

async def load_ticks_by_dataset(dataset_id: int) -> pd.DataFrame:
    """
    Carga los datos de ticks para un dataset específico.
    
    Args:
        dataset_id: ID del dataset
    
    Returns:
        pd.DataFrame: DataFrame con columnas 't', 'v', 'usd' ordenado por tiempo
    """
    try:
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            # Obtener datos con paginación para el dataset específico
            result = supabase.table('ticks_new').select('*').eq('dataset_id', dataset_id).order('t').range(offset, offset + page_size - 1).execute()
            
            if not result.data:
                break
                
            all_data.extend(result.data)
            offset += page_size
            
            # Si obtenemos menos registros que el page_size, hemos terminado
            if len(result.data) < page_size:
                break
        
        if not all_data:
            logger.warning(f"No se encontraron datos para el dataset {dataset_id}")
            return pd.DataFrame(columns=['t', 'v', 'usd'])
        
        # Convertir a DataFrame
        df = pd.DataFrame(all_data)
        
        # Convertir columna 't' a datetime
        df['t'] = pd.to_datetime(df['t'])
        
        # Ordenar por tiempo
        df = df.sort_values('t').reset_index(drop=True)
        
        logger.info(f"Cargados {len(df)} registros del dataset {dataset_id}")
        return df
        
    except Exception as e:
        logger.error(f"Error cargando dataset {dataset_id}: {str(e)}")
        raise e

async def get_all_datasets() -> List[Dict[str, Any]]:
    """
    Obtiene todos los datasets disponibles.
    
    Returns:
        List[Dict]: Lista de datasets con sus metadatos
    """
    try:
        result = supabase.table('datasets').select('*').order('created_at', desc=True).execute()
        
        if not result.data:
            return []
        
        logger.info(f"Obtenidos {len(result.data)} datasets")
        return result.data
        
    except Exception as e:
        logger.error(f"Error obteniendo datasets: {str(e)}")
        raise e

async def get_dataset_by_id(dataset_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un dataset específico por ID.
    
    Args:
        dataset_id: ID del dataset
    
    Returns:
        Optional[Dict]: Datos del dataset o None si no existe
    """
    try:
        result = supabase.table('datasets').select('*').eq('id', dataset_id).execute()
        
        if not result.data:
            return None
        
        return result.data[0]
        
    except Exception as e:
        logger.error(f"Error obteniendo dataset {dataset_id}: {str(e)}")
        raise e

async def update_dataset(dataset_id: int, name: Optional[str] = None, description: Optional[str] = None) -> bool:
    """
    Actualiza un dataset existente.
    
    Args:
        dataset_id: ID del dataset
        name: Nuevo nombre (opcional)
        description: Nueva descripción (opcional)
    
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        
        if not update_data:
            return True
        
        update_data['updated_at'] = datetime.now().isoformat()
        
        result = supabase.table('datasets').update(update_data).eq('id', dataset_id).execute()
        
        if not result.data:
            return False
        
        logger.info(f"Dataset {dataset_id} actualizado")
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando dataset {dataset_id}: {str(e)}")
        raise e

async def delete_dataset(dataset_id: int) -> bool:
    """
    Elimina un dataset y todos sus datos.
    
    Args:
        dataset_id: ID del dataset
    
    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        # Eliminar el dataset (los ticks se eliminan automáticamente por CASCADE)
        result = supabase.table('datasets').delete().eq('id', dataset_id).execute()
        
        if not result.data:
            return False
        
        logger.info(f"Dataset {dataset_id} eliminado")
        return True
        
    except Exception as e:
        logger.error(f"Error eliminando dataset {dataset_id}: {str(e)}")
        raise e

async def update_dataset_row_count(dataset_id: int, row_count: int) -> bool:
    """
    Actualiza el conteo de filas de un dataset.
    
    Args:
        dataset_id: ID del dataset
        row_count: Número de filas
    
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        result = supabase.table('datasets').update({
            'row_count': row_count,
            'updated_at': datetime.now().isoformat()
        }).eq('id', dataset_id).execute()
        
        return bool(result.data)
        
    except Exception as e:
        logger.error(f"Error actualizando conteo de filas del dataset {dataset_id}: {str(e)}")
        return False

async def clear_ticks() -> bool:
    """
    Limpia todos los datos de la tabla ticks.
    Solo usar en desarrollo o cuando se quiera empezar de nuevo.
    """
    try:
        result = supabase.table('ticks').delete().neq('id', 0).execute()
        logger.info("Tabla ticks limpiada")
        return True
    except Exception as e:
        logger.error(f"Error limpiando tabla: {str(e)}")
        return False

async def get_ticks_count() -> int:
    """
    Obtiene el número total de registros en la tabla ticks.
    """
    try:
        result = supabase.table('ticks').select('id', count='exact').execute()
        return result.count if hasattr(result, 'count') else 0
    except Exception as e:
        logger.error(f"Error obteniendo conteo: {str(e)}")
        return 0
