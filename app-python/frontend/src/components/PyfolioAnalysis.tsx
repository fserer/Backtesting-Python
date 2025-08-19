import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { BarChart3, TrendingUp, FileText, Loader2 } from 'lucide-react';
import { formatCurrency, formatPercentage, formatNumber } from '../lib/utils';
import { apiClient } from '@/lib/api';

interface PyfolioAnalysisProps {
  trades: any[];
  initialCash: number;
}

interface PyfolioData {
  basic_stats?: {
    total_return?: number;
    annual_return?: number;
    annual_volatility?: number;
    sharpe_ratio?: number;
    sortino_ratio?: number;
    max_drawdown?: number;
    calmar_ratio?: number;
    win_rate?: number;
    profit_factor?: number;
    var_95?: number;
    cvar_95?: number;
    beta?: number;
    alpha?: number;
    information_ratio?: number;
    stability?: number;
    tail_ratio?: number;
    common_sense_ratio?: number;
    outlier_win_ratio?: number;
    outlier_loss_ratio?: number;
    payoff_ratio?: number;
    profit_ratio?: number;
    win_loss_ratio?: number;
    expected_return?: number;
    expected_shortfall?: number;
    kelly_criterion?: number;
    risk_of_ruin?: number;
    ulcer_index?: number;
    ulcer_performance_index?: number;
    best_day?: number;
    worst_day?: number;
    avg_win?: number;
    avg_loss?: number;
    consecutive_wins?: number;
    consecutive_losses?: number;
    exposure_time?: number;
    recovery_factor?: number;
  };
  drawdown_details?: {
    drawdown_details?: Array<{
      start: string;
      end: string;
      days: number;
      'max drawdown': number;
      peak?: string;
      valley?: string;
    }>;
  };
  plots_data?: {
    rolling_sharpe?: {
      dates: string[];
      values: number[];
    };
    rolling_sortino?: {
      dates: string[];
      values: number[];
    };
    rolling_volatility?: {
      dates: string[];
      values: number[];
    };
    drawdown_series?: {
      dates: string[];
      values: number[];
    };
    monthly_returns_heatmap?: {
      years: string[];
      months: string[];
      values: number[];
    };
    distribution_stats?: {
      mean?: number;
      std?: number;
      skew?: number;
      kurtosis?: number;
      min?: number;
      max?: number;
      median?: number;
    };
  };
}

