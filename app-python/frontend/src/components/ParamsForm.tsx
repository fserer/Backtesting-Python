import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Settings, Play, Database, TrendingUp, TrendingDown, Calendar, ArrowUp, ArrowDown } from 'lucide-react';
import { TransformConfig, Dataset, CrossoverStrategy } from '@/lib/api';

interface ParamsFormProps {
  onSubmit: (params: any) => void;
  isRunning: boolean;
  selectedDataset?: Dataset;
}

export function ParamsForm({ onSubmit, isRunning, selectedDataset }: ParamsFormProps) {
  const [formData, setFormData] = React.useState({
    dataset_id: 0,
    transform: {
      v: { type: 'none' as const, period: 1 },
      usd: { type: 'none' as const, period: 1 }
    },
    apply_to: 'v' as 'v' | 'usd',
    strategy_type: 'threshold' as 'threshold' | 'crossover',
    threshold_entry: 0,
    threshold_exit: 0,
    crossover_strategy: {
      entry_fast_period: 7,
      entry_slow_period: 30,
      exit_fast_period: 7,
      exit_slow_period: 14,
      entry_type: 'sma' as 'sma' | 'ema',
      exit_type: 'sma' as 'sma' | 'ema',
      entry_direction: 'up' as 'up' | 'down',
      exit_direction: 'down' as 'up' | 'down'
    },
    period: 'all' as '1w' | '1m' | '3m' | '6m' | '1y' | 'ytd' | '2y' | '4y' | '6y' | '8y' | '10y' | 'all',
    fees: 0.0005,
    slippage: 0.0002,
    init_cash: 10000
  });

  // Actualizar dataset_id cuando cambie el dataset seleccionado
  React.useEffect(() => {
    if (selectedDataset) {
      setFormData(prev => ({ ...prev, dataset_id: selectedDataset.id }));
    }
  }, [selectedDataset]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const updateTransform = (field: 'v' | 'usd', key: keyof TransformConfig, value: any) => {
    setFormData(prev => ({
      ...prev,
      transform: {
        ...prev.transform,
        [field]: {
          ...prev.transform[field],
          [key]: value
        }
      }
    }));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Parámetros del Backtest
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dataset seleccionado */}
          {selectedDataset ? (
            <div className="p-3 border rounded-lg bg-blue-50">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">
                  Dataset: {selectedDataset.name}
                </span>
              </div>
              <p className="text-xs text-blue-600 mt-1">
                {selectedDataset.row_count.toLocaleString()} registros
              </p>
            </div>
          ) : (
            <div className="p-3 border rounded-lg bg-yellow-50">
              <p className="text-sm text-yellow-800">
                ⚠️ Selecciona un dataset para ejecutar el backtest
              </p>
            </div>
          )}

          {/* Transformaciones */}
          <div className="space-y-4">
            <h4 className="font-medium">Transformaciones</h4>
            
            {/* Transformación para 'v' */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="v-transform">Indicador (v)</Label>
                <Select
                  value={formData.transform.v.type}
                  onValueChange={(value) => updateTransform('v', 'type', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Ninguna</SelectItem>
                    <SelectItem value="sma">SMA</SelectItem>
                    <SelectItem value="ema">EMA</SelectItem>
                    <SelectItem value="median">Mediana</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="v-period">Período</Label>
                <Input
                  id="v-period"
                  type="number"
                  min="1"
                  value={formData.transform.v.period}
                  onChange={(e) => updateTransform('v', 'period', parseInt(e.target.value) || 1)}
                  disabled={formData.transform.v.type === 'none'}
                />
              </div>
            </div>

            {/* Transformación para 'usd' */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="usd-transform">Precio (USD)</Label>
                <Select
                  value={formData.transform.usd.type}
                  onValueChange={(value) => updateTransform('usd', 'type', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Ninguna</SelectItem>
                    <SelectItem value="sma">SMA</SelectItem>
                    <SelectItem value="ema">EMA</SelectItem>
                    <SelectItem value="median">Mediana</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="usd-period">Período</Label>
                <Input
                  id="usd-period"
                  type="number"
                  min="1"
                  value={formData.transform.usd.period}
                  onChange={(e) => updateTransform('usd', 'period', parseInt(e.target.value) || 1)}
                  disabled={formData.transform.usd.type === 'none'}
                />
              </div>
            </div>
          </div>

          {/* Aplicar señales a */}
          <div>
            <Label htmlFor="apply-to">Aplicar señales a</Label>
            <Select
              value={formData.apply_to}
              onValueChange={(value) => setFormData(prev => ({ ...prev, apply_to: value as 'v' | 'usd' }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="v">Indicador (v)</SelectItem>
                <SelectItem value="usd">Precio (USD)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Tipo de Estrategia */}
          <div>
            <Label htmlFor="strategy-type">Tipo de Estrategia</Label>
            <Select
              value={formData.strategy_type}
              onValueChange={(value) => setFormData(prev => ({ ...prev, strategy_type: value as 'threshold' | 'crossover' }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="threshold">Umbrales</SelectItem>
                <SelectItem value="crossover">Cruces de Medias Móviles</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Período de Backtesting */}
          <div>
            <Label htmlFor="period" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Período de Backtesting
            </Label>
            <Select
              value={formData.period}
              onValueChange={(value) => setFormData(prev => ({ ...prev, period: value as any }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1w">Última Semana</SelectItem>
                <SelectItem value="1m">Último Mes</SelectItem>
                <SelectItem value="3m">Último Trimestre</SelectItem>
                <SelectItem value="6m">Últimos 6 Meses</SelectItem>
                <SelectItem value="1y">Último Año</SelectItem>
                <SelectItem value="ytd">Este Año (YTD)</SelectItem>
                <SelectItem value="2y">Últimos 2 Años</SelectItem>
                <SelectItem value="4y">Últimos 4 Años</SelectItem>
                <SelectItem value="6y">Últimos 6 Años</SelectItem>
                <SelectItem value="8y">Últimos 8 Años</SelectItem>
                <SelectItem value="10y">Últimos 10 Años</SelectItem>
                <SelectItem value="all">Todo el Tiempo</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Umbrales - Solo para estrategia threshold */}
          {formData.strategy_type === 'threshold' && (
            <div className="space-y-4">
              <h4 className="font-medium">Umbrales</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="threshold-entry">Umbral de Entrada</Label>
                  <Input
                    id="threshold-entry"
                    type="number"
                    step="0.01"
                    value={formData.threshold_entry}
                    onChange={(e) => setFormData(prev => ({ ...prev, threshold_entry: parseFloat(e.target.value) || 0 }))}
                  />
                </div>
                <div>
                  <Label htmlFor="threshold-exit">Umbral de Salida</Label>
                  <Input
                    id="threshold-exit"
                    type="number"
                    step="0.01"
                    value={formData.threshold_exit}
                    onChange={(e) => setFormData(prev => ({ ...prev, threshold_exit: parseFloat(e.target.value) || 0 }))}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Cruces de Medias Móviles - Solo para estrategia crossover */}
          {formData.strategy_type === 'crossover' && (
            <div className="space-y-4">
              <h4 className="font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Cruces de Medias Móviles
              </h4>
              
              {/* Selector de serie a analizar */}
              <div className="space-y-2">
                <Label htmlFor="crossover-series" className="text-sm font-medium">Aplicar cruces sobre:</Label>
                <Select
                  value={formData.apply_to}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, apply_to: value as 'v' | 'usd' }))}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="v">Indicador (v)</SelectItem>
                    <SelectItem value="usd">Precio Bitcoin (usd)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {/* Configuración de Entrada */}
              <div className="space-y-3">
                <h5 className="text-sm font-medium text-green-700 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Señales de Entrada
                </h5>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="entry-fast" className="text-sm font-medium h-5 flex items-center">Período Rápido</Label>
                    <Input
                      id="entry-fast"
                      type="number"
                      min="1"
                      value={formData.crossover_strategy.entry_fast_period}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        crossover_strategy: {
                          ...prev.crossover_strategy,
                          entry_fast_period: parseInt(e.target.value) || 7
                        }
                      }))}
                      className="w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="entry-slow" className="text-sm font-medium h-5 flex items-center">Período Lento</Label>
                    <Input
                      id="entry-slow"
                      type="number"
                      min="1"
                      value={formData.crossover_strategy.entry_slow_period}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        crossover_strategy: {
                          ...prev.crossover_strategy,
                          entry_slow_period: parseInt(e.target.value) || 30
                        }
                      }))}
                      className="w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="entry-type" className="text-sm font-medium h-5 flex items-center">Tipo</Label>
                    <Select
                      value={formData.crossover_strategy.entry_type}
                      onValueChange={(value) => setFormData(prev => ({
                        ...prev,
                        crossover_strategy: {
                          ...prev.crossover_strategy,
                          entry_type: value as 'sma' | 'ema'
                        }
                      }))}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sma">SMA</SelectItem>
                        <SelectItem value="ema">EMA</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="entry-direction" className="text-sm font-medium h-5 flex items-center gap-1">
                      <ArrowUp className="h-3 w-3" />
                      Dirección
                    </Label>
                    <Select
                      value={formData.crossover_strategy.entry_direction}
                      onValueChange={(value) => setFormData(prev => ({
                        ...prev,
                        crossover_strategy: {
                          ...prev.crossover_strategy,
                          entry_direction: value as 'up' | 'down'
                        }
                      }))}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="up">Al Alza</SelectItem>
                        <SelectItem value="down">A la Baja</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              {/* Configuración de Salida */}
              <div className="space-y-3">
                <h5 className="text-sm font-medium text-red-700 flex items-center gap-2">
                  <TrendingDown className="h-4 w-4" />
                  Señales de Salida
                </h5>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="exit-fast" className="text-sm font-medium h-5 flex items-center">Período Rápido</Label>
                    <Input
                      id="exit-fast"
                      type="number"
                      min="1"
                      value={formData.crossover_strategy.exit_fast_period}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        crossover_strategy: {
                          ...prev.crossover_strategy,
                          exit_fast_period: parseInt(e.target.value) || 7
                        }
                      }))}
                      className="w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="exit-slow" className="text-sm font-medium h-5 flex items-center">Período Lento</Label>
                    <Input
                      id="exit-slow"
                      type="number"
                      min="1"
                      value={formData.crossover_strategy.exit_slow_period}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        crossover_strategy: {
                          ...prev.crossover_strategy,
                          exit_slow_period: parseInt(e.target.value) || 14
                        }
                      }))}
                      className="w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="exit-type" className="text-sm font-medium h-5 flex items-center">Tipo</Label>
                    <Select
                      value={formData.crossover_strategy.exit_type}
                      onValueChange={(value) => setFormData(prev => ({
                        ...prev,
                        crossover_strategy: {
                          ...prev.crossover_strategy,
                          exit_type: value as 'sma' | 'ema'
                        }
                      }))}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sma">SMA</SelectItem>
                        <SelectItem value="ema">EMA</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="exit-direction" className="text-sm font-medium h-5 flex items-center gap-1">
                      <ArrowDown className="h-3 w-3" />
                      Dirección
                    </Label>
                    <Select
                      value={formData.crossover_strategy.exit_direction}
                      onValueChange={(value) => setFormData(prev => ({
                        ...prev,
                        crossover_strategy: {
                          ...prev.crossover_strategy,
                          exit_direction: value as 'up' | 'down'
                        }
                      }))}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="up">Al Alza</SelectItem>
                        <SelectItem value="down">A la Baja</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Comisiones y Slippage */}
          <div className="space-y-3">
            <h5 className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Configuración de Trading
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="fees" className="text-sm font-medium">Comisiones (%)</Label>
                <Input
                  id="fees"
                  type="number"
                  step="0.0001"
                  min="0"
                  max="0.1"
                  value={formData.fees * 100}
                  onChange={(e) => setFormData(prev => ({ ...prev, fees: (parseFloat(e.target.value) || 0) / 100 }))}
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="slippage" className="text-sm font-medium">Slippage (%)</Label>
                <Input
                  id="slippage"
                  type="number"
                  step="0.0001"
                  min="0"
                  max="0.1"
                  value={formData.slippage * 100}
                  onChange={(e) => setFormData(prev => ({ ...prev, slippage: (parseFloat(e.target.value) || 0) / 100 }))}
                  className="w-full"
                />
              </div>
            </div>
          </div>

          {/* Capital inicial */}
          <div className="space-y-2">
            <Label htmlFor="init-cash" className="text-sm font-medium">Capital Inicial ($)</Label>
            <Input
              id="init-cash"
              type="number"
              min="1"
              value={formData.init_cash}
              onChange={(e) => setFormData(prev => ({ ...prev, init_cash: parseFloat(e.target.value) || 10000 }))}
              className="w-full"
            />
          </div>

          {/* Botón de envío */}
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isRunning || !selectedDataset}
          >
            {isRunning ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Ejecutando...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                {selectedDataset ? 'Ejecutar Backtest' : 'Selecciona un Dataset'}
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
