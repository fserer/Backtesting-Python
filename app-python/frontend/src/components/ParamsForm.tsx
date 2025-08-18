import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Settings, Play, Database, TrendingUp, TrendingDown, Calendar, ArrowUp, ArrowDown } from 'lucide-react';
import { TransformConfig, Dataset, CrossoverStrategy, MultiDatasetCrossoverStrategy } from '@/lib/api';
import { MultiDatasetSelector } from './MultiDatasetSelector';

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
    strategy_type: 'threshold' as 'threshold' | 'crossover' | 'multi_dataset_crossover',
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
    multi_dataset_crossover_strategy: {
      dataset1_id: 0,
      dataset1_indicator: 'v' as 'v' | 'usd',
      dataset1_ma_type: 'sma' as 'sma' | 'ema',
      dataset1_ma_period: 7,
      dataset2_id: 0,
      dataset2_indicator: 'v' as 'v' | 'usd',
      dataset2_ma_type: 'sma' as 'sma' | 'ema',
      dataset2_ma_period: 30,
      entry_direction: 'up' as 'up' | 'down',
      exit_direction: 'down' as 'up' | 'down',
      price_dataset_id: 0,
      take_profit_pct: 3.0,
      stop_loss_pct: 1.0,
      use_take_profit: true,
      use_stop_loss: true
    },
    period: '1y' as '1w' | '1m' | '3m' | '6m' | '1y' | 'ytd' | '2y' | '4y' | '6y' | '8y' | '10y' | '2015' | '2016' | '2017' | '2018' | '2019' | '2020' | '2021' | '2022' | '2023' | '2024' | '2025' | 'all',
    fees: 0.00045,
    slippage: 0.0002,
    init_cash: 10000
  });

  // Estado para datasets múltiples
  const [selectedDataset1, setSelectedDataset1] = React.useState<Dataset | null>(null);
  const [selectedDataset2, setSelectedDataset2] = React.useState<Dataset | null>(null);
  const [selectedPriceDataset, setSelectedPriceDataset] = React.useState<Dataset | null>(null);
  const [datasets, setDatasets] = React.useState<Dataset[]>([]);

  // Cargar datasets al montar el componente
  React.useEffect(() => {
    const loadDatasets = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/datasets');
        if (response.ok) {
          const data = await response.json();
          setDatasets(data);
        }
      } catch (error) {
        console.error('Error cargando datasets:', error);
      }
    };
    loadDatasets();
  }, []);

  // Actualizar dataset_id cuando cambie el dataset seleccionado
  React.useEffect(() => {
    if (selectedDataset) {
      setFormData(prev => ({ ...prev, dataset_id: selectedDataset.id }));
    }
  }, [selectedDataset]);

  // Actualizar estrategia multi-dataset cuando cambien los datasets seleccionados
  React.useEffect(() => {
    if (selectedDataset1) {
      setFormData(prev => ({
        ...prev,
        multi_dataset_crossover_strategy: {
          ...prev.multi_dataset_crossover_strategy,
          dataset1_id: selectedDataset1.id
        }
      }));
    }
  }, [selectedDataset1]);

  React.useEffect(() => {
    if (selectedDataset2) {
      setFormData(prev => ({
        ...prev,
        multi_dataset_crossover_strategy: {
          ...prev.multi_dataset_crossover_strategy,
          dataset2_id: selectedDataset2.id
        }
      }));
    }
  }, [selectedDataset2]);

  React.useEffect(() => {
    if (selectedPriceDataset) {
      setFormData(prev => ({
        ...prev,
        multi_dataset_crossover_strategy: {
          ...prev.multi_dataset_crossover_strategy,
          price_dataset_id: selectedPriceDataset.id
        }
      }));
    }
  }, [selectedPriceDataset]);

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

  const updateMultiDatasetStrategy = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      multi_dataset_crossover_strategy: {
        ...prev.multi_dataset_crossover_strategy,
        [field]: value
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
              onValueChange={(value) => setFormData(prev => ({ ...prev, strategy_type: value as 'threshold' | 'crossover' | 'multi_dataset_crossover' }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="threshold">Umbrales</SelectItem>
                <SelectItem value="crossover">Cruces de Medias Móviles</SelectItem>
                <SelectItem value="multi_dataset_crossover">Cruce entre Datasets</SelectItem>
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
                <SelectItem value="ytd">Este Año (YTD)</SelectItem>
                <SelectItem value="1y">Último Año</SelectItem>
                <SelectItem value="2y">Últimos 2 Años</SelectItem>
                <SelectItem value="3y">Últimos 3 Años</SelectItem>
                <SelectItem value="4y">Últimos 4 Años</SelectItem>
                <SelectItem value="5y">Últimos 5 Años</SelectItem>
                <SelectItem value="6y">Últimos 6 Años</SelectItem>
                <SelectItem value="7y">Últimos 7 Años</SelectItem>
                <SelectItem value="8y">Últimos 8 Años</SelectItem>
                <SelectItem value="9y">Últimos 9 Años</SelectItem>
                <SelectItem value="10y">Últimos 10 Años</SelectItem>
                <SelectItem value="2025">Año 2025</SelectItem>
                <SelectItem value="2024">Año 2024</SelectItem>
                <SelectItem value="2023">Año 2023</SelectItem>
                <SelectItem value="2022">Año 2022</SelectItem>
                <SelectItem value="2021">Año 2021</SelectItem>
                <SelectItem value="2020">Año 2020</SelectItem>
                <SelectItem value="2019">Año 2019</SelectItem>
                <SelectItem value="2018">Año 2018</SelectItem>
                <SelectItem value="2017">Año 2017</SelectItem>
                <SelectItem value="2016">Año 2016</SelectItem>
                <SelectItem value="2015">Año 2015</SelectItem>
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

          {/* Cruce entre Datasets - Solo para estrategia multi_dataset_crossover */}
          {formData.strategy_type === 'multi_dataset_crossover' && (
            <MultiDatasetSelector
              datasets={datasets}
              selectedDataset1={selectedDataset1}
              selectedDataset2={selectedDataset2}
              selectedPriceDataset={selectedPriceDataset}
              onDataset1Select={setSelectedDataset1}
              onDataset2Select={setSelectedDataset2}
              onPriceDatasetSelect={setSelectedPriceDataset}
              strategy={{
                dataset1_indicator: formData.multi_dataset_crossover_strategy.dataset1_indicator,
                dataset1_ma_type: formData.multi_dataset_crossover_strategy.dataset1_ma_type,
                dataset1_ma_period: formData.multi_dataset_crossover_strategy.dataset1_ma_period,
                dataset2_indicator: formData.multi_dataset_crossover_strategy.dataset2_indicator,
                dataset2_ma_type: formData.multi_dataset_crossover_strategy.dataset2_ma_type,
                dataset2_ma_period: formData.multi_dataset_crossover_strategy.dataset2_ma_period,
                entry_direction: formData.multi_dataset_crossover_strategy.entry_direction,
                exit_direction: formData.multi_dataset_crossover_strategy.exit_direction,
                take_profit_pct: formData.multi_dataset_crossover_strategy.take_profit_pct,
                stop_loss_pct: formData.multi_dataset_crossover_strategy.stop_loss_pct,
                use_take_profit: formData.multi_dataset_crossover_strategy.use_take_profit,
                use_stop_loss: formData.multi_dataset_crossover_strategy.use_stop_loss
              }}
              onStrategyChange={updateMultiDatasetStrategy}
            />
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
            disabled={
              isRunning || 
              !selectedDataset || 
              (formData.strategy_type === 'multi_dataset_crossover' && 
               (!selectedDataset1 || !selectedDataset2 || !selectedPriceDataset))
            }
          >
            {isRunning ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Ejecutando...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                {!selectedDataset ? 'Selecciona un Dataset' : 
                 formData.strategy_type === 'multi_dataset_crossover' && (!selectedDataset1 || !selectedDataset2 || !selectedPriceDataset) ? 
                 'Selecciona todos los Datasets' : 'Ejecutar Backtest'}
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
