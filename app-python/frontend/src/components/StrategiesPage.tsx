import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Eye, RefreshCw, Trash2, TrendingUp } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

interface Strategy {
  id: number;
  user_id: number;
  username: string;
  strategy_type: string;
  created_at: string;
  num_trades: number;
  total_pnl: number;
  total_costs: number;
  net_pnl: number;
  comments?: string;
  formatted_config: {
    dataset_name: string;
    strategy_description: string;
    period: string;
    fees_percentage: string;
    init_cash_formatted: string;
    transformations: string[];
    thresholds?: { entry: number; exit: number };
    crossover_details: string;
    bitcoin_condition: string;
    apply_to: string;
    raw_configuration: any;
  };
}

interface StrategiesPageProps {
  currentUserId: number;
}

const StrategiesPage: React.FC<StrategiesPageProps> = ({ currentUserId }) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingStrategy, setDeletingStrategy] = useState<number | null>(null);
  const [expandedStrategy, setExpandedStrategy] = useState<number | null>(null);

  const fetchStrategies = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/strategies`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStrategies(data.strategies);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Error cargando estrategias');
      }
    } catch (err) {
      setError('Error de conexión. Verifica que el backend esté funcionando.');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteStrategy = async (strategyId: number) => {
    if (!confirm('¿Estás seguro de que quieres eliminar esta estrategia?')) {
      return;
    }

    try {
      setDeletingStrategy(strategyId);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/strategies/${strategyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        // Eliminar de la lista local
        setStrategies(prev => prev.filter(s => s.id !== strategyId));
      } else {
        const errorData = await response.json();
        alert(errorData.detail || 'Error eliminando estrategia');
      }
    } catch (err) {
      alert('Error de conexión al eliminar estrategia');
    } finally {
      setDeletingStrategy(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStrategyTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'threshold': 'Umbrales',
      'crossover': 'Cruce de Medias',
      'multi_dataset_crossover': 'Cruce Multi-Dataset'
    };
    return labels[type] || type;
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto p-4">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando estrategias...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <TrendingUp className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Estrategias Guardadas</h1>
        </div>
        <Button 
          onClick={fetchStrategies} 
          disabled={isLoading}
          variant="outline" 
          size="sm" 
          className="flex items-center gap-2 bg-transparent"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Actualizar
        </Button>
      </div>

      <p className="text-gray-600 mb-6">Estrategias de backtesting compartidas por todos los usuarios</p>

      {/* Error */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-gray-200 shadow-sm">
          <CardContent className="px-4 py-3">
            <div className="text-2xl font-bold text-gray-900">{strategies.length}</div>
            <div className="text-sm text-gray-600">Total Estrategias</div>
          </CardContent>
        </Card>
        <Card className="border-gray-200 shadow-sm">
          <CardContent className="px-4 py-3">
            <div className="text-2xl font-bold text-gray-900">
              {strategies.filter(s => s.net_pnl > 0).length}
            </div>
            <div className="text-sm text-gray-600">Estrategias Rentables</div>
          </CardContent>
        </Card>
        <Card className="border-gray-200 shadow-sm">
          <CardContent className="px-4 py-3">
            <div className="text-2xl font-bold text-gray-900">
              {strategies.length > 0 ? 
                Math.round(strategies.reduce((sum, s) => sum + s.num_trades, 0) / strategies.length) : 0
              }
            </div>
            <div className="text-sm text-gray-600">Promedio Operaciones</div>
          </CardContent>
        </Card>
        <Card className="border-gray-200 shadow-sm">
          <CardContent className="px-4 py-3">
            <div className="text-2xl font-bold text-gray-900">
              {strategies.length > 0 ? 
                formatCurrency(strategies.reduce((sum, s) => sum + s.net_pnl, 0)) : '$0'
              }
            </div>
            <div className="text-sm text-gray-600">P&L Total Acumulado</div>
          </CardContent>
        </Card>
      </div>

      {/* Strategies Table */}
      <Card className="border-green-100 shadow-sm">
        <div className="bg-green-50/50 min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
          <div className="flex items-center gap-2 text-lg text-green-900 font-semibold">
            <TrendingUp className="h-5 w-5" />
            Estrategias
          </div>
        </div>
        <CardContent className="px-4 py-1">
          <p className="text-sm text-gray-600 mb-4">Lista de todas las estrategias guardadas por los usuarios</p>

          {strategies.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No hay estrategias guardadas aún.</p>
              <p className="text-sm text-muted-foreground mt-2">
                Ejecuta un backtest y guárdalo para que aparezca aquí.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-2 font-medium text-gray-700">Fecha</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-700">Usuario</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-700">Tipo</th>
                    <th className="text-center py-3 px-2 font-medium text-gray-700">Operaciones</th>
                    <th className="text-right py-3 px-2 font-medium text-gray-700">P&L</th>
                    <th className="text-right py-3 px-2 font-medium text-gray-700">Costes</th>
                    <th className="text-right py-3 px-2 font-medium text-gray-700">P&L Neto</th>
                    <th className="text-center py-3 px-2 font-medium text-gray-700">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {strategies.map((strategy) => (
                    <React.Fragment key={strategy.id}>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-2 text-gray-600">{formatDate(strategy.created_at)}</td>
                        <td className="py-3 px-2">
                          <Badge variant="secondary" className="text-xs">
                            {strategy.username}
                          </Badge>
                        </td>
                        <td className="py-3 px-2 text-gray-700 max-w-xs">
                          <div className="truncate" title={strategy.formatted_config.strategy_description}>
                            {strategy.formatted_config.strategy_description}
                          </div>
                        </td>
                        <td className="py-3 px-2 text-center text-gray-700">{strategy.num_trades}</td>
                        <td className={`py-3 px-2 text-right font-medium ${strategy.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(strategy.total_pnl)}
                        </td>
                        <td className="py-3 px-2 text-right text-orange-600">
                          {formatCurrency(strategy.total_costs)}
                        </td>
                        <td className={`py-3 px-2 text-right font-medium ${strategy.net_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(strategy.net_pnl)}
                        </td>
                        <td className="py-3 px-2">
                          <div className="flex items-center justify-start gap-1">
                            <Button
                              onClick={() => setExpandedStrategy(expandedStrategy === strategy.id ? null : strategy.id)}
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 hover:bg-blue-100"
                              title="Ver configuración"
                            >
                              <Eye className="h-4 w-4 text-blue-600" />
                            </Button>
                            {strategy.user_id === currentUserId && (
                              <Button
                                onClick={() => deleteStrategy(strategy.id)}
                                disabled={deletingStrategy === strategy.id}
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0 hover:bg-red-100"
                                title="Eliminar estrategia"
                              >
                                {deletingStrategy === strategy.id ? (
                                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                                ) : (
                                  <Trash2 className="h-4 w-4 text-red-600" />
                                )}
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                      {expandedStrategy === strategy.id && (
                        <tr>
                          <td colSpan={8} className="bg-gray-50 p-4">
                            <div className="space-y-4">
                              <h4 className="font-semibold text-gray-900">Configuración Detallada</h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                <div>
                                  <p><strong>Tipo de estrategia:</strong> {strategy.formatted_config.strategy_description}</p>
                                  <p><strong>Dataset:</strong> {strategy.formatted_config.dataset_name}</p>
                                  <p><strong>Período:</strong> {strategy.formatted_config.period}</p>
                                  <p><strong>Comisiones:</strong> {strategy.formatted_config.fees_percentage}</p>
                                  <p><strong>Capital inicial:</strong> {strategy.formatted_config.init_cash_formatted}</p>
                                  <p><strong>Aplicar a:</strong> {strategy.formatted_config.apply_to === 'v' ? 'Indicador' : 'Precio'}</p>
                                </div>
                                <div>
                                  {strategy.formatted_config.transformations.length > 0 && (
                                    <div>
                                      <p><strong>Transformaciones:</strong></p>
                                      <ul className="list-disc list-inside ml-2">
                                        {strategy.formatted_config.transformations.map((transform, index) => (
                                          <li key={index}>{transform}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  {strategy.formatted_config.thresholds && (
                                    <div>
                                      <p><strong>Umbrales:</strong></p>
                                      <p className="ml-2">Entrada: {strategy.formatted_config.thresholds.entry}</p>
                                      <p className="ml-2">Salida: {strategy.formatted_config.thresholds.exit}</p>
                                    </div>
                                  )}
                                  {strategy.formatted_config.crossover_details && (
                                    <div>
                                      <p><strong>Detalles de cruce:</strong></p>
                                      <p className="ml-2">{strategy.formatted_config.crossover_details}</p>
                                    </div>
                                  )}
                                  {strategy.formatted_config.bitcoin_condition && (
                                    <div>
                                      <p><strong>Condiciones de Bitcoin:</strong></p>
                                      <p className="ml-2 text-blue-600">{strategy.formatted_config.bitcoin_condition}</p>
                                    </div>
                                  )}
                                </div>
                              </div>
                              
                              {/* Comentarios */}
                              {strategy.comments && (
                                <div className="mt-4 pt-4 border-t border-gray-200">
                                  <p><strong>Comentarios:</strong></p>
                                  <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">{strategy.comments}</p>
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default StrategiesPage;
