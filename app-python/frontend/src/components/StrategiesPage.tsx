import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Badge } from './ui/badge';
import { Eye, RefreshCw, Trash2 } from 'lucide-react';
import { formatCurrency, formatPercentage } from '../lib/utils';

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
      <div className="min-h-screen bg-background p-8">
        <div className="container mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Cargando estrategias...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="container mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Estrategias Guardadas</h1>
              <p className="text-muted-foreground mt-2">
                Estrategias de backtesting compartidas por todos los usuarios
              </p>
            </div>
            <Button
              onClick={fetchStrategies}
              disabled={isLoading}
              variant="outline"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Actualizar
            </Button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{strategies.length}</div>
              <div className="text-sm text-muted-foreground">Total Estrategias</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {strategies.filter(s => s.net_pnl > 0).length}
              </div>
              <div className="text-sm text-muted-foreground">Estrategias Rentables</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {strategies.length > 0 ? 
                  Math.round(strategies.reduce((sum, s) => sum + s.num_trades, 0) / strategies.length) : 0
                }
              </div>
              <div className="text-sm text-muted-foreground">Promedio Operaciones</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {strategies.length > 0 ? 
                  formatCurrency(strategies.reduce((sum, s) => sum + s.net_pnl, 0)) : '$0'
                }
              </div>
              <div className="text-sm text-muted-foreground">P&L Total Acumulado</div>
            </CardContent>
          </Card>
        </div>

        {/* Tabla de estrategias */}
        <Card>
          <CardHeader>
            <CardTitle>Estrategias</CardTitle>
            <CardDescription>
              Lista de todas las estrategias guardadas por los usuarios
            </CardDescription>
          </CardHeader>
          <CardContent>
            {strategies.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No hay estrategias guardadas aún.</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Ejecuta un backtest y guárdalo para que aparezca aquí.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Fecha</TableHead>
                      <TableHead>Usuario</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead className="text-right">Operaciones</TableHead>
                      <TableHead className="text-right">P&L</TableHead>
                      <TableHead className="text-right">Costes</TableHead>
                      <TableHead className="text-right">P&L Neto</TableHead>
                      <TableHead className="text-right">Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {strategies.map((strategy) => (
                      <React.Fragment key={strategy.id}>
                        <TableRow>
                          <TableCell className="font-mono text-sm">
                            {formatDate(strategy.created_at)}
                          </TableCell>
                          <TableCell>
                            <span className="font-medium">{strategy.username}</span>
                          </TableCell>

                          <TableCell>
                            <Badge variant="secondary">
                              {strategy.formatted_config.strategy_description}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right font-mono">
                            {strategy.num_trades}
                          </TableCell>
                          <TableCell className={`text-right font-mono ${strategy.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatCurrency(strategy.total_pnl)}
                          </TableCell>
                          <TableCell className="text-right font-mono text-orange-600">
                            {formatCurrency(strategy.total_costs)}
                          </TableCell>
                          <TableCell className={`text-right font-mono font-semibold ${strategy.net_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatCurrency(strategy.net_pnl)}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setExpandedStrategy(expandedStrategy === strategy.id ? null : strategy.id)}
                                title="Ver configuración"
                              >
                                <Eye className="h-3 w-3" />
                              </Button>
                              {strategy.user_id === currentUserId && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => deleteStrategy(strategy.id)}
                                  disabled={deletingStrategy === strategy.id}
                                  title="Eliminar estrategia"
                                  className="text-red-600 hover:text-red-700"
                                >
                                  {deletingStrategy === strategy.id ? (
                                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-red-600"></div>
                                  ) : (
                                    <Trash2 className="h-3 w-3" />
                                  )}
                                </Button>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                        {expandedStrategy === strategy.id && (
                          <TableRow>
                            <TableCell colSpan={8} className="bg-gray-50 p-4">
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
                            </TableCell>
                          </TableRow>
                        )}
                      </React.Fragment>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StrategiesPage;
