import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { BarChart3, TrendingUp, FileText, Loader2 } from 'lucide-react';
import { formatCurrency, formatPercentage, formatNumber } from '../lib/utils';
import { apiClient } from '../lib/api';

interface QuantStatsAnalysisProps {
  trades: any[];
  initialCash: number;
}

interface QuantStatsData {
  basic_stats?: {
    total_return?: number;
    sharpe_ratio?: number;
    sortino_ratio?: number;
    max_drawdown?: number;
    volatility?: number;
    win_rate?: number;
    profit_factor?: number;
    calmar_ratio?: number;
    information_ratio?: number;
    skewness?: number;
    kurtosis?: number;
    var_95?: number;
    cvar_95?: number;
    ulcer_index?: number;
    gain_to_pain_ratio?: number;
    best_day?: number;
    worst_day?: number;
    avg_win?: number;
    avg_loss?: number;
    consecutive_wins?: number;
    consecutive_losses?: number;
    exposure_time?: number;
    recovery_factor?: number;
    risk_of_ruin?: number;
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
    rar?: number;
    ror?: number;
    ghpr?: number;
    adjusted_sortino?: number;
    ulcer_performance_index?: number;
    cpc_index?: number;
    comp?: number;
    compsum?: number;
    geometric_mean?: number;
  };
  drawdown_details?: {
    drawdown_details?: any[];
  };
  plots_data?: {
    rolling_sharpe?: Record<string, number>;
    rolling_sortino?: Record<string, number>;
    rolling_volatility?: Record<string, number>;
    drawdown_series?: Record<string, number>;
    monthly_returns_heatmap?: Record<string, any>;
    distribution_stats?: {
      mean?: number;
      std?: number;
      skew?: number;
      kurtosis?: number;
    };
  };
}

