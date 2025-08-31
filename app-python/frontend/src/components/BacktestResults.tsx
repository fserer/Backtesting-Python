import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { 
  Calendar, 
  TrendingUp, 
  BarChart3, 
  TrendingDown, 
  Target, 
  DollarSign 
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BacktestResponse } from '../lib/api';

interface BacktestResultsProps {
  results: BacktestResponse;
  initialCapital?: number;
  onSaveStrategy: () => void;
  onViewStrategies: () => void;
}

export function BacktestResults({ results, initialCapital, onSaveStrategy, onViewStrategies }: BacktestResultsProps) {
  const formatValue = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toLocaleString()}`;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value);
  };

  // Preparar datos para el gráfico de equity
  const equityData = results.equity?.map((point, index) => ({
    date: new Date(point.timestamp).toLocaleDateString('es-ES', { 
      day: '2-digit', 
      month: '2-digit', 
      year: '2-digit' 
    }),
    value: point.equity
  })) || [];

  // Calcular métricas adicionales
  const totalReturn = results.results?.total_return || 0;
  const cagr = results.results?.cagr || 0;
  const maxDrawdown = results.results?.max_drawdown || 0;
  const sharpeRatio = results.results?.sharpe_ratio || 0;
  const trades = results.trades?.length || 0;
  const finalCapital = initialCapital ? initialCapital * (1 + totalReturn) : 0;
  
  // Calcular duración total
  const periodDuration = results.results?.period_duration || '';

  return (
    <div className="space-y-6 mt-8">
      {/* KPIs Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">PLAZO TOTAL</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{periodDuration}</div>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">CAGR</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{(cagr * 100).toFixed(2)}%</div>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Retorno Total</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{(totalReturn * 100).toFixed(2)}%</div>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Ratio Sharpe</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{sharpeRatio.toFixed(2)}</div>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Máx. Drawdown</span>
            </div>
            <div className="text-2xl font-bold text-red-600">{(maxDrawdown * 100).toFixed(2)}%</div>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Operaciones</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{trades}</div>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Capital Inicial</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{formatCurrency(initialCapital || 0)}</div>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Capital Final</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{formatCurrency(finalCapital)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Gráfico de Equity */}
      <Card className="border-gray-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg text-gray-900">
            <TrendingUp className="h-5 w-5" />
            Curva de Equity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={equityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#666" />
                <YAxis tickFormatter={formatValue} tick={{ fontSize: 12 }} stroke="#666" />
                <Tooltip
                  formatter={(value: number) => [formatValue(value), "Equity"]}
                  labelStyle={{ color: "#333" }}
                  contentStyle={{
                    backgroundColor: "white",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={{ fill: "#2563eb", strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: "#2563eb", strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de Operaciones */}
      <Card className="border-gray-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg text-gray-900">
            <BarChart3 className="h-5 w-5" />
            Operaciones Detalladas ({trades} operaciones)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">#</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">Entrada</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">Precio Entrada</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">Salida</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">Precio Salida</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">Tamaño</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">Duración</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">P&L</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">Retorno</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-600">Comisiones</th>
                </tr>
              </thead>
              <tbody>
                {results.trades?.map((trade, index) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-3 px-2 text-sm">{index + 1}</td>
                    <td className="py-3 px-2 text-sm">
                      {new Date(trade.entry_time).toLocaleDateString('es-ES', {
                        day: '2-digit',
                        month: '2-digit',
                        year: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="py-3 px-2 text-sm">{formatCurrency(trade.entry_price)}</td>
                    <td className="py-3 px-2 text-sm">
                      {new Date(trade.exit_time).toLocaleDateString('es-ES', {
                        day: '2-digit',
                        month: '2-digit',
                        year: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="py-3 px-2 text-sm">{formatCurrency(trade.exit_price)}</td>
                    <td className="py-3 px-2 text-sm">{trade.size.toFixed(2)}</td>
                    <td className="py-3 px-2 text-sm">{trade.duration}</td>
                    <td className="py-3 px-2 text-sm text-green-600 font-medium">
                      {formatCurrency(trade.pnl)}
                    </td>
                    <td className="py-3 px-2 text-sm text-green-600 font-medium">
                      {(trade.return * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 px-2 text-sm text-orange-600">
                      {formatCurrency(trade.fees)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Resumen de operaciones */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {results.trades?.filter(t => t.pnl > 0).length || 0}
              </div>
              <div className="text-sm text-gray-600">Ganadoras</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">
                {results.trades?.filter(t => t.pnl < 0).length || 0}
              </div>
              <div className="text-sm text-gray-600">Perdedoras</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {formatCurrency(results.results?.total_pnl || 0)}
              </div>
              <div className="text-sm text-gray-600">P&L Total</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {formatCurrency(results.trades?.reduce((sum, t) => sum + t.fees, 0) || 0)}
              </div>
              <div className="text-sm text-gray-600">Comisiones Totales</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sección de Guardar Estrategia */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">¿Te gusta esta estrategia?</h3>
              <p className="text-gray-600">
                Guarda esta configuración para reutilizarla o compartirla con otros usuarios.
              </p>
            </div>
            <div className="flex gap-3">
              <Button 
                className="bg-blue-600 hover:bg-blue-700 text-white"
                onClick={onSaveStrategy}
              >
                Guardar Estrategia
              </Button>
              <Button 
                variant="outline" 
                className="border-blue-300 text-blue-700 hover:bg-blue-100 bg-transparent"
                onClick={onViewStrategies}
              >
                Ver Todas las Estrategias
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
