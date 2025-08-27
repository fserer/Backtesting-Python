import pandas as pd
import numpy as np
import vectorbt as vbt
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def run_backtest(
    df: pd.DataFrame,
    threshold_entry: float,
    threshold_exit: float,
    fees: float,
    slippage: float,
    init_cash: float,
    apply_to: str = "v",
    override_freq: Optional[str] = None,
    strategy_type: str = "threshold",
    crossover_strategy: dict = None,
    multi_dataset_crossover_strategy: dict = None,
    period: str = "all"
) -> Dict[str, Any]:
    """
    Ejecuta un backtest usando vectorbt.
    
    Args:
        df: DataFrame con columnas 't', 'v_transformed', 'usd_transformed'
        threshold_entry: Umbral de entrada
        threshold_exit: Umbral de salida
        fees: Comisiones (ej: 0.0005 = 0.05%)
        slippage: Slippage (ej: 0.0002 = 0.02%)
        init_cash: Capital inicial
        apply_to: A qué columna aplicar las señales ('v' o 'usd')
        override_freq: Frecuencia manual ('1D' o '1H')
        
    Returns:
        Dict con resultados del backtest
    """
    try:
        # Filtrar datos por período
        df_filtered = filter_data_by_period(df, period)
        
        if df_filtered.empty:
            raise ValueError(f"No hay datos disponibles para el período '{period}'")
        
        logger.info(f"Período seleccionado: {period} - {len(df_filtered)} registros de {len(df)} totales")
        
        # Determinar frecuencia
        freq = determine_frequency(df_filtered, override_freq)
        
        # Generar señales
        signals = generate_signals(df_filtered, threshold_entry, threshold_exit, apply_to, strategy_type, crossover_strategy, multi_dataset_crossover_strategy)
        
        # Preparar datos para vectorbt
        close_prices = df_filtered['usd_transformed'].values
        entries = signals['entries'].values
        exits = signals['exits'].values
        
        # Configurar parámetros de vectorbt
        vbt_settings = {
            'close': close_prices,
            'entries': entries,
            'exits': exits,
            'fees': fees,
            'slippage': slippage,
            'init_cash': init_cash,
            'freq': freq,
            'accumulate': False,
            'upon_long_conflict': 'ignore',
            'upon_short_conflict': 'ignore'
        }
        
        # Ejecutar backtest
        portfolio = vbt.Portfolio.from_signals(**vbt_settings)
        
        # Calcular métricas
        results = calculate_metrics(portfolio, df_filtered)
        
        logger.info(f"Backtest completado: {results['results']['trades']} trades, {results['results']['total_return']:.2%} retorno")
        
        return results
        
    except Exception as e:
        logger.error(f"Error en backtest: {str(e)}")
        raise e

