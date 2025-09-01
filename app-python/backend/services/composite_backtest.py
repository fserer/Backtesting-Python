import pandas as pd
import numpy as np
import vectorbt as vbt
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from .backtest import (
    filter_data_by_period, determine_frequency, generate_signals,
    calculate_metrics
)
from .transform import apply_transformations
from .sqlite_client import load_ticks_by_dataset

logger = logging.getLogger(__name__)

def run_composite_backtest(request) -> Dict[str, Any]:
    """
    Ejecuta un backtest compuesto con múltiples condiciones.
    
    Args:
        request: CompositeBacktestRequest con las condiciones y parámetros
        
    Returns:
        Dict con resultados del backtest
    """
    try:
        logger.info(f"Iniciando backtest compuesto con {len(request.conditions)} condiciones")
        
        # Obtener el primer dataset para determinar el período base
        base_dataset_id = request.conditions[0].dataset_id
        base_df = load_ticks_by_dataset(base_dataset_id)
        
        if base_df.empty:
            raise ValueError(f"No hay datos disponibles en el dataset base {base_dataset_id}")
        
        # Filtrar datos por período
        base_df_filtered = filter_data_by_period(base_df, request.period)
        
        if base_df_filtered.empty:
            raise ValueError(f"No hay datos disponibles para el período '{request.period}'")
        
        logger.info(f"Período seleccionado: {request.period} - {len(base_df_filtered)} registros")
        
        # Determinar frecuencia
        freq = determine_frequency(base_df_filtered, None)
        
        # Generar señales compuestas
        composite_signals = generate_composite_signals(request.conditions, request.period)
        
        # Preparar datos para vectorbt
        close_prices = base_df_filtered['usd'].values  # Usar precio USD del dataset base
        
        # Aplicar señales compuestas
        entries = composite_signals['entries'].values
        exits = composite_signals['exits'].values
        
        # Configurar parámetros de vectorbt
        vbt_settings = {
            'close': close_prices,
            'entries': entries,
            'exits': exits,
            'fees': request.fees,
            'slippage': request.slippage,
            'init_cash': request.init_cash,
            'freq': freq,
            'accumulate': False,
            'upon_long_conflict': 'ignore',
            'upon_short_conflict': 'ignore'
        }
        
        # Ejecutar backtest
        portfolio = vbt.Portfolio.from_signals(**vbt_settings)
        
        # Calcular métricas
        results = calculate_metrics(portfolio, base_df_filtered)
        
        logger.info(f"Backtest compuesto completado: {results['results']['trades']} trades, {results['results']['total_return']:.2%} retorno")
        
        return results
        
    except Exception as e:
        logger.error(f"Error en backtest compuesto: {str(e)}")
        raise e

def generate_composite_signals(conditions: List, period: str) -> pd.DataFrame:
    """
    Genera señales compuestas combinando múltiples condiciones.
    
    Args:
        conditions: Lista de condiciones de estrategia
        period: Período a filtrar
        
    Returns:
        DataFrame con señales de entrada y salida compuestas
    """
    try:
        # Obtener el primer dataset para crear el DataFrame base de señales
        base_dataset_id = conditions[0].dataset_id
        base_df = load_ticks_by_dataset(base_dataset_id)
        base_df_filtered = filter_data_by_period(base_df, period)
        
        # Crear DataFrame base para señales
        signals_df = pd.DataFrame(index=base_df_filtered.index)
        signals_df['entries'] = False
        signals_df['exits'] = False
        
        # Procesar cada condición
        for i, condition in enumerate(conditions):
            logger.info(f"Procesando condición {i+1}: {condition.type}")
            
            # Cargar datos del dataset de esta condición
            condition_df = load_ticks_by_dataset(condition.dataset_id)
            condition_df_filtered = filter_data_by_period(condition_df, period)
            
            if condition_df_filtered.empty:
                logger.warning(f"No hay datos para la condición {i+1} en el período {period}")
                continue
            
            # Aplicar transformaciones
            condition_df_transformed = apply_transformations(condition_df_filtered, condition.transform)
            
            # Generar señales para esta condición
            condition_signals = generate_signals(
                condition_df_transformed,
                condition.threshold_entry or 0.0,
                condition.threshold_exit or 0.0,
                condition.apply_to,
                condition.type,
                condition.crossover_strategy.dict() if condition.crossover_strategy else None,
                condition.multi_dataset_crossover_strategy.dict() if condition.multi_dataset_crossover_strategy else None,
                condition.bitcoin_price_condition.dict() if condition.bitcoin_price_condition else None,
                period
            )
            
            # Alinear índices (puede haber diferencias de timestamps entre datasets)
            aligned_signals = align_signals_to_base(condition_signals, base_df_filtered.index)
            
            # Combinar señales según la lógica
            if i == 0:
                # Primera condición: usar directamente
                signals_df['entries'] = aligned_signals['entries']
                signals_df['exits'] = aligned_signals['exits']
            else:
                # Condiciones subsiguientes: combinar según lógica
                if condition.logic == "AND":
                    signals_df['entries'] = signals_df['entries'] & aligned_signals['entries']
                    signals_df['exits'] = signals_df['exits'] & aligned_signals['exits']
                elif condition.logic == "OR":
                    signals_df['entries'] = signals_df['entries'] | aligned_signals['entries']
                    signals_df['exits'] = signals_df['exits'] | aligned_signals['exits']
        
        # Limpiar señales (no puede haber entrada y salida al mismo tiempo)
        signals_df.loc[signals_df['entries'] & signals_df['exits'], 'exits'] = False
        
        logger.info(f"Señales compuestas generadas: {signals_df['entries'].sum()} entradas, {signals_df['exits'].sum()} salidas")
        
        return signals_df
        
    except Exception as e:
        logger.error(f"Error generando señales compuestas: {str(e)}")
        raise e

def align_signals_to_base(signals_df: pd.DataFrame, base_index: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Alinea las señales de una condición al índice base del DataFrame principal.
    
    Args:
        signals_df: DataFrame con señales de la condición
        base_index: Índice temporal base
        
    Returns:
        DataFrame con señales alineadas
    """
    try:
        # Crear DataFrame con el índice base
        aligned_df = pd.DataFrame(index=base_index)
        aligned_df['entries'] = False
        aligned_df['exits'] = False
        
        # Reindexar señales al índice base, rellenando con False
        aligned_entries = signals_df['entries'].reindex(base_index, fill_value=False)
        aligned_exits = signals_df['exits'].reindex(base_index, fill_value=False)
        
        aligned_df['entries'] = aligned_entries
        aligned_df['exits'] = aligned_exits
        
        return aligned_df
        
    except Exception as e:
        logger.error(f"Error alineando señales: {str(e)}")
        raise e
