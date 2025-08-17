import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def apply_transformations(df: pd.DataFrame, transform_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplica transformaciones a las columnas 'v' y 'usd' según la configuración.
    
    Args:
        df: DataFrame con columnas 't', 'v', 'usd'
        transform_config: Configuración de transformaciones
        
    Returns:
        pd.DataFrame: DataFrame con columnas transformadas
    """
    try:
        df_transformed = df.copy()
        
        # Aplicar transformación a 'v'
        if 'v' in transform_config:
            v_config = transform_config['v']
            df_transformed['v_transformed'] = apply_single_transformation(
                df['v'], 
                v_config['type'], 
                v_config['period']
            )
            logger.info(f"Transformación 'v': {v_config['type']} (periodo {v_config['period']})")
            logger.info(f"  - Original stats: min={df['v'].min():.4f}, max={df['v'].max():.4f}, mean={df['v'].mean():.4f}")
            logger.info(f"  - Transformado stats: min={df_transformed['v_transformed'].min():.4f}, max={df_transformed['v_transformed'].max():.4f}, mean={df_transformed['v_transformed'].mean():.4f}")
        else:
            df_transformed['v_transformed'] = df['v']
            logger.info("Transformación 'v': none (sin transformar)")
        
        # Aplicar transformación a 'usd'
        if 'usd' in transform_config:
            usd_config = transform_config['usd']
            df_transformed['usd_transformed'] = apply_single_transformation(
                df['usd'], 
                usd_config['type'], 
                usd_config['period']
            )
            logger.info(f"Transformación 'usd': {usd_config['type']} (periodo {usd_config['period']})")
        else:
            df_transformed['usd_transformed'] = df['usd']
            logger.info("Transformación 'usd': none (sin transformar)")
        
        logger.info("Transformaciones aplicadas correctamente")
        return df_transformed
        
    except Exception as e:
        logger.error(f"Error aplicando transformaciones: {str(e)}")
        raise e

def apply_single_transformation(series: pd.Series, transform_type: str, period: int) -> pd.Series:
    """
    Aplica una transformación específica a una serie de datos.
    
    Args:
        series: Serie de datos a transformar
        transform_type: Tipo de transformación ('none', 'sma', 'ema', 'median')
        period: Período para la transformación
        
    Returns:
        pd.Series: Serie transformada
    """
    try:
        if transform_type == 'none':
            return series
        
        elif transform_type == 'sma':
            return sma(series, period)
        
        elif transform_type == 'ema':
            return ema(series, period)
        
        elif transform_type == 'median':
            return median_filter(series, period)
        
        else:
            raise ValueError(f"Tipo de transformación no soportado: {transform_type}")
            
    except Exception as e:
        logger.error(f"Error en transformación {transform_type}: {str(e)}")
        raise e

def sma(series: pd.Series, period: int) -> pd.Series:
    """
    Calcula la Media Móvil Simple (Simple Moving Average).
    
    Args:
        series: Serie de datos
        period: Período de la media móvil
        
    Returns:
        pd.Series: Media móvil simple
    """
    return series.rolling(window=period, min_periods=1).mean()

def ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calcula la Media Móvil Exponencial (Exponential Moving Average).
    
    Args:
        series: Serie de datos
        period: Período de la media móvil
        
    Returns:
        pd.Series: Media móvil exponencial
    """
    alpha = 2.0 / (period + 1.0)
    return series.ewm(span=period, adjust=False).mean()

def median_filter(series: pd.Series, period: int) -> pd.Series:
    """
    Calcula la mediana móvil.
    
    Args:
        series: Serie de datos
        period: Período de la mediana móvil
        
    Returns:
        pd.Series: Mediana móvil
    """
    return series.rolling(window=period, min_periods=1).median()

def identity(series: pd.Series) -> pd.Series:
    """
    Transformación de identidad (sin cambios).
    
    Args:
        series: Serie de datos
        
    Returns:
        pd.Series: Serie sin cambios
    """
    return series.copy()