def filter_data_by_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    Filtra los datos por el período especificado.
    
    Args:
        df: DataFrame con columna 't' (timestamp)
        period: Período a filtrar ('1w', '1m', '3m', '6m', '1y', 'ytd', '2y', '3y', '4y', '5y', '6y', '7y', '8y', '9y', '10y', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', 'all')
    
    Returns:
        DataFrame filtrado
    """
    if period == "all":
        return df
    
    # Obtener la fecha más reciente y asegurar tipo consistente
    latest_date = pd.to_datetime(df['t'].max())
    
    # Calcular la fecha de inicio según el período
    if period == "1w":
        start_date = latest_date - pd.Timedelta(days=7)
    elif period == "1m":
        start_date = latest_date - pd.Timedelta(days=30)
    elif period == "3m":
        start_date = latest_date - pd.Timedelta(days=90)
    elif period == "6m":
        start_date = latest_date - pd.Timedelta(days=180)
    elif period == "1y":
        start_date = latest_date - pd.Timedelta(days=365)
    elif period == "ytd":
        # Año hasta la fecha (desde el 1 de enero del año actual)
        start_date = pd.Timestamp(latest_date.year, 1, 1, tz=latest_date.tz)
    elif period == "2y":
        start_date = latest_date - pd.Timedelta(days=2*365)
    elif period == "3y":
        start_date = latest_date - pd.Timedelta(days=3*365)
    elif period == "4y":
        start_date = latest_date - pd.Timedelta(days=4*365)
    elif period == "5y":
        start_date = latest_date - pd.Timedelta(days=5*365)
    elif period == "6y":
        start_date = latest_date - pd.Timedelta(days=6*365)
    elif period == "7y":
        start_date = latest_date - pd.Timedelta(days=7*365)
    elif period == "8y":
        start_date = latest_date - pd.Timedelta(days=8*365)
    elif period == "9y":
        start_date = latest_date - pd.Timedelta(days=9*365)
    elif period == "10y":
        start_date = latest_date - pd.Timedelta(days=10*365)
    elif period in ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]:
        # Filtrar por año específico
        year = int(period)
        start_date = pd.Timestamp(year, 1, 1, tz=latest_date.tz)
        end_date = pd.Timestamp(year, 12, 31, 23, 59, 59, tz=latest_date.tz)
        
        # Filtrar datos por año específico
        filtered_df = df[(df['t'] >= start_date) & (df['t'] <= end_date)].copy()
        
        logger.info(f"Filtrado por año '{period}': {len(filtered_df)} registros desde {start_date.strftime('%Y-%m-%d')} hasta {end_date.strftime('%Y-%m-%d')}")
        
        return filtered_df
    else:
        return df
    
    # Filtrar datos
    filtered_df = df[df['t'] >= start_date].copy()
    
    logger.info(f"Filtrado por período '{period}': {len(filtered_df)} registros desde {start_date.strftime('%Y-%m-%d')} hasta {latest_date.strftime('%Y-%m-%d')}")
    
    return filtered_df

def determine_frequency(df: pd.DataFrame, override_freq: Optional[str] = None) -> str:
    """
    Determina la frecuencia de los datos.
    """
    if override_freq:
        return override_freq
    
    # Calcular diferencias de tiempo
    time_diffs = df['t'].diff().dropna()
    time_diffs_seconds = time_diffs.dt.total_seconds()
    
    if len(time_diffs_seconds) == 0:
        return '1H'
    
    # Calcular el delta modal
    mode_diff = time_diffs_seconds.mode().iloc[0]
    
    # Definir rangos de tolerancia (±5%)
    daily_range = (86400 * 0.95, 86400 * 1.05)
    hourly_range = (3600 * 0.95, 3600 * 1.05)
    
    if daily_range[0] <= mode_diff <= daily_range[1]:
        return '1D'
    elif hourly_range[0] <= mode_diff <= hourly_range[1]:
        return '1H'
    else:
        return '1H'  # Default

def determine_dataset_interval(df: pd.DataFrame) -> str:
    """
    Determina el intervalo del dataset para cálculo de duración.
    """
    # Calcular diferencias de tiempo
    time_diffs = df['t'].diff().dropna()
    time_diffs_seconds = time_diffs.dt.total_seconds()
    
    if len(time_diffs_seconds) == 0:
        return 'hour'
    
    # Calcular el delta modal
    mode_diff = time_diffs_seconds.mode().iloc[0]
    
    # Definir rangos de tolerancia (±5%)
    daily_range = (86400 * 0.95, 86400 * 1.05)  # ~24 horas
    hourly_range = (3600 * 0.95, 3600 * 1.05)   # ~1 hora
    block_range = (600 * 0.95, 600 * 1.05)      # ~10 minutos (bloque Bitcoin)
    
    if daily_range[0] <= mode_diff <= daily_range[1]:
        return 'day'
    elif hourly_range[0] <= mode_diff <= hourly_range[1]:
        return 'hour'
    elif block_range[0] <= mode_diff <= block_range[1]:
        return 'block'
    else:
        # Si no coincide con ningún patrón conocido, usar el valor en segundos
        return f'{int(mode_diff)}s'

def generate_signals(
    df: pd.DataFrame, 
    threshold_entry: float, 
    threshold_exit: float, 
    apply_to: str,
    strategy_type: str = "threshold",
    crossover_strategy: dict = None,
    multi_dataset_crossover_strategy: dict = None
) -> pd.DataFrame:
    """
    Genera señales de entrada y salida basadas en diferentes estrategias.
    
    Args:
        df: DataFrame con datos transformados
        threshold_entry: Umbral de entrada (solo para strategy_type="threshold")
        threshold_exit: Umbral de salida (solo para strategy_type="threshold")
        apply_to: Columna a usar para señales ('v' o 'usd')
        strategy_type: 'threshold', 'crossover', o 'multi_dataset_crossover'
        crossover_strategy: Configuración para estrategia de cruce
        multi_dataset_crossover_strategy: Configuración para cruce entre datasets
        
    Returns:
        DataFrame con columnas 'entries' y 'exits'
    """
    try:
        if strategy_type == "threshold":
            return generate_threshold_signals(df, threshold_entry, threshold_exit, apply_to)
        elif strategy_type == "crossover" and crossover_strategy:
            return generate_crossover_signals(df, apply_to, crossover_strategy)
        elif strategy_type == "multi_dataset_crossover" and multi_dataset_crossover_strategy:
            return generate_multi_dataset_crossover_signals(df, multi_dataset_crossover_strategy)
        else:
            raise ValueError(f"Estrategia no válida: {strategy_type}")
        
    except Exception as e:
        logger.error(f"Error generando señales: {str(e)}")
        raise e

def generate_threshold_signals(
    df: pd.DataFrame, 
    threshold_entry: float, 
    threshold_exit: float, 
    apply_to: str
) -> pd.DataFrame:
    """
    Genera señales basadas en cruces de umbral (estrategia original).
    """
    # Seleccionar columna para señales
    signal_column = f'{apply_to}_transformed'
    
    if signal_column not in df.columns:
        raise ValueError(f"Columna {signal_column} no encontrada")
    
    series = df[signal_column]
    
    # Debug: Verificar qué columna se está usando y sus valores
    logger.info(f"Generando señales de umbral:")
    logger.info(f"  - apply_to: {apply_to}")
    logger.info(f"  - signal_column: {signal_column}")
    logger.info(f"  - threshold_entry: {threshold_entry}")
    logger.info(f"  - threshold_exit: {threshold_exit}")
    logger.info(f"  - Series stats: min={series.min():.4f}, max={series.max():.4f}, mean={series.mean():.4f}")
    logger.info(f"  - Primeros 5 valores: {series.head().tolist()}")
    
    # Generar señales de entrada (crossover hacia abajo - compra cuando baja)
    entries = (
        (series.shift(1) > threshold_entry) & 
        (series <= threshold_entry)
    )
    
    # Generar señales de salida (crossover hacia arriba - vende cuando sube)
    exits = (
        (series.shift(1) < threshold_exit) & 
        (series >= threshold_exit)
    )
    
    # Crear DataFrame de señales
    signals = pd.DataFrame({
        'entries': entries,
        'exits': exits
    })
    
    # Rellenar NaN con False
    signals = signals.fillna(False)
    
    logger.info(f"Señales de umbral generadas: {signals['entries'].sum()} entradas, {signals['exits'].sum()} salidas")
    
    return signals

def generate_crossover_signals(df: pd.DataFrame, apply_to: str, crossover_strategy: dict) -> pd.DataFrame:
    """
    Genera señales basadas en cruces de medias móviles.
    
    Args:
        df: DataFrame con datos transformados
        apply_to: 'v' o 'usd'
        crossover_strategy: Configuración de la estrategia de cruce
    
    Returns:
        DataFrame con columnas 'entries', 'exits'
    """
    # Seleccionar columna para señales
    signal_column = f'{apply_to}_transformed'
    
    if signal_column not in df.columns:
        raise ValueError(f"Columna {signal_column} no encontrada")
    
    series = df[signal_column]
    
    # Calcular medias móviles para entrada
    if crossover_strategy['entry_type'] == 'sma':
        entry_fast = series.rolling(window=crossover_strategy['entry_fast_period'], min_periods=1).mean()
        entry_slow = series.rolling(window=crossover_strategy['entry_slow_period'], min_periods=1).mean()
    else:  # ema
        entry_fast = series.ewm(span=crossover_strategy['entry_fast_period']).mean()
        entry_slow = series.ewm(span=crossover_strategy['entry_slow_period']).mean()
    
    # Calcular medias móviles para salida
    if crossover_strategy['exit_type'] == 'sma':
        exit_fast = series.rolling(window=crossover_strategy['exit_fast_period'], min_periods=1).mean()
        exit_slow = series.rolling(window=crossover_strategy['exit_slow_period'], min_periods=1).mean()
    else:  # ema
        exit_fast = series.ewm(span=crossover_strategy['exit_fast_period']).mean()
        exit_slow = series.ewm(span=crossover_strategy['exit_slow_period']).mean()
    
    # Generar señales de entrada según la dirección configurada
    if crossover_strategy['entry_direction'] == 'up':
        # Cruce al alza: fast cruza por encima de slow
        entries = (entry_fast > entry_slow) & (entry_fast.shift(1) <= entry_slow.shift(1))
    else:
        # Cruce a la baja: fast cruza por debajo de slow
        entries = (entry_fast < entry_slow) & (entry_fast.shift(1) >= entry_slow.shift(1))
    
    # Generar señales de salida según la dirección configurada
    if crossover_strategy['exit_direction'] == 'up':
        # Cruce al alza: fast cruza por encima de slow
        exits = (exit_fast > exit_slow) & (exit_fast.shift(1) <= exit_slow.shift(1))
    else:
        # Cruce a la baja: fast cruza por debajo de slow
        exits = (exit_fast < exit_slow) & (exit_fast.shift(1) >= exit_slow.shift(1))
    
    # Crear DataFrame de señales
    signals = pd.DataFrame({
        'entries': entries,
        'exits': exits
    })
    
    # Rellenar NaN con False
    signals = signals.fillna(False)
    
    logger.info(f"Señales de cruce generadas: {signals['entries'].sum()} entradas, {signals['exits'].sum()} salidas")
    
    return signals

def calculate_metrics(portfolio: vbt.Portfolio, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula métricas del backtest.
    
    Args:
        portfolio: Objeto Portfolio de vectorbt
        df: DataFrame original con timestamps
        
    Returns:
        Dict con métricas y curva de equity
    """
    try:
        # Métricas básicas
        total_return = portfolio.total_return()
        sharpe_ratio = portfolio.sharpe_ratio()
        max_drawdown = portfolio.max_drawdown()
        trades_count = len(portfolio.trades.records_readable)
        
        
        
        # Información detallada de operaciones
        trades_data = []
        total_fees = 0.0
        total_funding_cost = 0.0
        funding_rate_annual = 11.6  # Tasa de funding anual en porcentaje
        
        if hasattr(portfolio.trades, 'records_readable') and len(portfolio.trades.records_readable) > 0:
            trades_df = portfolio.trades.records_readable
            
            # Debug: imprimir las columnas disponibles y datos completos
            logger.info(f"Columnas disponibles en trades: {list(trades_df.columns)}")
            logger.info(f"Shape de trades_df: {trades_df.shape}")
            logger.info(f"Primera fila de trades: {trades_df.iloc[0].to_dict()}")
            logger.info(f"Todas las filas de trades:")
            for i, row in trades_df.iterrows():
                logger.info(f"Trade {i}: {row.to_dict()}")
            
            for idx, trade in trades_df.iterrows():
                try:
                    # Obtener índices de entrada y salida - usar los nombres correctos de vectorbt
                    entry_idx = int(trade.get('Entry Timestamp', trade.get('entry_timestamp', 0)))
                    exit_idx = int(trade.get('Exit Timestamp', trade.get('exit_timestamp', 0)))
                    
                    logger.info(f"Procesando trade {idx}: entry_idx={entry_idx}, exit_idx={exit_idx}")
                    logger.info(f"DataFrame length: {len(df)}")
                    
                    # Obtener timestamps
                    if entry_idx < len(df) and exit_idx < len(df):
                        entry_timestamp = df['t'].iloc[entry_idx].isoformat()
                        exit_timestamp = df['t'].iloc[exit_idx].isoformat()
                        logger.info(f"Timestamps: entry={entry_timestamp}, exit={exit_timestamp}")
                    else:
                        entry_timestamp = None
                        exit_timestamp = None
                        logger.warning(f"Índices fuera de rango: entry_idx={entry_idx}, exit_idx={exit_idx}, df_length={len(df)}")
                    
                    # Usar los precios promedio de vectorbt en lugar de los del DataFrame
                    entry_price = float(trade.get('Avg Entry Price', trade.get('avg_entry_price', 0)))
                    exit_price = float(trade.get('Avg Exit Price', trade.get('avg_exit_price', 0)))
                    
                    logger.info(f"Precios vectorbt: entry={entry_price}, exit={exit_price}")
                    
                    # Calcular duración en períodos
                    duration_periods = exit_idx - entry_idx if entry_idx < len(df) and exit_idx < len(df) else 0
                    
                    entry_fees = float(trade.get('Entry Fees', trade.get('entry_fees', 0)))
                    exit_fees = float(trade.get('Exit Fees', trade.get('exit_fees', 0)))
                    total_fees += entry_fees + exit_fees
                    
                    # Calcular funding cost
                    if entry_timestamp and exit_timestamp and trade.get('Size', trade.get('size', 0)) > 0:
                        try:
                            entry_date = pd.to_datetime(entry_timestamp)
                            exit_date = pd.to_datetime(exit_timestamp)
                            duration_days = (exit_date - entry_date).total_seconds() / (24 * 3600)
                            
                            # Calcular valor de la posición (tamaño * precio de entrada)
                            position_value = float(trade.get('Size', trade.get('size', 0))) * entry_price
                            
                            # Calcular coste de funding (valor * tasa anual * días / 365)
                            funding_cost = position_value * (funding_rate_annual / 100) * (duration_days / 365)
                            total_funding_cost += funding_cost
                        except Exception as e:
                            logger.warning(f"Error calculando funding cost para trade {idx}: {e}")
                    
                    trades_data.append({
                        'entry_date': entry_timestamp,
                        'exit_date': exit_timestamp,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'size': float(trade.get('Size', trade.get('size', 0))),
                        'pnl': float(trade.get('PnL', trade.get('pnl', 0))),
                        'return_pct': float(trade.get('Return', trade.get('return', 0))),
                        'duration': duration_periods,
                        'entry_fees': entry_fees,
                        'exit_fees': exit_fees
                    })
                except Exception as e:
                    logger.error(f"Error procesando trade {idx}: {str(e)}")
                    logger.error(f"Datos del trade: {trade.to_dict()}")
                    continue
        
        # Curva de equity
        equity_curve = portfolio.value()
        equity_data = []
        
        # Alinear timestamps con equity curve
        timestamps = df['t'].iloc[:len(equity_curve)].tolist()
        
        for i, (timestamp, equity) in enumerate(zip(timestamps, equity_curve)):
            equity_data.append({
                'timestamp': timestamp.isoformat(),
                'equity': float(equity)
            })
        
        # Determinar frecuencia para respuesta
        freq = determine_frequency(df)
        
        # Determinar intervalo del dataset para cálculo de duración
        dataset_interval = determine_dataset_interval(df)
        logger.info(f"🔍 Dataset interval detectado: {dataset_interval}")
        logger.info(f"🔍 Frecuencia detectada: {freq}")
        
        # Manejar valores infinitos y NaN
        def safe_float(value):
            if pd.isna(value) or np.isinf(value):
                return 0.0
            return float(value)
        
        results = {
            'results': {
                'total_return': safe_float(total_return),
                'sharpe': safe_float(sharpe_ratio),
                'max_drawdown': safe_float(max_drawdown),
                'trades': int(trades_count)
            },
            'equity': equity_data,
            'trades': trades_data,
            'total_fees': total_fees,
            'funding_cost': {
                'totalFundingCost': total_funding_cost
            },
            'freq': freq,
            'dataset_interval': dataset_interval
        }
        
        logger.info(f"🔍 Resultados finales - dataset_interval: {results.get('dataset_interval')}")
        logger.info(f"🔍 Claves en results: {list(results.keys())}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error calculando métricas: {str(e)}")
        raise e

def validate_backtest_params(
    threshold_entry: float,
    threshold_exit: float,
    fees: float,
    slippage: float,
    init_cash: float
) -> None:
    """
    Valida los parámetros del backtest.
    """
    if fees < 0 or fees > 0.1:
        raise ValueError("Fees debe estar entre 0 y 0.1 (10%)")
    
    if slippage < 0 or slippage > 0.1:
        raise ValueError("Slippage debe estar entre 0 y 0.1 (10%)")
    
    if init_cash <= 0:
        raise ValueError("Capital inicial debe ser positivo")
    
    # Los thresholds pueden ser cualquier valor numérico
    if not isinstance(threshold_entry, (int, float)) or not isinstance(threshold_exit, (int, float)):
        raise ValueError("Los thresholds deben ser valores numéricos")

def generate_multi_dataset_crossover_signals(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """
    Genera señales basadas en cruces entre indicadores de diferentes datasets.
    
    Args:
        df: DataFrame con datos del dataset principal (para timestamps y precio)
        strategy: Configuración de la estrategia multi-dataset
        
    Returns:
        DataFrame con columnas 'entries' y 'exits'
    """
    try:
        # Esta función será llamada desde el endpoint que maneja múltiples datasets
        # Por ahora, retornamos señales vacías ya que necesitamos acceso a múltiples datasets
        logger.info("Función multi-dataset crossover llamada - requiere implementación en endpoint")
        
        # Crear señales vacías del mismo tamaño que el DataFrame
        signals = pd.DataFrame({
            'entries': [False] * len(df),
            'exits': [False] * len(df)
        })
        
        return signals
        
    except Exception as e:
        logger.error(f"Error en multi-dataset crossover: {str(e)}")
        raise e

def run_multi_dataset_backtest(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    price_df: pd.DataFrame,
    strategy: dict,
    fees: float,
    slippage: float,
    init_cash: float,
    period: str = "all"
) -> Dict[str, Any]:
    """
    Ejecuta un backtest usando cruces entre indicadores de diferentes datasets.
    
    Args:
        df1: DataFrame del primer dataset
        df2: DataFrame del segundo dataset  
        price_df: DataFrame para precios (puede ser df1, df2, o un tercer dataset)
        strategy: Configuración de la estrategia multi-dataset
        fees: Comisiones
        slippage: Slippage
        init_cash: Capital inicial
        period: Período a filtrar
        
    Returns:
        Dict con resultados del backtest
    """
    try:
        # Filtrar datos por período
        df1_filtered = filter_data_by_period(df1, period)
        df2_filtered = filter_data_by_period(df2, period)
        price_df_filtered = filter_data_by_period(price_df, period)
        
        if df1_filtered.empty or df2_filtered.empty or price_df_filtered.empty:
            raise ValueError(f"No hay datos disponibles para el período '{period}'")
        
        logger.info(f"Período seleccionado: {period} - Datasets: {len(df1_filtered)}, {len(df2_filtered)}, {len(price_df_filtered)} registros")
        
        # Determinar frecuencia
        freq = determine_frequency(price_df_filtered)
        
        # Generar señales de cruce entre datasets
        signals = generate_multi_dataset_crossover_signals_impl(
            df1_filtered, df2_filtered, price_df_filtered, strategy
        )
        
        # Alinear todos los arrays al mismo tamaño (usar el más pequeño)
        min_length = min(len(price_df_filtered), len(signals))
        
        # Preparar datos para vectorbt (alineados)
        close_prices = price_df_filtered['usd'].values[:min_length]
        entries = signals['entries'].values[:min_length]
        exits = signals['exits'].values[:min_length]
        
        logger.info(f"Datos alineados: {min_length} registros para vectorbt")
        
        # Configurar parámetros de vectorbt
        vbt_settings = {
            'close': close_prices,
            'entries': entries,
            'exits': exits,
            'fees': fees,
            'slippage': slippage,
            'init_cash': init_cash,
            'freq': freq,
            'accumulate': False,
            'upon_long_conflict': 'ignore',
            'upon_short_conflict': 'ignore'
        }
        
        # Ejecutar backtest
        portfolio = vbt.Portfolio.from_signals(**vbt_settings)
        
        # Calcular métricas usando el DataFrame alineado
        price_df_aligned = price_df_filtered.iloc[:min_length]
        results = calculate_metrics(portfolio, price_df_aligned)
        
        logger.info(f"Multi-dataset backtest completado: {results['results']['trades']} trades, {results['results']['total_return']:.2%} retorno")
        
        return results
        
    except Exception as e:
        logger.error(f"Error en multi-dataset backtest: {str(e)}")
        raise e

def generate_multi_dataset_crossover_signals_impl(
    df1: pd.DataFrame, 
    df2: pd.DataFrame, 
    price_df: pd.DataFrame,
    strategy: dict
) -> pd.DataFrame:
    """
    Implementación real de señales de cruce entre datasets.
    
    Args:
        df1: DataFrame del primer dataset
        df2: DataFrame del segundo dataset
        strategy: Configuración de la estrategia
        
    Returns:
        DataFrame con columnas 'entries' y 'exits'
    """
    try:
        # Extraer configuración
        dataset1_indicator = strategy['dataset1_indicator']  # 'v' o 'usd'
        dataset1_ma_type = strategy['dataset1_ma_type']      # 'sma' o 'ema'
        dataset1_ma_period = strategy['dataset1_ma_period']
        
        dataset2_indicator = strategy['dataset2_indicator']  # 'v' o 'usd'
        dataset2_ma_type = strategy['dataset2_ma_type']      # 'sma' o 'ema'
        dataset2_ma_period = strategy['dataset2_ma_period']
        
        entry_direction = strategy['entry_direction']        # 'up' o 'down'
        exit_direction = strategy['exit_direction']          # 'up' o 'down'
        
        # Calcular medias móviles para dataset 1
        series1 = df1[dataset1_indicator]
        if dataset1_ma_type == 'sma':
            ma1 = series1.rolling(window=dataset1_ma_period).mean()
        else:  # ema
            ma1 = series1.ewm(span=dataset1_ma_period).mean()
        
        # Calcular medias móviles para dataset 2
        series2 = df2[dataset2_indicator]
        if dataset2_ma_type == 'sma':
            ma2 = series2.rolling(window=dataset2_ma_period).mean()
        else:  # ema
            ma2 = series2.ewm(span=dataset2_ma_period).mean()
        
        # Alinear los datos por timestamp
        # Usar el mínimo de ambos datasets
        min_len = min(len(ma1), len(ma2))
        ma1_aligned = ma1.iloc[:min_len]
        ma2_aligned = ma2.iloc[:min_len]
        
        logger.info(f"Medias móviles alineadas: {min_len} períodos")
        logger.info(f"Dataset 1 MA: {dataset1_ma_type}({dataset1_ma_period}) - {dataset1_indicator}")
        logger.info(f"Dataset 2 MA: {dataset2_ma_type}({dataset2_ma_period}) - {dataset2_indicator}")
        
        # Generar señales de entrada según la dirección configurada
        if entry_direction == 'up':
            # Cruce al alza: ma1 cruza por encima de ma2
            entries = (ma1_aligned > ma2_aligned) & (ma1_aligned.shift(1) <= ma2_aligned.shift(1))
        else:
            # Cruce a la baja: ma1 cruza por debajo de ma2
            entries = (ma1_aligned < ma2_aligned) & (ma1_aligned.shift(1) >= ma2_aligned.shift(1))
        
        # Generar señales de salida según la dirección configurada
        if exit_direction == 'up':
            # Cruce al alza: ma1 cruza por encima de ma2
            exits = (ma1_aligned > ma2_aligned) & (ma1_aligned.shift(1) <= ma2_aligned.shift(1))
        else:
            # Cruce a la baja: ma1 cruza por debajo de ma2
            exits = (ma1_aligned < ma2_aligned) & (ma1_aligned.shift(1) >= ma2_aligned.shift(1))
        
        # Aplicar Take Profit y Stop Loss si están habilitados
        if strategy.get('use_take_profit', False) or strategy.get('use_stop_loss', False):
            exits = apply_take_profit_stop_loss(
                price_df, entries, exits, strategy
            )
        
        # Crear DataFrame de señales
        signals = pd.DataFrame({
            'entries': entries,
            'exits': exits
        })
        
        # Rellenar NaN con False
        signals = signals.fillna(False)
        
        logger.info(f"Señales multi-dataset generadas: {signals['entries'].sum()} entradas, {signals['exits'].sum()} salidas")
        
        return signals
        
    except Exception as e:
        logger.error(f"Error generando señales multi-dataset: {str(e)}")
        raise e

def apply_take_profit_stop_loss(
    price_df: pd.DataFrame,
    entries: pd.Series,
    exits: pd.Series,
    strategy: dict
) -> pd.Series:
    """
    Aplica lógica de Take Profit y Stop Loss basada en porcentajes del precio de entrada.
    
    Args:
        price_df: DataFrame con precios USD
        entries: Serie de señales de entrada
        exits: Serie de señales de salida originales
        strategy: Configuración de la estrategia con TP/SL
        
    Returns:
        Serie de señales de salida modificada con TP/SL
    """
    try:
        prices = price_df['usd'].values
        take_profit_pct = strategy.get('take_profit_pct', 3.0) / 100.0
        stop_loss_pct = strategy.get('stop_loss_pct', 1.0) / 100.0
        use_take_profit = strategy.get('use_take_profit', True)
        use_stop_loss = strategy.get('use_stop_loss', True)
        
        # Crear copia de las señales de salida
        modified_exits = exits.copy()
        
        # Encontrar posiciones de entrada (usar índices relativos)
        entry_positions = entries[entries == True].index.tolist()
        
        logger.info(f"Aplicando TP/SL: {len(entry_positions)} entradas, TP: {take_profit_pct*100}%, SL: {stop_loss_pct*100}%")
        
        for entry_idx in entry_positions:
            # Convertir índice del DataFrame a índice del array
            entry_array_idx = entries.index.get_loc(entry_idx)
            entry_price = prices[entry_array_idx]
            
            # Buscar la siguiente señal de salida después de esta entrada
            next_exit_mask = exits[entry_idx:].index[exits[entry_idx:] == True]
            
            if len(next_exit_mask) == 0:
                # No hay señal de salida, usar TP/SL hasta el final
                start_array_idx = entry_array_idx + 1
                end_array_idx = len(prices)
            else:
                # Hay señal de salida, usar TP/SL hasta esa señal
                next_exit_idx = next_exit_mask[0]
                next_exit_array_idx = exits.index.get_loc(next_exit_idx)
                start_array_idx = entry_array_idx + 1
                end_array_idx = next_exit_array_idx
            
            # Verificar TP/SL en cada período después de la entrada
            for i in range(start_array_idx, end_array_idx):
                if i >= len(prices):
                    break
                    
                current_price = prices[i]
                price_change_pct = (current_price - entry_price) / entry_price
                
                # Take Profit
                if use_take_profit and price_change_pct >= take_profit_pct:
                    # Convertir índice del array de vuelta al índice del DataFrame
                    array_to_df_idx = entries.index[i]
                    modified_exits.loc[array_to_df_idx] = True
                    logger.debug(f"Take Profit activado en posición {i}: {price_change_pct*100:.2f}%")
                    break
                
                # Stop Loss
                if use_stop_loss and price_change_pct <= -stop_loss_pct:
                    # Convertir índice del array de vuelta al índice del DataFrame
                    array_to_df_idx = entries.index[i]
                    modified_exits.loc[array_to_df_idx] = True
                    logger.debug(f"Stop Loss activado en posición {i}: {price_change_pct*100:.2f}%")
                    break
        
        tp_exits = (modified_exits & ~exits).sum()
        sl_exits = (modified_exits & ~exits).sum()
        logger.info(f"TP/SL aplicado: {tp_exits} salidas por TP, {sl_exits} salidas por SL")
        
        return modified_exits
        
    except Exception as e:
        logger.error(f"Error aplicando TP/SL: {str(e)}")
        raise e


