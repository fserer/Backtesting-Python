import pandas as pd
import numpy as np
from fastapi import UploadFile, HTTPException
import logging
from typing import Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def process_csv_upload(file: UploadFile) -> Tuple[pd.DataFrame, str, int]:
    """
    Procesa un archivo CSV subido y retorna el DataFrame procesado,
    la frecuencia detectada y el número de filas.
    
    Args:
        file: Archivo CSV subido
        
    Returns:
        Tuple[pd.DataFrame, str, int]: (DataFrame procesado, frecuencia detectada, número de filas)
    """
    try:
        # Leer el CSV
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content))
        
        # Validar columnas requeridas
        required_columns = ['t', 'v', 'usd']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Columnas faltantes en el CSV: {missing_columns}. Se requieren: {required_columns}"
            )
        
        # Validar que no haya filas vacías
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="El archivo CSV está vacío"
            )
        
        # Limpiar datos
        df = df[required_columns].copy()
        df = df.dropna()
        
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="No hay datos válidos después de limpiar valores nulos"
            )
        
        # Procesar timestamp
        df = process_timestamps(df)
        
        # Ordenar por tiempo
        df = df.sort_values('t').reset_index(drop=True)
        
        # Detectar frecuencia
        freq_detected = detect_frequency(df)
        
        # Validar tipos de datos
        validate_data_types(df)
        
        logger.info(f"CSV procesado: {len(df)} filas, frecuencia: {freq_detected}")
        
        return df, freq_detected, len(df)
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al parsear el CSV")
    except Exception as e:
        logger.error(f"Error procesando CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando CSV: {str(e)}")

def process_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa la columna de timestamps, detectando si está en segundos o milisegundos
    y convirtiendo a datetime UTC.
    """
    try:
        # Convertir a numérico
        df['t'] = pd.to_numeric(df['t'], errors='coerce')
        df = df.dropna(subset=['t'])
        
        if df.empty:
            raise ValueError("No hay timestamps válidos después de la conversión")
        
        # Detectar si está en milisegundos o segundos
        # Si el timestamp es mayor a 1e10, probablemente está en milisegundos
        sample_timestamp = df['t'].iloc[0]
        
        if sample_timestamp > 1e10:  # Milisegundos
            df['t'] = pd.to_datetime(df['t'], unit='ms', utc=True)
            logger.info("Timestamps detectados en milisegundos")
        else:  # Segundos
            df['t'] = pd.to_datetime(df['t'], unit='s', utc=True)
            logger.info("Timestamps detectados en segundos")
        
        return df
        
    except Exception as e:
        logger.error(f"Error procesando timestamps: {str(e)}")
        raise ValueError(f"Error procesando timestamps: {str(e)}")

def detect_frequency(df: pd.DataFrame) -> str:
    """
    Detecta la frecuencia de los datos basándose en los deltas entre timestamps.
    
    Returns:
        str: '1D' para diario, '1H' para horario
    """
    try:
        # Calcular diferencias en segundos
        time_diffs = df['t'].diff().dropna()
        time_diffs_seconds = time_diffs.dt.total_seconds()
        
        if len(time_diffs_seconds) == 0:
            return '1H'  # Default
        
        # Calcular el delta modal (más común)
        mode_diff = time_diffs_seconds.mode().iloc[0]
        
        # Definir rangos de tolerancia (±5%)
        daily_range = (86400 * 0.95, 86400 * 1.05)  # ~24 horas
        hourly_range = (3600 * 0.95, 3600 * 1.05)   # ~1 hora
        
        if daily_range[0] <= mode_diff <= daily_range[1]:
            logger.info(f"Frecuencia detectada: Diaria (delta modal: {mode_diff:.0f}s)")
            return '1D'
        elif hourly_range[0] <= mode_diff <= hourly_range[1]:
            logger.info(f"Frecuencia detectada: Horaria (delta modal: {mode_diff:.0f}s)")
            return '1H'
        else:
            logger.warning(f"Frecuencia no reconocida (delta modal: {mode_diff:.0f}s), usando horaria por defecto")
            return '1H'
            
    except Exception as e:
        logger.error(f"Error detectando frecuencia: {str(e)}")
        return '1H'  # Default

def validate_data_types(df: pd.DataFrame) -> None:
    """
    Valida que los tipos de datos sean correctos.
    """
    try:
        # Validar que 'v' y 'usd' sean numéricos
        df['v'] = pd.to_numeric(df['v'], errors='coerce')
        df['usd'] = pd.to_numeric(df['usd'], errors='coerce')
        
        # Verificar que no haya valores nulos después de la conversión
        if df['v'].isna().any() or df['usd'].isna().any():
            raise ValueError("Columnas 'v' y 'usd' deben contener solo valores numéricos")
        
        # Verificar que los precios sean positivos
        if (df['usd'] <= 0).any():
            raise ValueError("Los precios USD deben ser positivos")
        
        logger.info("Validación de tipos de datos completada")
        
    except Exception as e:
        logger.error(f"Error en validación de tipos: {str(e)}")
        raise ValueError(f"Error en validación de tipos: {str(e)}")
