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
            
            # Convertir fechas
            trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date'])
            trades_df['exit_date'] = pd.to_datetime(trades_df['exit_date'])
            
            # Calcular retornos diarios
            daily_returns = []
            current_cash = initial_cash
            
            # Ordenar trades por fecha de entrada
            trades_df = trades_df.sort_values('entry_date')
            
            # Crear rango de fechas desde el primer trade hasta el último
            start_date = trades_df['entry_date'].min()
            end_date = trades_df['exit_date'].max()
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Para cada día, calcular el retorno basado en los trades activos
            for date in date_range:
                daily_return = 0.0
                
                # Buscar trades que estén activos en esta fecha
                active_trades = trades_df[
                    (trades_df['entry_date'] <= date) & 
                    (trades_df['exit_date'] >= date)
                ]
                
                if not active_trades.empty:
                    # Calcular retorno ponderado de todos los trades activos
                    total_pnl = active_trades['pnl'].sum()
                    total_invested = active_trades['size'].sum() * active_trades['entry_price'].mean()
                    
                    if total_invested > 0:
                        daily_return = total_pnl / total_invested
                
                daily_returns.append(daily_return)
            
            # Crear serie de retornos
            returns_series = pd.Series(daily_returns, index=date_range)
            
            logger.info(f"Serie de retornos generada: {len(returns_series)} días, desde {start_date} hasta {end_date}")
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
                    if pd.isna(value):
                        stats[metric_name] = None
                    elif isinstance(value, (np.integer, np.floating)):
                        stats[metric_name] = float(value)
                    else:
                        stats[metric_name] = value
                except Exception as e:
                    logger.warning(f"Error calculando métrica {metric_name}: {str(e)}")
                    stats[metric_name] = None
            
            # Añadir métricas que pueden requerir manejo especial
            try:
                stats['monthly_returns'] = qs.stats.monthly_returns(returns).to_dict()
            except Exception as e:
                logger.warning(f"Error calculando monthly_returns: {str(e)}")
                stats['monthly_returns'] = {}
            
            try:
                if hasattr(qs.stats, 'yearly_returns'):
                    stats['yearly_returns'] = qs.stats.yearly_returns(returns).to_dict()
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
                drawdown_details = qs.stats.drawdown_details(returns)
                
                # Convertir a formato serializable
                if isinstance(drawdown_details, pd.DataFrame):
                    drawdown_details = drawdown_details.to_dict('records')
                
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
                plots_data['rolling_sharpe'] = qs.stats.rolling_sharpe(returns).to_dict()
            except Exception as e:
                logger.warning(f"Error calculando rolling_sharpe: {str(e)}")
                plots_data['rolling_sharpe'] = {}
            
            try:
                plots_data['rolling_sortino'] = qs.stats.rolling_sortino(returns).to_dict()
            except Exception as e:
                logger.warning(f"Error calculando rolling_sortino: {str(e)}")
                plots_data['rolling_sortino'] = {}
            
            try:
                plots_data['rolling_volatility'] = qs.stats.rolling_volatility(returns).to_dict()
            except Exception as e:
                logger.warning(f"Error calculando rolling_volatility: {str(e)}")
                plots_data['rolling_volatility'] = {}
            
            try:
                plots_data['drawdown_series'] = qs.stats.to_drawdown_series(returns).to_dict()
            except Exception as e:
                logger.warning(f"Error calculando drawdown_series: {str(e)}")
                plots_data['drawdown_series'] = {}
            
            try:
                plots_data['monthly_returns_heatmap'] = qs.stats.monthly_returns(returns).to_dict()
            except Exception as e:
                logger.warning(f"Error calculando monthly_returns_heatmap: {str(e)}")
                plots_data['monthly_returns_heatmap'] = {}
            
            try:
                plots_data['distribution_stats'] = {
                    'mean': float(returns.mean()),
                    'std': float(returns.std()),
                    'skew': float(qs.stats.skew(returns)),
                    'kurtosis': float(qs.stats.kurtosis(returns))
                }
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
            
            logger.info(f"Reporte completo generado con {len(report_data)} secciones")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generando reporte completo: {str(e)}")
            raise e