const QuantStatsAnalysis: React.FC<QuantStatsAnalysisProps> = ({ trades, initialCash }) => {
  const [quantStatsData, setQuantStatsData] = useState<QuantStatsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateQuantStatsAnalysis = async () => {
    if (!trades || trades.length === 0) {
      setError('No hay trades para analizar');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('Enviando trades a QuantStats:', trades.length, 'trades');
      const data = await apiClient.generateQuantStatsAnalysis(trades, initialCash);
      console.log('Respuesta de QuantStats:', data);
      setQuantStatsData(data);
    } catch (err) {
      console.error('Error en QuantStats:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError('Error desconocido al generar análisis QuantStats');
      }
    } finally {
      setLoading(false);
    }
  };

  const renderMetricCard = (title: string, value: number | undefined, format: 'currency' | 'percentage' | 'number' = 'number', suffix: string = '') => {
    if (value === undefined || value === null) return null;

    let formattedValue = '';
    switch (format) {
      case 'currency':
        formattedValue = formatCurrency(value);
        break;
      case 'percentage':
        formattedValue = formatPercentage(value);
        break;
      case 'number':
        formattedValue = formatNumber(value) + suffix;
        break;
    }

    return (
      <div className="bg-white p-3 rounded-lg border">
        <div className="text-sm text-gray-600 font-medium">{title}</div>
        <div className="text-lg font-bold text-gray-900">{formattedValue}</div>
      </div>
    );
  };

  const renderBasicStats = () => {
    if (!quantStatsData?.basic_stats) return null;

    const stats = quantStatsData.basic_stats;

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {renderMetricCard('Retorno Total', stats.total_return, 'percentage')}
          {renderMetricCard('Ratio Sharpe', stats.sharpe_ratio, 'number')}
          {renderMetricCard('Ratio Sortino', stats.sortino_ratio, 'number')}
          {renderMetricCard('Máximo Drawdown', stats.max_drawdown, 'percentage')}
          {renderMetricCard('Volatilidad', stats.volatility, 'percentage')}
          {renderMetricCard('Win Rate', stats.win_rate, 'percentage')}
          {renderMetricCard('Profit Factor', stats.profit_factor, 'number')}
          {renderMetricCard('Ratio Calmar', stats.calmar_ratio, 'number')}
          {renderMetricCard('Ratio de Información', stats.information_ratio, 'number')}
          {renderMetricCard('Asimetría', stats.skewness, 'number')}
          {renderMetricCard('Curtosis', stats.kurtosis, 'number')}
          {renderMetricCard('VaR 95%', stats.var_95, 'percentage')}
          {renderMetricCard('CVaR 95%', stats.cvar_95, 'percentage')}
          {renderMetricCard('Índice Úlcera', stats.ulcer_index, 'number')}
          {renderMetricCard('Ganancia/Dolor', stats.gain_to_pain_ratio, 'number')}
          {renderMetricCard('Mejor Día', stats.best_day, 'percentage')}
          {renderMetricCard('Peor Día', stats.worst_day, 'percentage')}
          {renderMetricCard('Ganancia Promedio', stats.avg_win, 'percentage')}
          {renderMetricCard('Pérdida Promedio', stats.avg_loss, 'percentage')}
          {renderMetricCard('Victorias Consecutivas', stats.consecutive_wins, 'number')}
          {renderMetricCard('Pérdidas Consecutivas', stats.consecutive_losses, 'number')}
          {renderMetricCard('Tiempo de Exposición', stats.exposure_time, 'percentage')}
          {renderMetricCard('Factor de Recuperación', stats.recovery_factor, 'number')}
          {renderMetricCard('Riesgo de Ruina', stats.risk_of_ruin, 'percentage')}
          {renderMetricCard('Ratio de Cola', stats.tail_ratio, 'number')}
          {renderMetricCard('Ratio de Sentido Común', stats.common_sense_ratio, 'number')}
          {renderMetricCard('Ratio de Outliers Ganadores', stats.outlier_win_ratio, 'percentage')}
          {renderMetricCard('Ratio de Outliers Perdedores', stats.outlier_loss_ratio, 'percentage')}
          {renderMetricCard('Ratio de Pago', stats.payoff_ratio, 'number')}
          {renderMetricCard('Ratio de Beneficio', stats.profit_ratio, 'percentage')}
          {renderMetricCard('Ratio Ganancia/Pérdida', stats.win_loss_ratio, 'number')}
          {renderMetricCard('Retorno Esperado', stats.expected_return, 'percentage')}
          {renderMetricCard('Pérdida Esperada', stats.expected_shortfall, 'percentage')}
          {renderMetricCard('Criterio de Kelly', stats.kelly_criterion, 'percentage')}
          {renderMetricCard('RAR', stats.rar, 'percentage')}
          {renderMetricCard('ROR', stats.ror, 'percentage')}
          {renderMetricCard('GHPR', stats.ghpr, 'percentage')}
          {renderMetricCard('Sortino Ajustado', stats.adjusted_sortino, 'number')}
          {renderMetricCard('Índice de Rendimiento Úlcera', stats.ulcer_performance_index, 'number')}
          {renderMetricCard('Índice CPC', stats.cpc_index, 'number')}
          {renderMetricCard('Comp', stats.comp, 'number')}
          {renderMetricCard('Compsum', stats.compsum, 'number')}
          {renderMetricCard('Media Geométrica', stats.geometric_mean, 'percentage')}
        </div>
      </div>
    );
  };

  const renderDrawdownDetails = () => {
    if (!quantStatsData?.drawdown_details?.drawdown_details) return null;

    const drawdowns = quantStatsData.drawdown_details.drawdown_details;

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Detalles de Drawdowns</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Inicio</th>
                <th className="text-left p-2">Fin</th>
                <th className="text-left p-2">Duración</th>
                <th className="text-left p-2">Drawdown</th>
                <th className="text-left p-2">Recuperación</th>
              </tr>
            </thead>
            <tbody>
              {drawdowns.map((dd: any, index: number) => (
                <tr key={index} className="border-b">
                  <td className="p-2">{dd.start}</td>
                  <td className="p-2">{dd.end}</td>
                  <td className="p-2">{dd.duration}</td>
                  <td className="p-2 text-red-600">{formatPercentage(dd.drawdown)}</td>
                  <td className="p-2 text-green-600">{formatPercentage(dd.recovery)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderPlotsData = () => {
    if (!quantStatsData?.plots_data) return null;

    const plots = quantStatsData.plots_data;

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Estadísticas de Distribución */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Estadísticas de Distribución</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {renderMetricCard('Media', plots.distribution_stats?.mean, 'percentage')}
                {renderMetricCard('Desviación Estándar', plots.distribution_stats?.std, 'percentage')}
                {renderMetricCard('Asimetría', plots.distribution_stats?.skew, 'number')}
                {renderMetricCard('Curtosis', plots.distribution_stats?.kurtosis, 'number')}
              </div>
            </CardContent>
          </Card>

          {/* Datos de Series Temporales */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Series Temporales</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Rolling Sharpe:</span> {Object.keys(plots.rolling_sharpe || {}).length} puntos
                </div>
                <div className="text-sm">
                  <span className="font-medium">Rolling Sortino:</span> {Object.keys(plots.rolling_sortino || {}).length} puntos
                </div>
                <div className="text-sm">
                  <span className="font-medium">Rolling Volatility:</span> {Object.keys(plots.rolling_volatility || {}).length} puntos
                </div>
                <div className="text-sm">
                  <span className="font-medium">Drawdown Series:</span> {Object.keys(plots.drawdown_series || {}).length} puntos
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Nota sobre visualizaciones */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Nota:</strong> Los datos para visualizaciones están disponibles. 
            Para gráficos interactivos completos, considera integrar librerías como Chart.js o Recharts.
          </p>
        </div>
      </div>
    );
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Análisis QuantStats
        </CardTitle>
        <p className="text-sm text-gray-600">
          Análisis avanzado de rendimiento usando QuantStats basado en los trades del backtesting
        </p>
      </CardHeader>
      <CardContent>
        {!quantStatsData && (
          <div className="text-center py-8">
            <Button 
              onClick={generateQuantStatsAnalysis}
              disabled={loading || !trades || trades.length === 0}
              className="flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generando Análisis...
                </>
              ) : (
                <>
                  <BarChart3 className="h-4 w-4" />
                  Generar Análisis QuantStats
                </>
              )}
            </Button>
            {error && (
              <p className="text-red-600 text-sm mt-2">{error}</p>
            )}
          </div>
        )}

        {quantStatsData && (
          <Tabs defaultValue="stats" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="stats" className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Métricas
              </TabsTrigger>
              <TabsTrigger value="drawdowns" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Drawdowns
              </TabsTrigger>
              <TabsTrigger value="plots" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Visualizaciones
              </TabsTrigger>
            </TabsList>

            <TabsContent value="stats" className="mt-6">
              {renderBasicStats()}
            </TabsContent>

            <TabsContent value="drawdowns" className="mt-6">
              {renderDrawdownDetails()}
            </TabsContent>

            <TabsContent value="plots" className="mt-6">
              {renderPlotsData()}
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
};

export default QuantStatsAnalysis;
