import pandas as pd
import numpy as np
import quantstats as qs
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QuantStatsService:
    """
    Servicio para generar análisis de QuantStats basado en los trades del backtesting.
    """
    
    def __init__(self):
        # Extender pandas con funcionalidades de QuantStats
        qs.extend_pandas()
    
    def _clean_json_value(self, value):
        """
        Limpia un valor para que sea JSON serializable.
        
        Args:
            value: Valor a limpiar
            
        Returns:
            Valor limpio o None si no es válido
        """
        try:
            if value is None:
                return None
            elif isinstance(value, dict):
                cleaned_dict = {}
                for k, v in value.items():
                    cleaned_v = self._clean_json_value(v)
                    # Incluir todos los valores, incluso None, para mantener la estructura
                    cleaned_dict[k] = cleaned_v
                return cleaned_dict
            elif isinstance(value, list):
                cleaned_list = []
                for v in value:
                    cleaned_v = self._clean_json_value(v)
                    # Incluir todos los valores, incluso None, para mantener la estructura
                    cleaned_list.append(cleaned_v)
                return cleaned_list
            elif isinstance(value, (str, bool)):
                return value
            elif isinstance(value, (np.integer, np.floating)):
                float_value = float(value)
                if np.isfinite(float_value) and -1e308 <= float_value <= 1e308:
                    return float_value
                else:
                    return None
            elif pd.isna(value) or np.isinf(value):
                return None
            elif hasattr(value, 'item'):  # Para numpy scalars
                return self._clean_json_value(value.item())
            else:
                # Para otros tipos, intentar convertir a string
                return str(value)
        except Exception as e:
            logger.warning(f"Error limpiando valor JSON: {str(e)}, valor: {value}")
            return None
    
    def generate_returns_series(self, trades: List[Dict], initial_cash: float = 10000.0) -> pd.Series:
        """
        Convierte los trades en una serie de retornos diarios para QuantStats.
        
        Args:
            trades: Lista de trades del backtesting
            initial_cash: Capital inicial
            
        Returns:
            Serie de retornos diarios
        """
        try:
            if not trades:
                logger.warning("No hay trades para generar serie de retornos")
                return pd.Series(dtype=float)
            
            # Crear DataFrame de trades
            trades_df = pd.DataFrame(trades)
            
            # Log para debug
            logger.info(f"Columnas en trades_df: {trades_df.columns.tolist()}")
            logger.info(f"Primer trade: {trades_df.iloc[0].to_dict()}")
            
            # Convertir fechas
            trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date'])
            trades_df['exit_date'] = pd.to_datetime(trades_df['exit_date'])
            
            # Ordenar trades por fecha de entrada
            trades_df = trades_df.sort_values('entry_date')
            
            # Crear rango de fechas desde el primer trade hasta el último
            start_date = trades_df['entry_date'].min()
            end_date = trades_df['exit_date'].max()
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Inicializar serie de retornos con ceros
            returns_series = pd.Series(0.0, index=date_range)
            
            # Crear retornos diarios basados en el equity curve real
            # Cada trade se registra en su día de salida con su retorno real
            for _, trade in trades_df.iterrows():
                exit_date = trade['exit_date']
                if exit_date in returns_series.index:
                    # Usar el retorno real del trade
                    if 'return_pct' in trade:
                        trade_return = trade['return_pct']
                    else:
                        trade_return = trade['pnl'] / initial_cash
                    
                    # Asignar el retorno completo en el día de salida
                    # IMPORTANTE: Usar .loc para asignar correctamente
                    returns_series.loc[exit_date] = trade_return
            
            # Limpiar valores extremos
            returns_series = returns_series.replace([np.inf, -np.inf], np.nan)
            returns_series = returns_series.fillna(0.0)
            
            # Verificar que los valores sean razonables (entre -1 y 1)
            returns_series = returns_series.clip(-1.0, 1.0)
            
            logger.info(f"Serie de retornos generada: {len(returns_series)} días, desde {start_date} hasta {end_date}")
            logger.info(f"Retornos: min={returns_series.min():.6f}, max={returns_series.max():.6f}, mean={returns_series.mean():.6f}")
            
            # Calcular retorno total acumulado para verificar
            total_return = (1 + returns_series).prod() - 1
            logger.info(f"Retorno total acumulado: {total_return:.6f} ({total_return*100:.2f}%)")
            
            # Verificar con los trades originales
            if 'return_pct' in trades_df.columns:
                trades_total_return = trades_df['return_pct'].sum()
                logger.info(f"Retorno total de trades: {trades_total_return:.6f} ({trades_total_return*100:.2f}%)")
            
            # Log adicional para verificar los trades individuales
            logger.info(f"Trades individuales:")
            for i, trade in trades_df.iterrows():
                logger.info(f"  Trade {i+1}: {trade['return_pct']:.4f} ({trade['return_pct']*100:.2f}%)")
            
            return returns_series
            
        except Exception as e:
            logger.error(f"Error generando serie de retornos: {str(e)}")
            raise e
    
    def get_basic_stats(self, returns: pd.Series) -> Dict:
        """
        Obtiene métricas básicas de rendimiento usando QuantStats.
        
        Args:
            returns: Serie de retornos diarios
            
        Returns:
            Diccionario con métricas básicas
        """
        try:
            if returns.empty:
                return {}
            
            # Definir las métricas que queremos calcular con manejo de errores
            metrics_to_calculate = {
                'total_return': lambda: qs.stats.cagr(returns),
                'sharpe_ratio': lambda: qs.stats.sharpe(returns),
                'sortino_ratio': lambda: qs.stats.sortino(returns),
                'max_drawdown': lambda: qs.stats.max_drawdown(returns),
                'volatility': lambda: qs.stats.volatility(returns),
                'win_rate': lambda: qs.stats.win_rate(returns),
                'profit_factor': lambda: qs.stats.profit_factor(returns),
                'calmar_ratio': lambda: qs.stats.calmar(returns),
                'skewness': lambda: qs.stats.skew(returns),
                'kurtosis': lambda: qs.stats.kurtosis(returns),
                'var_95': lambda: qs.stats.var(returns, 0.95),
                'cvar_95': lambda: qs.stats.cvar(returns, 0.95),
                'ulcer_index': lambda: qs.stats.ulcer_index(returns),
                'gain_to_pain_ratio': lambda: qs.stats.gain_to_pain_ratio(returns),
                'best_day': lambda: qs.stats.best(returns),
                'worst_day': lambda: qs.stats.worst(returns),
                'avg_win': lambda: qs.stats.avg_win(returns),
                'avg_loss': lambda: qs.stats.avg_loss(returns),
                'consecutive_wins': lambda: qs.stats.consecutive_wins(returns),
                'consecutive_losses': lambda: qs.stats.consecutive_losses(returns),
                'exposure_time': lambda: qs.stats.exposure(returns),
                'recovery_factor': lambda: qs.stats.recovery_factor(returns),
                'risk_of_ruin': lambda: qs.stats.risk_of_ruin(returns),
                'tail_ratio': lambda: qs.stats.tail_ratio(returns),
                'common_sense_ratio': lambda: qs.stats.common_sense_ratio(returns),
                'outlier_win_ratio': lambda: qs.stats.outlier_win_ratio(returns),
                'outlier_loss_ratio': lambda: qs.stats.outlier_loss_ratio(returns),
                'payoff_ratio': lambda: qs.stats.payoff_ratio(returns),
                'profit_ratio': lambda: qs.stats.profit_ratio(returns),
                'win_loss_ratio': lambda: qs.stats.win_loss_ratio(returns),
                'expected_return': lambda: qs.stats.expected_return(returns),
                'expected_shortfall': lambda: qs.stats.expected_shortfall(returns),
                'kelly_criterion': lambda: qs.stats.kelly_criterion(returns),
                'rar': lambda: qs.stats.rar(returns),
                'ror': lambda: qs.stats.ror(returns),
                'ghpr': lambda: qs.stats.ghpr(returns),
                'adjusted_sortino': lambda: qs.stats.adjusted_sortino(returns),
                'ulcer_performance_index': lambda: qs.stats.ulcer_performance_index(returns),
                'cpc_index': lambda: qs.stats.cpc_index(returns),
                'comp': lambda: qs.stats.comp(returns),
                'compsum': lambda: qs.stats.compsum(returns),
                'geometric_mean': lambda: qs.stats.geometric_mean(returns)
            }
            
            stats = {}
            
            # Calcular cada métrica con manejo de errores individual
            for metric_name, metric_func in metrics_to_calculate.items():
                try:
                    value = metric_func()
                    stats[metric_name] = self._clean_json_value(value)
                except Exception as e:
                    logger.warning(f"Error calculando métrica {metric_name}: {str(e)}")
                    stats[metric_name] = None
            
            # Añadir métricas que pueden requerir manejo especial
            try:
                monthly_returns = qs.stats.monthly_returns(returns)
                if monthly_returns is not None and not monthly_returns.empty:
                    stats['monthly_returns'] = self._clean_json_value(monthly_returns.to_dict())
                else:
                    stats['monthly_returns'] = {}
            except Exception as e:
                logger.warning(f"Error calculando monthly_returns: {str(e)}")
                stats['monthly_returns'] = {}
            
            try:
                if hasattr(qs.stats, 'yearly_returns'):
                    yearly_returns = qs.stats.yearly_returns(returns)
                    if yearly_returns is not None and not yearly_returns.empty:
                        stats['yearly_returns'] = self._clean_json_value(yearly_returns.to_dict())
                    else:
                        stats['yearly_returns'] = {}
                else:
                    stats['yearly_returns'] = {}
            except Exception as e:
                logger.warning(f"Error calculando yearly_returns: {str(e)}")
                stats['yearly_returns'] = {}
            
            logger.info(f"Métricas básicas calculadas: {len(stats)} métricas")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculando métricas básicas: {str(e)}")
            raise e
    
    def get_drawdown_details(self, returns: pd.Series) -> Dict:
        """
        Obtiene detalles de los drawdowns usando QuantStats.
        
        Args:
            returns: Serie de retornos diarios
            
        Returns:
            Diccionario con detalles de drawdowns
        """
        try:
            if returns.empty:
                return {}
            
            try:
                # Verificar que tenemos suficientes datos para calcular drawdowns
                if returns.empty or len(returns) < 2:
                    logger.warning("No hay suficientes datos para calcular drawdowns")
                    return {'drawdown_details': []}
                
                # Filtrar valores NaN antes de calcular drawdowns
                clean_returns = returns.replace([np.inf, -np.inf], np.nan).fillna(0.0)
                
                # Verificar que tenemos datos válidos
                if clean_returns.sum() == 0:
                    logger.warning("Todos los retornos son cero, no se pueden calcular drawdowns")
                    return {'drawdown_details': []}
                
                # Calcular drawdowns manualmente (QuantStats tiene problemas con nuestros datos)
                logger.info("Calculando drawdowns manualmente")
                cumulative_returns = (1 + clean_returns).cumprod()
                running_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - running_max) / running_max
                
                # Encontrar períodos de drawdown
                drawdown_periods = []
                in_drawdown = False
                start_idx = None
                
                for i, dd in enumerate(drawdown):
                    if dd < 0 and not in_drawdown:
                        in_drawdown = True
                        start_idx = i
                    elif dd >= 0 and in_drawdown:
                        in_drawdown = False
                        if start_idx is not None:
                            period = {
                                'start': clean_returns.index[start_idx].strftime('%Y-%m-%d'),
                                'valley': clean_returns.index[drawdown[start_idx:i].idxmin()].strftime('%Y-%m-%d'),
                                'end': clean_returns.index[i-1].strftime('%Y-%m-%d'),
                                'days': i - start_idx,
                                'max drawdown': float(drawdown[start_idx:i].min()),
                                '99% max drawdown': None
                            }
                            drawdown_periods.append(period)
                
                # Si aún estamos en drawdown al final, añadir el período final
                if in_drawdown and start_idx is not None:
                    period = {
                        'start': clean_returns.index[start_idx].strftime('%Y-%m-%d'),
                        'valley': clean_returns.index[drawdown[start_idx:].idxmin()].strftime('%Y-%m-%d'),
                        'end': clean_returns.index[-1].strftime('%Y-%m-%d'),
                        'days': len(drawdown) - start_idx,
                        'max drawdown': float(drawdown[start_idx:].min()),
                        '99% max drawdown': None
                    }
                    drawdown_periods.append(period)
                
                drawdown_details = drawdown_periods
                
                # Convertir a formato serializable
                if isinstance(drawdown_details, pd.DataFrame):
                    drawdown_details = drawdown_details.to_dict('records')
                
                # Limpiar valores NaN en los drawdowns
                if isinstance(drawdown_details, list):
                    for drawdown in drawdown_details:
                        for key, value in drawdown.items():
                            if pd.isna(value) or np.isinf(value):
                                drawdown[key] = None
                
                logger.info(f"Detalles de drawdown calculados: {len(drawdown_details) if isinstance(drawdown_details, list) else 1} períodos")
                return {'drawdown_details': drawdown_details}
            except Exception as e:
                logger.warning(f"Error calculando drawdown_details: {str(e)}")
                return {'drawdown_details': []}
            
        except Exception as e:
            logger.error(f"Error calculando detalles de drawdown: {str(e)}")
            raise e
    
    def generate_plots_data(self, returns: pd.Series) -> Dict:
        """
        Genera datos para las visualizaciones de QuantStats.
        
        Args:
            returns: Serie de retornos diarios
            
        Returns:
            Diccionario con datos para plots
        """
        try:
            if returns.empty:
                return {}
            
            plots_data = {}
            
            # Calcular cada tipo de plot con manejo de errores individual
            try:
                plots_data['rolling_sharpe'] = self._clean_json_value(qs.stats.rolling_sharpe(returns).to_dict())
            except Exception as e:
                logger.warning(f"Error calculando rolling_sharpe: {str(e)}")
                plots_data['rolling_sharpe'] = {}
            
            try:
                plots_data['rolling_sortino'] = self._clean_json_value(qs.stats.rolling_sortino(returns).to_dict())
            except Exception as e:
                logger.warning(f"Error calculando rolling_sortino: {str(e)}")
                plots_data['rolling_sortino'] = {}
            
            try:
                plots_data['rolling_volatility'] = self._clean_json_value(qs.stats.rolling_volatility(returns).to_dict())
            except Exception as e:
                logger.warning(f"Error calculando rolling_volatility: {str(e)}")
                plots_data['rolling_volatility'] = {}
            
            try:
                plots_data['drawdown_series'] = self._clean_json_value(qs.stats.to_drawdown_series(returns).to_dict())
            except Exception as e:
                logger.warning(f"Error calculando drawdown_series: {str(e)}")
                plots_data['drawdown_series'] = {}
            
            try:
                plots_data['monthly_returns_heatmap'] = self._clean_json_value(qs.stats.monthly_returns(returns).to_dict())
            except Exception as e:
                logger.warning(f"Error calculando monthly_returns_heatmap: {str(e)}")
                plots_data['monthly_returns_heatmap'] = {}
            
            try:
                plots_data['distribution_stats'] = self._clean_json_value({
                    'mean': returns.mean(),
                    'std': returns.std(),
                    'skew': qs.stats.skew(returns),
                    'kurtosis': qs.stats.kurtosis(returns)
                })
            except Exception as e:
                logger.warning(f"Error calculando distribution_stats: {str(e)}")
                plots_data['distribution_stats'] = {
                    'mean': None,
                    'std': None,
                    'skew': None,
                    'kurtosis': None
                }
            
            logger.info(f"Datos de plots generados: {len(plots_data)} tipos de visualización")
            return plots_data
            
        except Exception as e:
            logger.error(f"Error generando datos de plots: {str(e)}")
            raise e
    
    def generate_full_report(self, returns: pd.Series, benchmark_returns: Optional[pd.Series] = None) -> Dict:
        """
        Genera un reporte completo usando QuantStats.
        
        Args:
            returns: Serie de retornos diarios
            benchmark_returns: Serie de retornos del benchmark (opcional)
            
        Returns:
            Diccionario con reporte completo
        """
        try:
            if returns.empty:
                return {}
            
            # Generar reporte completo
            report_data = {
                'basic_stats': self.get_basic_stats(returns),
                'drawdown_details': self.get_drawdown_details(returns),
                'plots_data': self.generate_plots_data(returns)
            }
            
            # Si hay benchmark, añadir comparaciones
            if benchmark_returns is not None and not benchmark_returns.empty:
                report_data['benchmark_comparison'] = {
                    'information_ratio': qs.stats.information_ratio(returns, benchmark_returns),
                    'beta': qs.stats.beta(returns, benchmark_returns),
                    'alpha': qs.stats.alpha(returns, benchmark_returns),
                    'correlation': qs.stats.correlation(returns, benchmark_returns),
                    'r_squared': qs.stats.r_squared(returns, benchmark_returns)
                }
            
            # No aplicar limpieza al reporte completo, ya se aplicó a cada sección individualmente
            logger.info(f"Reporte completo generado con {len(report_data)} secciones")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generando reporte completo: {str(e)}")
            raise e
