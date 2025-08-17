import pandas as pd
import numpy as np
import pyfolio as pf
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PyfolioService:
    """
    Servicio para generar análisis de trades usando pyfolio.
    """
    
    def __init__(self):
        """Inicializa el servicio de pyfolio."""
        logger.info("Inicializando servicio Pyfolio")
    
    def generate_returns_series(self, trades: List[Dict], initial_cash: float = 10000.0) -> pd.Series:
        """
        Convierte los trades en una serie de retornos diarios para pyfolio.
        
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
    
    def generate_basic_stats(self, returns: pd.Series) -> Dict[str, Any]:
        """
        Genera estadísticas básicas usando pyfolio.
        
        Args:
            returns: Serie de retornos diarios
            
        Returns:
            Diccionario con estadísticas básicas
        """
        try:
            if returns.empty or returns.sum() == 0:
                logger.warning("No hay retornos para calcular estadísticas")
                return {}
            
            # Calcular estadísticas básicas
            stats = {}
            
            # Retorno total
            stats['total_return'] = float((1 + returns).prod() - 1)
            
            # Retorno anualizado
            stats['annual_return'] = float(pf.timeseries.annual_return(returns))
            
            # Volatilidad anualizada
            stats['annual_volatility'] = float(pf.timeseries.annual_volatility(returns))
            
            # Sharpe ratio
            stats['sharpe_ratio'] = float(pf.timeseries.sharpe_ratio(returns))
            
            # Sortino ratio
            stats['sortino_ratio'] = float(pf.timeseries.sortino_ratio(returns))
            
            # Maximum drawdown
            stats['max_drawdown'] = float(pf.timeseries.max_drawdown(returns))
            
            # Calmar ratio
            stats['calmar_ratio'] = float(pf.timeseries.calmar_ratio(returns))
            
            # Win rate
            stats['win_rate'] = float(pf.timeseries.win_rate(returns))
            
            # Profit factor
            stats['profit_factor'] = float(pf.timeseries.profit_factor(returns))
            
            # VaR (Value at Risk)
            stats['var_95'] = float(pf.timeseries.var(returns, cutoff=0.05))
            
            # CVaR (Conditional Value at Risk)
            stats['cvar_95'] = float(pf.timeseries.cvar(returns, cutoff=0.05))
            
            # Beta (asumiendo benchmark = 0)
            stats['beta'] = float(pf.timeseries.beta(returns, pd.Series(0.0, index=returns.index)))
            
            # Alpha
            stats['alpha'] = float(pf.timeseries.alpha(returns, pd.Series(0.0, index=returns.index)))
            
            # Information ratio
            stats['information_ratio'] = float(pf.timeseries.information_ratio(returns, pd.Series(0.0, index=returns.index)))
            
            # Stability
            stats['stability'] = float(pf.timeseries.stability_of_timeseries(returns))
            
            # Tail ratio
            stats['tail_ratio'] = float(pf.timeseries.tail_ratio(returns))
            
            # Common sense ratio
            stats['common_sense_ratio'] = float(pf.timeseries.common_sense_ratio(returns))
            
            # Outlier win ratio
            stats['outlier_win_ratio'] = float(pf.timeseries.outlier_win_ratio(returns))
            
            # Outlier loss ratio
            stats['outlier_loss_ratio'] = float(pf.timeseries.outlier_loss_ratio(returns))
            
            # Payoff ratio
            stats['payoff_ratio'] = float(pf.timeseries.payoff_ratio(returns))
            
            # Profit ratio
            stats['profit_ratio'] = float(pf.timeseries.profit_ratio(returns))
            
            # Win loss ratio
            stats['win_loss_ratio'] = float(pf.timeseries.win_loss_ratio(returns))
            
            # Expected return
            stats['expected_return'] = float(pf.timeseries.expected_return(returns))
            
            # Expected shortfall
            stats['expected_shortfall'] = float(pf.timeseries.expected_shortfall(returns))
            
            # Kelly criterion
            stats['kelly_criterion'] = float(pf.timeseries.kelly_criterion(returns))
            
            # Risk of ruin
            stats['risk_of_ruin'] = float(pf.timeseries.risk_of_ruin(returns))
            
            # Ulcer index
            stats['ulcer_index'] = float(pf.timeseries.ulcer_index(returns))
            
            # Ulcer performance index
            stats['ulcer_performance_index'] = float(pf.timeseries.ulcer_performance_index(returns))
            
            # Best day
            stats['best_day'] = float(returns.max())
            
            # Worst day
            stats['worst_day'] = float(returns.min())
            
            # Average win
            stats['avg_win'] = float(returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0.0)
            
            # Average loss
            stats['avg_loss'] = float(returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0.0)
            
            # Consecutive wins
            stats['consecutive_wins'] = float(pf.timeseries.consecutive_wins(returns))
            
            # Consecutive losses
            stats['consecutive_losses'] = float(pf.timeseries.consecutive_losses(returns))
            
            # Exposure time
            stats['exposure_time'] = float(pf.timeseries.exposure_time(returns))
            
            # Recovery factor
            stats['recovery_factor'] = float(pf.timeseries.recovery_factor(returns))
            
            # Clean stats (remove NaN and Inf values)
            cleaned_stats = {}
            for key, value in stats.items():
                if pd.isna(value) or np.isinf(value):
                    cleaned_stats[key] = None
                else:
                    cleaned_stats[key] = value
            
            logger.info(f"Estadísticas básicas calculadas: {len(cleaned_stats)} métricas")
            return cleaned_stats
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas básicas: {str(e)}")
            return {}
    
    def generate_drawdown_details(self, returns: pd.Series) -> Dict[str, Any]:
        """
        Genera detalles de drawdown usando pyfolio.
        
        Args:
            returns: Serie de retornos diarios
            
        Returns:
            Diccionario con detalles de drawdown
        """
        try:
            if returns.empty or returns.sum() == 0:
                logger.warning("No hay retornos para calcular drawdowns")
                return {'drawdown_details': []}
            
            # Calcular drawdowns usando pyfolio
            drawdowns = pf.timeseries.gen_drawdown_table(returns)
            
            # Convertir a formato JSON serializable
            drawdown_details = []
            for _, row in drawdowns.iterrows():
                drawdown_period = {
                    'start': row['Start'].strftime('%Y-%m-%d') if pd.notna(row['Start']) else None,
                    'end': row['End'].strftime('%Y-%m-%d') if pd.notna(row['End']) else None,
                    'days': int(row['Days']) if pd.notna(row['Days']) else None,
                    'max drawdown': float(row['Net drawdown in %']) if pd.notna(row['Net drawdown in %']) else None,
                    'peak': row['Peak date'].strftime('%Y-%m-%d') if pd.notna(row['Peak date']) else None,
                    'valley': row['Valley date'].strftime('%Y-%m-%d') if pd.notna(row['Valley date']) else None
                }
                drawdown_details.append(drawdown_period)
            
            logger.info(f"Detalles de drawdown calculados: {len(drawdown_details)} períodos")
            return {'drawdown_details': drawdown_details}
            
        except Exception as e:
            logger.error(f"Error calculando detalles de drawdown: {str(e)}")
            return {'drawdown_details': []}
    
    def generate_plots_data(self, returns: pd.Series) -> Dict[str, Any]:
        """
        Genera datos para visualizaciones usando pyfolio.
        
        Args:
            returns: Serie de retornos diarios
            
        Returns:
            Diccionario con datos para plots
        """
        try:
            if returns.empty or returns.sum() == 0:
                logger.warning("No hay retornos para generar datos de plots")
                return {}
            
            plots_data = {}
            
            # Rolling Sharpe ratio
            try:
                rolling_sharpe = pf.timeseries.rolling_sharpe(returns, rolling_window=252)
                plots_data['rolling_sharpe'] = {
                    'dates': rolling_sharpe.index.strftime('%Y-%m-%d').tolist(),
                    'values': rolling_sharpe.values.tolist()
                }
            except Exception as e:
                logger.warning(f"Error calculando rolling Sharpe: {str(e)}")
                plots_data['rolling_sharpe'] = None
            
            # Rolling Sortino ratio
            try:
                rolling_sortino = pf.timeseries.rolling_sortino(returns, rolling_window=252)
                plots_data['rolling_sortino'] = {
                    'dates': rolling_sortino.index.strftime('%Y-%m-%d').tolist(),
                    'values': rolling_sortino.values.tolist()
                }
            except Exception as e:
                logger.warning(f"Error calculando rolling Sortino: {str(e)}")
                plots_data['rolling_sortino'] = None
            
            # Rolling volatility
            try:
                rolling_vol = pf.timeseries.rolling_volatility(returns, rolling_window=252)
                plots_data['rolling_volatility'] = {
                    'dates': rolling_vol.index.strftime('%Y-%m-%d').tolist(),
                    'values': rolling_vol.values.tolist()
                }
            except Exception as e:
                logger.warning(f"Error calculando rolling volatility: {str(e)}")
                plots_data['rolling_volatility'] = None
            
            # Drawdown series
            try:
                drawdown_series = pf.timeseries.drawdown(returns)
                plots_data['drawdown_series'] = {
                    'dates': drawdown_series.index.strftime('%Y-%m-%d').tolist(),
                    'values': drawdown_series.values.tolist()
                }
            except Exception as e:
                logger.warning(f"Error calculando drawdown series: {str(e)}")
                plots_data['drawdown_series'] = None
            
            # Monthly returns heatmap
            try:
                monthly_returns = pf.timeseries.aggregate_returns(returns, 'monthly')
                plots_data['monthly_returns_heatmap'] = {
                    'years': [str(year) for year in monthly_returns.index.year.unique()],
                    'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    'values': monthly_returns.values.tolist()
                }
            except Exception as e:
                logger.warning(f"Error calculando monthly returns: {str(e)}")
                plots_data['monthly_returns_heatmap'] = None
            
            # Distribution stats
            try:
                plots_data['distribution_stats'] = {
                    'mean': float(returns.mean()),
                    'std': float(returns.std()),
                    'skew': float(returns.skew()),
                    'kurtosis': float(returns.kurtosis()),
                    'min': float(returns.min()),
                    'max': float(returns.max()),
                    'median': float(returns.median())
                }
            except Exception as e:
                logger.warning(f"Error calculando distribution stats: {str(e)}")
                plots_data['distribution_stats'] = None
            
            logger.info(f"Datos de plots generados: {len(plots_data)} tipos de visualización")
            return plots_data
            
        except Exception as e:
            logger.error(f"Error generando datos de plots: {str(e)}")
            return {}
    
    def generate_full_report(self, trades: List[Dict], initial_cash: float = 10000.0) -> Dict[str, Any]:
        """
        Genera un reporte completo usando pyfolio.
        
        Args:
            trades: Lista de trades del backtesting
            initial_cash: Capital inicial
            
        Returns:
            Diccionario con el reporte completo
        """
        try:
            logger.info(f"Generando reporte completo de pyfolio para {len(trades)} trades")
            
            # Generar serie de retornos
            returns = self.generate_returns_series(trades, initial_cash)
            
            if returns.empty:
                logger.warning("No se pudo generar serie de retornos")
                return {}
            
            # Generar estadísticas básicas
            basic_stats = self.generate_basic_stats(returns)
            
            # Generar detalles de drawdown
            drawdown_details = self.generate_drawdown_details(returns)
            
            # Generar datos para plots
            plots_data = self.generate_plots_data(returns)
            
            # Compilar reporte completo
            report_data = {
                'basic_stats': basic_stats,
                'drawdown_details': drawdown_details,
                'plots_data': plots_data
            }
            
            logger.info(f"Reporte completo generado con {len(report_data)} secciones")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generando reporte completo: {str(e)}")
            return {}
