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
            
            # Crear equity curve diaria
            equity_curve = pd.Series(initial_cash, index=date_range)
            
            # Procesar cada trade para construir el equity curve
            for _, trade in trades_df.iterrows():
                entry_date = trade['entry_date']
                exit_date = trade['exit_date']
                
                # Encontrar las fechas más cercanas en el índice
                entry_idx = date_range.get_indexer([entry_date], method='nearest')[0]
                exit_idx = date_range.get_indexer([exit_date], method='nearest')[0]
                
                # Calcular el retorno del trade
                if 'return_pct' in trade:
                    trade_return = trade['return_pct']
                else:
                    trade_return = trade['pnl'] / initial_cash
                
                # Aplicar el retorno del trade en el día de salida
                if exit_idx < len(equity_curve):
                    # Calcular el nuevo equity
                    current_equity = equity_curve.iloc[exit_idx]
                    new_equity = current_equity * (1 + trade_return)
                    equity_curve.iloc[exit_idx] = new_equity
                    
                    # Propagar el nuevo equity hacia adelante
                    for i in range(exit_idx + 1, len(equity_curve)):
                        equity_curve.iloc[i] = new_equity
                
                logger.info(f"Trade: {entry_date.date()} -> {exit_date.date()}, Retorno: {trade_return:.4f} ({trade_return*100:.2f}%)")
            
            # Calcular retornos diarios a partir del equity curve
            daily_returns = equity_curve.pct_change().fillna(0.0)
            
            # Limpiar valores extremos
            daily_returns = daily_returns.replace([np.inf, -np.inf], np.nan)
            daily_returns = daily_returns.fillna(0.0)
            
            # Verificar que los valores sean razonables
            daily_returns = daily_returns.clip(-1.0, 1.0)
            
            logger.info(f"Serie de retornos generada: {len(daily_returns)} días, desde {start_date} hasta {end_date}")
            logger.info(f"Retornos: min={daily_returns.min():.6f}, max={daily_returns.max():.6f}, mean={daily_returns.mean():.6f}")
            
            # Calcular retorno total acumulado para verificar
            total_return = (1 + daily_returns).prod() - 1
            logger.info(f"Retorno total acumulado: {total_return:.6f} ({total_return*100:.2f}%)")
            
            # Verificar con los trades originales
            if 'return_pct' in trades_df.columns:
                trades_total_return = trades_df['return_pct'].sum()
                logger.info(f"Retorno total de trades: {trades_total_return:.6f} ({trades_total_return*100:.2f}%)")
            
            # Log adicional para verificar los trades individuales
            logger.info(f"Trades individuales:")
            for i, trade in trades_df.iterrows():
                logger.info(f"  Trade {i+1}: {trade['return_pct']:.4f} ({trade['return_pct']*100:.2f}%)")
            
            return daily_returns
            
        except Exception as e:
            logger.error(f"Error generando serie de retornos: {str(e)}")
            raise e
    
    def _custom_win_rate(self, returns: pd.Series) -> float:
        """Calcula el win rate personalizado."""
        if len(returns) == 0:
            return 0.0
        winning_days = (returns > 0).sum()
        return winning_days / len(returns)
    
    def _custom_profit_factor(self, returns: pd.Series) -> float:
        """Calcula el profit factor personalizado."""
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        if len(negative_returns) == 0:
            return float('inf') if len(positive_returns) > 0 else 0.0
        
        gross_profit = positive_returns.sum()
        gross_loss = abs(negative_returns.sum())
        
        return gross_profit / gross_loss if gross_loss > 0 else 0.0
    
    def _custom_var(self, returns: pd.Series, cutoff: float = 0.05) -> float:
        """Calcula el Value at Risk personalizado."""
        if len(returns) == 0:
            return 0.0
        return np.percentile(returns, cutoff * 100)
    
    def _custom_cvar(self, returns: pd.Series, cutoff: float = 0.05) -> float:
        """Calcula el Conditional Value at Risk personalizado."""
        if len(returns) == 0:
            return 0.0
        var = self._custom_var(returns, cutoff)
        return returns[returns <= var].mean()
    
    def _custom_information_ratio(self, returns: pd.Series, benchmark: pd.Series) -> float:
        """Calcula el information ratio personalizado."""
        if len(returns) == 0:
            return 0.0
        excess_returns = returns - benchmark
        return excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0.0
    
    def _custom_outlier_win_ratio(self, returns: pd.Series) -> float:
        """Calcula el outlier win ratio personalizado."""
        if len(returns) == 0:
            return 0.0
        positive_returns = returns[returns > 0]
        if len(positive_returns) == 0:
            return 0.0
        outlier_threshold = positive_returns.mean() + 2 * positive_returns.std()
        outlier_wins = (positive_returns > outlier_threshold).sum()
        return outlier_wins / len(positive_returns)
    
    def _custom_outlier_loss_ratio(self, returns: pd.Series) -> float:
        """Calcula el outlier loss ratio personalizado."""
        if len(returns) == 0:
            return 0.0
        negative_returns = returns[returns < 0]
        if len(negative_returns) == 0:
            return 0.0
        outlier_threshold = negative_returns.mean() - 2 * negative_returns.std()
        outlier_losses = (negative_returns < outlier_threshold).sum()
        return outlier_losses / len(negative_returns)
    
    def _custom_payoff_ratio(self, returns: pd.Series) -> float:
        """Calcula el payoff ratio personalizado."""
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        if len(positive_returns) == 0 or len(negative_returns) == 0:
            return 0.0
        
        avg_win = positive_returns.mean()
        avg_loss = abs(negative_returns.mean())
        
        return avg_win / avg_loss if avg_loss > 0 else 0.0
    
    def _custom_profit_ratio(self, returns: pd.Series) -> float:
        """Calcula el profit ratio personalizado."""
        if len(returns) == 0:
            return 0.0
        return returns[returns > 0].sum() / abs(returns[returns < 0].sum()) if returns[returns < 0].sum() != 0 else 0.0
    
    def _custom_win_loss_ratio(self, returns: pd.Series) -> float:
        """Calcula el win/loss ratio personalizado."""
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        if len(negative_returns) == 0:
            return float('inf') if len(positive_returns) > 0 else 0.0
        
        return len(positive_returns) / len(negative_returns)
    
    def _custom_expected_return(self, returns: pd.Series) -> float:
        """Calcula el expected return personalizado."""
        if len(returns) == 0:
            return 0.0
        return returns.mean()
    
    def _custom_expected_shortfall(self, returns: pd.Series) -> float:
        """Calcula el expected shortfall personalizado."""
        return self._custom_cvar(returns, 0.05)
    
    def _custom_kelly_criterion(self, returns: pd.Series) -> float:
        """Calcula el Kelly criterion personalizado."""
        if len(returns) == 0:
            return 0.0
        win_rate = self._custom_win_rate(returns)
        avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
        avg_loss = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 1
        
        if avg_loss == 0:
            return 0.0
        
        return (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win if avg_win > 0 else 0.0
    
    def _custom_risk_of_ruin(self, returns: pd.Series) -> float:
        """Calcula el risk of ruin personalizado."""
        if len(returns) == 0:
            return 0.0
        # Implementación simplificada del risk of ruin
        negative_returns = returns[returns < 0]
        if len(negative_returns) == 0:
            return 0.0
        return len(negative_returns) / len(returns)
    
    def _custom_ulcer_index(self, returns: pd.Series) -> float:
        """Calcula el ulcer index personalizado."""
        if len(returns) == 0:
            return 0.0
        cumulative_returns = (1 + returns).cumprod()
        drawdown = (cumulative_returns - cumulative_returns.cummax()) / cumulative_returns.cummax()
        return np.sqrt((drawdown ** 2).mean())
    
    def _custom_ulcer_performance_index(self, returns: pd.Series) -> float:
        """Calcula el ulcer performance index personalizado."""
        if len(returns) == 0:
            return 0.0
        ulcer_index = self._custom_ulcer_index(returns)
        if ulcer_index == 0:
            return 0.0
        return returns.mean() / ulcer_index
    
    def _custom_consecutive_wins(self, returns: pd.Series) -> float:
        """Calcula el número de victorias consecutivas personalizado."""
        if len(returns) == 0:
            return 0.0
        max_consecutive = 0
        current_consecutive = 0
        for ret in returns:
            if ret > 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        return float(max_consecutive)
    
    def _custom_consecutive_losses(self, returns: pd.Series) -> float:
        """Calcula el número de pérdidas consecutivas personalizado."""
        if len(returns) == 0:
            return 0.0
        max_consecutive = 0
        current_consecutive = 0
        for ret in returns:
            if ret < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        return float(max_consecutive)
    
    def _custom_exposure_time(self, returns: pd.Series) -> float:
        """Calcula el tiempo de exposición personalizado."""
        if len(returns) == 0:
            return 0.0
        # Para trades discretos, el tiempo de exposición es la proporción de días con actividad
        active_days = (returns != 0).sum()
        return active_days / len(returns)
    
    def _custom_recovery_factor(self, returns: pd.Series) -> float:
        """Calcula el recovery factor personalizado."""
        if len(returns) == 0:
            return 0.0
        total_return = (1 + returns).prod() - 1
        max_dd = abs(pf.timeseries.max_drawdown(returns))
        return total_return / max_dd if max_dd > 0 else 0.0
    
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
            try:
                stats['annual_return'] = float(pf.timeseries.annual_return(returns))
            except Exception as e:
                logger.warning(f"Error calculando annual_return: {str(e)}")
                stats['annual_return'] = None
            
            # Volatilidad anualizada
            try:
                stats['annual_volatility'] = float(pf.timeseries.annual_volatility(returns))
            except Exception as e:
                logger.warning(f"Error calculando annual_volatility: {str(e)}")
                stats['annual_volatility'] = None
            
            # Sharpe ratio
            try:
                stats['sharpe_ratio'] = float(pf.timeseries.sharpe_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando sharpe_ratio: {str(e)}")
                stats['sharpe_ratio'] = None
            
            # Sortino ratio
            try:
                stats['sortino_ratio'] = float(pf.timeseries.sortino_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando sortino_ratio: {str(e)}")
                stats['sortino_ratio'] = None
            
            # Maximum drawdown
            try:
                stats['max_drawdown'] = float(pf.timeseries.max_drawdown(returns))
            except Exception as e:
                logger.warning(f"Error calculando max_drawdown: {str(e)}")
                stats['max_drawdown'] = None
            
            # Calmar ratio
            try:
                stats['calmar_ratio'] = float(pf.timeseries.calmar_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando calmar_ratio: {str(e)}")
                stats['calmar_ratio'] = None
            
            # Win rate (custom implementation)
            try:
                stats['win_rate'] = float(self._custom_win_rate(returns))
            except Exception as e:
                logger.warning(f"Error calculando win_rate: {str(e)}")
                stats['win_rate'] = None
            
            # Profit factor (custom implementation)
            try:
                stats['profit_factor'] = float(self._custom_profit_factor(returns))
            except Exception as e:
                logger.warning(f"Error calculando profit_factor: {str(e)}")
                stats['profit_factor'] = None
            
            # VaR (Value at Risk) - custom implementation
            try:
                stats['var_95'] = float(self._custom_var(returns, cutoff=0.05))
            except Exception as e:
                logger.warning(f"Error calculando var_95: {str(e)}")
                stats['var_95'] = None
            
            # CVaR (Conditional Value at Risk) - custom implementation
            try:
                stats['cvar_95'] = float(self._custom_cvar(returns, cutoff=0.05))
            except Exception as e:
                logger.warning(f"Error calculando cvar_95: {str(e)}")
                stats['cvar_95'] = None
            
            # Beta (asumiendo benchmark = 0)
            try:
                stats['beta'] = float(pf.timeseries.beta(returns, pd.Series(0.0, index=returns.index)))
            except Exception as e:
                logger.warning(f"Error calculando beta: {str(e)}")
                stats['beta'] = None
            
            # Alpha
            try:
                stats['alpha'] = float(pf.timeseries.alpha(returns, pd.Series(0.0, index=returns.index)))
            except Exception as e:
                logger.warning(f"Error calculando alpha: {str(e)}")
                stats['alpha'] = None
            
            # Information ratio (custom implementation)
            try:
                stats['information_ratio'] = float(self._custom_information_ratio(returns, pd.Series(0.0, index=returns.index)))
            except Exception as e:
                logger.warning(f"Error calculando information_ratio: {str(e)}")
                stats['information_ratio'] = None
            
            # Stability
            try:
                stats['stability'] = float(pf.timeseries.stability_of_timeseries(returns))
            except Exception as e:
                logger.warning(f"Error calculando stability: {str(e)}")
                stats['stability'] = None
            
            # Tail ratio
            try:
                stats['tail_ratio'] = float(pf.timeseries.tail_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando tail_ratio: {str(e)}")
                stats['tail_ratio'] = None
            
            # Common sense ratio
            try:
                stats['common_sense_ratio'] = float(pf.timeseries.common_sense_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando common_sense_ratio: {str(e)}")
                stats['common_sense_ratio'] = None
            
            # Outlier win ratio (custom implementation)
            try:
                stats['outlier_win_ratio'] = float(self._custom_outlier_win_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando outlier_win_ratio: {str(e)}")
                stats['outlier_win_ratio'] = None
            
            # Outlier loss ratio (custom implementation)
            try:
                stats['outlier_loss_ratio'] = float(self._custom_outlier_loss_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando outlier_loss_ratio: {str(e)}")
                stats['outlier_loss_ratio'] = None
            
            # Payoff ratio (custom implementation)
            try:
                stats['payoff_ratio'] = float(self._custom_payoff_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando payoff_ratio: {str(e)}")
                stats['payoff_ratio'] = None
            
            # Profit ratio (custom implementation)
            try:
                stats['profit_ratio'] = float(self._custom_profit_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando profit_ratio: {str(e)}")
                stats['profit_ratio'] = None
            
            # Win loss ratio (custom implementation)
            try:
                stats['win_loss_ratio'] = float(self._custom_win_loss_ratio(returns))
            except Exception as e:
                logger.warning(f"Error calculando win_loss_ratio: {str(e)}")
                stats['win_loss_ratio'] = None
            
            # Expected return (custom implementation)
            try:
                stats['expected_return'] = float(self._custom_expected_return(returns))
            except Exception as e:
                logger.warning(f"Error calculando expected_return: {str(e)}")
                stats['expected_return'] = None
            
            # Expected shortfall (custom implementation)
            try:
                stats['expected_shortfall'] = float(self._custom_expected_shortfall(returns))
            except Exception as e:
                logger.warning(f"Error calculando expected_shortfall: {str(e)}")
                stats['expected_shortfall'] = None
            
            # Kelly criterion (custom implementation)
            try:
                stats['kelly_criterion'] = float(self._custom_kelly_criterion(returns))
            except Exception as e:
                logger.warning(f"Error calculando kelly_criterion: {str(e)}")
                stats['kelly_criterion'] = None
            
            # Risk of ruin (custom implementation)
            try:
                stats['risk_of_ruin'] = float(self._custom_risk_of_ruin(returns))
            except Exception as e:
                logger.warning(f"Error calculando risk_of_ruin: {str(e)}")
                stats['risk_of_ruin'] = None
            
            # Ulcer index (custom implementation)
            try:
                stats['ulcer_index'] = float(self._custom_ulcer_index(returns))
            except Exception as e:
                logger.warning(f"Error calculando ulcer_index: {str(e)}")
                stats['ulcer_index'] = None
            
            # Ulcer performance index (custom implementation)
            try:
                stats['ulcer_performance_index'] = float(self._custom_ulcer_performance_index(returns))
            except Exception as e:
                logger.warning(f"Error calculando ulcer_performance_index: {str(e)}")
                stats['ulcer_performance_index'] = None
            
            # Best day
            stats['best_day'] = float(returns.max())
            
            # Worst day
            stats['worst_day'] = float(returns.min())
            
            # Average win
            stats['avg_win'] = float(returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0.0)
            
            # Average loss
            stats['avg_loss'] = float(returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0.0)
            
            # Consecutive wins (custom implementation)
            try:
                stats['consecutive_wins'] = float(self._custom_consecutive_wins(returns))
            except Exception as e:
                logger.warning(f"Error calculando consecutive_wins: {str(e)}")
                stats['consecutive_wins'] = None
            
            # Consecutive losses (custom implementation)
            try:
                stats['consecutive_losses'] = float(self._custom_consecutive_losses(returns))
            except Exception as e:
                logger.warning(f"Error calculando consecutive_losses: {str(e)}")
                stats['consecutive_losses'] = None
            
            # Exposure time (custom implementation)
            try:
                stats['exposure_time'] = float(self._custom_exposure_time(returns))
            except Exception as e:
                logger.warning(f"Error calculando exposure_time: {str(e)}")
                stats['exposure_time'] = None
            
            # Recovery factor (custom implementation)
            try:
                stats['recovery_factor'] = float(self._custom_recovery_factor(returns))
            except Exception as e:
                logger.warning(f"Error calculando recovery_factor: {str(e)}")
                stats['recovery_factor'] = None
            
            # Clean stats (remove NaN and Inf values)
            cleaned_stats = {}
            for key, value in stats.items():
                if pd.isna(value) or np.isinf(value):
                    cleaned_stats[key] = None
                else:
                    cleaned_stats[key] = value
            
            logger.info(f"Estadísticas básicas calculadas: {len(cleaned_stats)} métricas")
            logger.info(f"Estadísticas disponibles: {list(cleaned_stats.keys())}")
            logger.info(f"Total return: {cleaned_stats.get('total_return', 'N/A')}")
            logger.info(f"Sharpe ratio: {cleaned_stats.get('sharpe_ratio', 'N/A')}")
            logger.info(f"Max drawdown: {cleaned_stats.get('max_drawdown', 'N/A')}")
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
            
            # Verificar si hay datos de drawdown
            if drawdowns.empty:
                logger.info("No se encontraron períodos de drawdown")
                return {'drawdown_details': []}
            
            # Convertir a formato JSON serializable
            drawdown_details = []
            for _, row in drawdowns.iterrows():
                try:
                    drawdown_period = {
                        'start': row['Start'].strftime('%Y-%m-%d') if pd.notna(row['Start']) else None,
                        'end': row['End'].strftime('%Y-%m-%d') if pd.notna(row['End']) else None,
                        'days': int(row['Days']) if pd.notna(row['Days']) else None,
                        'max drawdown': float(row['Net drawdown in %']) if pd.notna(row['Net drawdown in %']) else None,
                        'peak': row['Peak date'].strftime('%Y-%m-%d') if pd.notna(row['Peak date']) else None,
                        'valley': row['Valley date'].strftime('%Y-%m-%d') if pd.notna(row['Valley date']) else None
                    }
                    drawdown_details.append(drawdown_period)
                except Exception as e:
                    logger.warning(f"Error procesando fila de drawdown: {str(e)}")
                    continue
            
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
            
            # Rolling Sharpe ratio (custom implementation)
            try:
                # Custom rolling sharpe implementation
                window = 252
                rolling_sharpe = pd.Series(index=returns.index, dtype=float)
                
                for i in range(window, len(returns)):
                    window_returns = returns.iloc[i-window:i]
                    if len(window_returns) > 0:
                        mean_return = window_returns.mean()
                        std_return = window_returns.std()
                        if std_return > 0:
                            rolling_sharpe.iloc[i] = mean_return / std_return
                
                rolling_sharpe = rolling_sharpe.dropna()
                if len(rolling_sharpe) > 0:
                    plots_data['rolling_sharpe'] = {
                        'dates': rolling_sharpe.index.strftime('%Y-%m-%d').tolist(),
                        'values': rolling_sharpe.values.tolist()
                    }
                else:
                    plots_data['rolling_sharpe'] = None
            except Exception as e:
                logger.warning(f"Error calculando rolling Sharpe: {str(e)}")
                plots_data['rolling_sharpe'] = None
            
            # Rolling volatility (custom implementation)
            try:
                # Custom rolling volatility implementation
                window = 252
                rolling_vol = pd.Series(index=returns.index, dtype=float)
                
                for i in range(window, len(returns)):
                    window_returns = returns.iloc[i-window:i]
                    if len(window_returns) > 0:
                        rolling_vol.iloc[i] = window_returns.std() * np.sqrt(252)  # Annualized
                
                rolling_vol = rolling_vol.dropna()
                if len(rolling_vol) > 0:
                    plots_data['rolling_volatility'] = {
                        'dates': rolling_vol.index.strftime('%Y-%m-%d').tolist(),
                        'values': rolling_vol.values.tolist()
                    }
                else:
                    plots_data['rolling_volatility'] = None
            except Exception as e:
                logger.warning(f"Error calculando rolling volatility: {str(e)}")
                plots_data['rolling_volatility'] = None
            
            # Rolling Sortino ratio (custom implementation)
            try:
                # Custom rolling sortino implementation
                window = 252
                rolling_sortino = pd.Series(index=returns.index, dtype=float)
                
                for i in range(window, len(returns)):
                    window_returns = returns.iloc[i-window:i]
                    if len(window_returns) > 0:
                        mean_return = window_returns.mean()
                        downside_returns = window_returns[window_returns < 0]
                        if len(downside_returns) > 0:
                            downside_std = downside_returns.std()
                            if downside_std > 0:
                                rolling_sortino.iloc[i] = mean_return / downside_std
                
                rolling_sortino = rolling_sortino.dropna()
                if len(rolling_sortino) > 0:
                    plots_data['rolling_sortino'] = {
                        'dates': rolling_sortino.index.strftime('%Y-%m-%d').tolist(),
                        'values': rolling_sortino.values.tolist()
                    }
                else:
                    plots_data['rolling_sortino'] = None
            except Exception as e:
                logger.warning(f"Error calculando rolling Sortino: {str(e)}")
                plots_data['rolling_sortino'] = None
            
            # Drawdown series
            try:
                # Crear serie de drawdown diario directamente
                cumulative_returns = (1 + returns).cumprod()
                running_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - running_max) / running_max
                
                if len(drawdown) > 0:
                    plots_data['drawdown_series'] = {
                        'dates': drawdown.index.strftime('%Y-%m-%d').tolist(),
                        'values': drawdown.values.tolist()
                    }
                else:
                    plots_data['drawdown_series'] = None
            except Exception as e:
                logger.warning(f"Error calculando drawdown series: {str(e)}")
                plots_data['drawdown_series'] = None
            
            # Monthly returns heatmap
            try:
                monthly_returns = pf.timeseries.aggregate_returns(returns, 'monthly')
                # Convertir el índice a formato más simple
                plots_data['monthly_returns_heatmap'] = {
                    'years': [str(year) for year in monthly_returns.index.get_level_values(0).unique()],
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