const PyfolioAnalysis: React.FC<PyfolioAnalysisProps> = ({ trades, initialCash }) => {
  const [pyfolioData, setPyfolioData] = useState<PyfolioData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generatePyfolioAnalysis = async () => {
    if (!trades || trades.length === 0) {
      setError('No hay trades para analizar');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('Enviando trades a Pyfolio:', trades.length, 'trades');
      const data = await apiClient.generatePyfolioAnalysis(trades, initialCash);
      console.log('Respuesta de Pyfolio:', data);
      setPyfolioData(data);
    } catch (err) {
      console.error('Error en Pyfolio:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Error desconocido al generar análisis Pyfolio');
      }
    } finally {
      setLoading(false);
    }
  };

  const renderMetricCard = (title: string, value: any, format: 'currency' | 'percentage' | 'number' = 'number') => {
    if (value === null || value === undefined) return null;
    
    let formattedValue = '';
    switch (format) {
      case 'currency':
        formattedValue = formatCurrency(value);
        break;
      case 'percentage':
        formattedValue = formatPercentage(value);
        break;
      default:
        formattedValue = formatNumber(value);
    }

    return (
      <Card key={title} className="flex-1 min-w-[200px]">
        <CardContent className="p-4">
          <div className="text-sm font-medium text-muted-foreground">{title}</div>
          <div className="text-2xl font-bold">{formattedValue}</div>
        </CardContent>
      </Card>
    );
  };

  const renderBasicStats = () => {
    console.log('renderBasicStats - pyfolioData:', pyfolioData);
    if (!pyfolioData?.basic_stats) {
      console.log('No basic_stats found');
      return <div className="text-muted-foreground">No hay estadísticas básicas disponibles</div>;
    }

    const stats = pyfolioData.basic_stats;
    console.log('renderBasicStats - stats:', stats);

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Retorno Total', stats.total_return, 'percentage')}
          {renderMetricCard('Retorno Anual', stats.annual_return, 'percentage')}
          {renderMetricCard('Volatilidad Anual', stats.annual_volatility, 'percentage')}
          {renderMetricCard('Sharpe Ratio', stats.sharpe_ratio)}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Sortino Ratio', stats.sortino_ratio)}
          {renderMetricCard('Máximo Drawdown', stats.max_drawdown, 'percentage')}
          {renderMetricCard('Calmar Ratio', stats.calmar_ratio)}
          {renderMetricCard('Win Rate', stats.win_rate, 'percentage')}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Profit Factor', stats.profit_factor)}
          {renderMetricCard('VaR (95%)', stats.var_95, 'percentage')}
          {renderMetricCard('CVaR (95%)', stats.cvar_95, 'percentage')}
          {renderMetricCard('Beta', stats.beta)}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Alpha', stats.alpha, 'percentage')}
          {renderMetricCard('Information Ratio', stats.information_ratio)}
          {renderMetricCard('Stability', stats.stability)}
          {renderMetricCard('Tail Ratio', stats.tail_ratio)}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Common Sense Ratio', stats.common_sense_ratio)}
          {renderMetricCard('Outlier Win Ratio', stats.outlier_win_ratio)}
          {renderMetricCard('Outlier Loss Ratio', stats.outlier_loss_ratio)}
          {renderMetricCard('Payoff Ratio', stats.payoff_ratio)}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Profit Ratio', stats.profit_ratio, 'percentage')}
          {renderMetricCard('Win/Loss Ratio', stats.win_loss_ratio)}
          {renderMetricCard('Expected Return', stats.expected_return, 'percentage')}
          {renderMetricCard('Expected Shortfall', stats.expected_shortfall, 'percentage')}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Kelly Criterion', stats.kelly_criterion, 'percentage')}
          {renderMetricCard('Risk of Ruin', stats.risk_of_ruin, 'percentage')}
          {renderMetricCard('Ulcer Index', stats.ulcer_index)}
          {renderMetricCard('Ulcer Performance Index', stats.ulcer_performance_index)}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Mejor Día', stats.best_day, 'percentage')}
          {renderMetricCard('Peor Día', stats.worst_day, 'percentage')}
          {renderMetricCard('Ganancia Promedio', stats.avg_win, 'percentage')}
          {renderMetricCard('Pérdida Promedio', stats.avg_loss, 'percentage')}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Victorias Consecutivas', stats.consecutive_wins)}
          {renderMetricCard('Pérdidas Consecutivas', stats.consecutive_losses)}
          {renderMetricCard('Tiempo de Exposición', stats.exposure_time, 'percentage')}
          {renderMetricCard('Recovery Factor', stats.recovery_factor)}
        </div>
      </div>
    );
  };

  const renderDrawdownDetails = () => {
    console.log('renderDrawdownDetails - pyfolioData:', pyfolioData);
    if (!pyfolioData?.drawdown_details?.drawdown_details) {
      console.log('No drawdown_details found');
      return <div className="text-muted-foreground">No hay detalles de drawdown disponibles</div>;
    }

    const drawdowns = pyfolioData.drawdown_details.drawdown_details;
    console.log('renderDrawdownDetails - drawdowns:', drawdowns);

    if (drawdowns.length === 0) {
      return <div className="text-muted-foreground">No se encontraron períodos de drawdown</div>;
    }

    return (
      <div className="space-y-4">
        <div className="text-lg font-semibold">Períodos de Drawdown</div>
        <div className="space-y-2">
          {drawdowns.map((drawdown, index) => (
            <Card key={index}>
              <CardContent className="p-4">
                <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-sm">
                  <div>
                    <span className="font-medium">Inicio:</span> {drawdown.start}
                  </div>
                  <div>
                    <span className="font-medium">Fin:</span> {drawdown.end}
                  </div>
                  <div>
                    <span className="font-medium">Días:</span> {drawdown.days}
                  </div>
                  <div>
                    <span className="font-medium">Máx Drawdown:</span> {formatPercentage(drawdown['max drawdown'])}
                  </div>
                  {drawdown.peak && (
                    <div>
                      <span className="font-medium">Pico:</span> {drawdown.peak}
                    </div>
                  )}
                  {drawdown.valley && (
                    <div>
                      <span className="font-medium">Valle:</span> {drawdown.valley}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  };

  const renderPlotsData = () => {
    console.log('renderPlotsData - pyfolioData:', pyfolioData);
    if (!pyfolioData?.plots_data) {
      console.log('No plots_data found');
      return <div className="text-muted-foreground">No hay datos de visualizaciones disponibles</div>;
    }

    const plots = pyfolioData.plots_data;
    console.log('renderPlotsData - plots:', plots);

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Estadísticas de Distribución</CardTitle>
            </CardHeader>
            <CardContent>
              {plots.distribution_stats && (
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><span className="font-medium">Media:</span> {formatNumber(plots.distribution_stats.mean)}</div>
                  <div><span className="font-medium">Desv. Est.:</span> {formatNumber(plots.distribution_stats.std)}</div>
                  <div><span className="font-medium">Asimetría:</span> {formatNumber(plots.distribution_stats.skew)}</div>
                  <div><span className="font-medium">Curtosis:</span> {formatNumber(plots.distribution_stats.kurtosis)}</div>
                  <div><span className="font-medium">Mínimo:</span> {formatNumber(plots.distribution_stats.min)}</div>
                  <div><span className="font-medium">Máximo:</span> {formatNumber(plots.distribution_stats.max)}</div>
                  <div><span className="font-medium">Mediana:</span> {formatNumber(plots.distribution_stats.median)}</div>
                </div>
              )}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Datos de Series Temporales</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium">Rolling Sharpe:</span> {plots.rolling_sharpe ? `${plots.rolling_sharpe.dates.length} puntos` : 'No disponible'}
                </div>
                <div>
                  <span className="font-medium">Rolling Sortino:</span> {plots.rolling_sortino ? `${plots.rolling_sortino.dates.length} puntos` : 'No disponible'}
                </div>
                <div>
                  <span className="font-medium">Rolling Volatility:</span> {plots.rolling_volatility ? `${plots.rolling_volatility.dates.length} puntos` : 'No disponible'}
                </div>
                <div>
                  <span className="font-medium">Drawdown Series:</span> {plots.drawdown_series ? `${plots.drawdown_series.dates.length} puntos` : 'No disponible'}
                </div>
                <div>
                  <span className="font-medium">Monthly Returns:</span> {plots.monthly_returns_heatmap ? `${plots.monthly_returns_heatmap.years.length} años` : 'No disponible'}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Análisis Pyfolio
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Análisis avanzado de rendimiento usando Pyfolio basado en los trades del backtesting
        </p>
      </CardHeader>
      <CardContent>
        {!pyfolioData && (
          <div className="flex flex-col items-center justify-center py-8 space-y-4">
            <Button
              onClick={generatePyfolioAnalysis}
              disabled={loading}
              className="flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generando...
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4" />
                  Generar Análisis Pyfolio
                </>
              )}
            </Button>
            {error && (
              <div className="text-red-500 text-sm text-center max-w-md">{error}</div>
            )}
          </div>
        )}

        {pyfolioData && (
          <Tabs defaultValue="metrics" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="metrics" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Métricas
              </TabsTrigger>
              <TabsTrigger value="drawdowns" className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Drawdowns
              </TabsTrigger>
              <TabsTrigger value="visualizations" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Visualizaciones
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="metrics" className="mt-6">
              {renderBasicStats()}
            </TabsContent>
            
            <TabsContent value="drawdowns" className="mt-6">
              {renderDrawdownDetails()}
            </TabsContent>
            
            <TabsContent value="visualizations" className="mt-6">
              {renderPlotsData()}
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
};

export default PyfolioAnalysis;
