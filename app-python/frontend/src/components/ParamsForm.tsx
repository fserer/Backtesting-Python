import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from './ui/command';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Settings, Play, Database, TrendingUp, TrendingDown, Calendar, ArrowUp, ArrowDown, Bitcoin, BarChart3, Search, Target } from 'lucide-react';
import { TransformConfig, Dataset, CrossoverStrategy, MultiDatasetCrossoverStrategy, BitcoinPriceCondition } from '../lib/api';
import { API_BASE_URL } from '../config';
import { MultiDatasetSelector } from './MultiDatasetSelector';
import { CompositeStrategyFlowBuilder } from './CompositeStrategyFlowBuilder';

interface ParamsFormProps {
  onSubmit: (params: any) => void;
  isRunning: boolean;
  selectedDataset?: Dataset;
  onDatasetSelect?: (dataset: Dataset) => void;
  formState?: any;
  onFormStateChange?: (state: any) => void;
}

export function ParamsForm({ onSubmit, isRunning, selectedDataset, onDatasetSelect, formState, onFormStateChange }: ParamsFormProps) {
  const [formData, setFormData] = React.useState(() => {
    // Usar el estado global si está disponible, sino usar valores por defecto
    if (formState) {
      return formState;
    }
    return {
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
      bitcoin_price_condition: {
        enabled: false,
        ma_type: 'sma' as 'sma' | 'ema',
        ma_period: 50,
        condition: 'above' as 'above' | 'below'
      },
      period: '1y' as '1w' | '1m' | '3m' | '6m' | '1y' | 'ytd' | '2y' | '4y' | '6y' | '8y' | '10y' | '2015' | '2016' | '2017' | '2018' | '2019' | '2020' | '2021' | '2022' | '2023' | '2024' | '2025' | 'all',
      fees: 0.00045,
      slippage: 0.0002,
      init_cash: 10000
    };
  });

  // Estado para datasets múltiples
  const [selectedDataset1, setSelectedDataset1] = React.useState<Dataset | null>(null);
  const [selectedDataset2, setSelectedDataset2] = React.useState<Dataset | null>(null);
  const [selectedPriceDataset, setSelectedPriceDataset] = React.useState<Dataset | null>(null);
  const [datasets, setDatasets] = React.useState<Dataset[]>([]);
  const [datasetOpen, setDatasetOpen] = React.useState(false);
  
  // Estado para estrategia simple vs compuesta
  const [strategyMode, setStrategyMode] = React.useState<'simple' | 'composite'>('simple');
  const [compositeStrategy, setCompositeStrategy] = React.useState<any>(null);

  // Cargar datasets al montar el componente
  React.useEffect(() => {
    const loadDatasets = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/datasets`);
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

  // Función para actualizar tanto el estado local como el global
  const updateFormData = (updater: (prev: any) => any) => {
    const newFormData = updater(formData);
    setFormData(newFormData);
    
    // Actualizar el estado global si existe
    if (onFormStateChange) {
      onFormStateChange(newFormData);
    }
  };

  React.useEffect(() => {
    if (selectedDataset) {
      updateFormData((prev: any) => ({
        ...prev,
        dataset_id: selectedDataset.id
      }));
    }
  }, [selectedDataset]);

  const getPeriodDescription = (period: string) => {
    const periodMap: { [key: string]: string } = {
      '1w': 'Última semana',
      '1m': 'Último mes',
      '3m': 'Últimos 3 meses',
      '6m': 'Últimos 6 meses',
      '1y': 'Último año',
      'ytd': 'Año hasta la fecha',
      '2y': 'Últimos 2 años',
      '4y': 'Últimos 4 años',
      '6y': 'Últimos 6 años',
      '8y': 'Últimos 8 años',
      '9y': 'Últimos 9 Años',
      '10y': 'Últimos 10 Años',
      '2025': 'Año 2025',
      '2024': 'Año 2024',
      '2023': 'Año 2023',
      '2022': 'Año 2022',
      '2021': 'Año 2021',
      '2020': 'Año 2020',
      '2019': 'Año 2019',
      '2018': 'Año 2018',
      '2017': 'Año 2017',
      '2016': 'Año 2016',
      '2015': 'Año 2015',
      'all': 'Todo el Tiempo'
    };
    return periodMap[period] || period;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (strategyMode === 'composite') {
      // Para estrategias compuestas, usar el Flow Builder
      if (compositeStrategy) {
        onSubmit(compositeStrategy);
      }
      return;
    }
    
    // Para estrategias simples, usar el formulario tradicional
    const paramsWithMetadata = {
      ...formData,
      dataset_name: selectedDataset?.name || '',
      period_description: getPeriodDescription(formData.period)
    };
    
    onSubmit(paramsWithMetadata);
  };

  const updateTransform = (field: 'v' | 'usd', key: keyof TransformConfig, value: any) => {
    updateFormData((prev: any) => ({
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
    updateFormData((prev: any) => ({
      ...prev,
      multi_dataset_crossover_strategy: {
        ...prev.multi_dataset_crossover_strategy,
        [field]: value
      }
    }));
  };

  const updateBitcoinPriceCondition = (field: string, value: any) => {
    updateFormData((prev: any) => ({
      ...prev,
      bitcoin_price_condition: {
        ...prev.bitcoin_price_condition,
        [field]: value
      }
    }));
  };

  const selectedDatasetInfo = selectedDataset;

  return (
    <div className="max-w-7xl mx-auto p-4">
      <div className="flex items-center gap-3 mb-4">
        <Settings className="h-6 w-6 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">Configuración del Backtest</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Selector de Modo de Estrategia */}
        <Card className="border-indigo-100 shadow-sm">
          <div className="bg-indigo-50/50 min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
            <div className="flex items-center gap-2 text-lg text-indigo-900 font-semibold">
              <Target className="h-5 w-5" />
              Modo de Estrategia
            </div>
          </div>
          <CardContent className="px-4 py-6">
            <div className="flex items-center gap-4">
              <div className="flex items-center space-x-2">
                <input
                  type="radio"
                  id="simple-strategy"
                  name="strategy-mode"
                  value="simple"
                  checked={strategyMode === 'simple'}
                  onChange={(e) => setStrategyMode(e.target.value as 'simple' | 'composite')}
                  className="h-4 w-4 text-indigo-600"
                />
                <Label htmlFor="simple-strategy" className="text-sm font-medium text-gray-700">
                  Estrategia Simple
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="radio"
                  id="composite-strategy"
                  name="strategy-mode"
                  value="composite"
                  checked={strategyMode === 'composite'}
                  onChange={(e) => setStrategyMode(e.target.value as 'simple' | 'composite')}
                  className="h-4 w-4 text-indigo-600"
                />
                <Label htmlFor="composite-strategy" className="text-sm font-medium text-gray-700">
                  Estrategia Compuesta (Flow Builder)
                </Label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contenido condicional */}
        {strategyMode === 'simple' ? (
          <>
            {/* Parámetros del Backtest */}
            <Card className="border-blue-100 shadow-sm">
              <div className="bg-blue-50/50 min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
                <div className="flex items-center gap-2 text-lg text-blue-900 font-semibold">
                  <BarChart3 className="h-5 w-5" />
                  Parámetros del backtest
                </div>
              </div>
              <CardContent className="px-4 py-6 space-y-4">
                {/* Dataset selector and other parameters */}
                <div className="space-y-3">
                  <div className="space-y-2">
                    <Label htmlFor="dataset" className="text-sm font-medium text-gray-700">
                      Dataset
                    </Label>
                    <Popover open={datasetOpen} onOpenChange={setDatasetOpen}>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          role="combobox"
                          aria-expanded={datasetOpen}
                          className="w-full justify-between h-12 px-4 py-3 bg-transparent"
                        >
                          <div className="text-left">
                            <div className="font-medium text-blue-700 text-sm">
                              {selectedDatasetInfo ? selectedDatasetInfo.name : "Selecciona un dataset para hacer backtesting"}
                            </div>
                            <div className="text-xs text-gray-500">
                              {selectedDatasetInfo ? `${selectedDatasetInfo.row_count.toLocaleString()} registros` : ""}
                            </div>
                          </div>
                          <Search className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start" side="bottom">
                        <Command>
                          <CommandInput placeholder="Buscar dataset..." />
                          <CommandEmpty>No se encontró ningún dataset.</CommandEmpty>
                          <CommandList>
                            <CommandGroup>
                              {datasets.map((dataset) => (
                                <CommandItem
                                  key={dataset.id}
                                  value={dataset.name}
                                  onSelect={() => {
                                    if (onDatasetSelect) {
                                      onDatasetSelect(dataset);
                                    }
                                    setDatasetOpen(false);
                                  }}
                                >
                                  <div className="flex flex-col">
                                    <span className="font-medium">{dataset.name}</span>
                                    <span className="text-xs text-gray-500">{dataset.row_count.toLocaleString()} registros</span>
                                  </div>
                                </CommandItem>
                              ))}
                            </CommandGroup>
                          </CommandList>
                        </Command>
                      </PopoverContent>
                    </Popover>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-gray-700">Período</Label>
                      <Select
                        value={formData.period}
                        onValueChange={(value) => updateFormData((prev: any) => ({ ...prev, period: value }))}
                      >
                        <SelectTrigger className="h-10 w-full">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1w">Última semana</SelectItem>
                          <SelectItem value="1m">Último mes</SelectItem>
                          <SelectItem value="3m">Últimos 3 meses</SelectItem>
                          <SelectItem value="6m">Últimos 6 meses</SelectItem>
                          <SelectItem value="1y">Último año</SelectItem>
                          <SelectItem value="ytd">Año hasta la fecha</SelectItem>
                          <SelectItem value="2y">Últimos 2 años</SelectItem>
                          <SelectItem value="4y">Últimos 4 años</SelectItem>
                          <SelectItem value="6y">Últimos 6 años</SelectItem>
                          <SelectItem value="8y">Últimos 8 años</SelectItem>
                          <SelectItem value="10y">Últimos 10 años</SelectItem>
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
                          <SelectItem value="all">Todo el tiempo</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-gray-700">Capital inicial ($)</Label>
                      <Input 
                        type="number" 
                        value={formData.init_cash}
                        onChange={(e) => updateFormData((prev: any) => ({ ...prev, init_cash: parseFloat(e.target.value) || 10000 }))}
                        className="h-10" 
                      />
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-gray-700">Comisiones (%)</Label>
                      <Input 
                        type="number" 
                        step="0.00001" 
                        value={formData.fees}
                        onChange={(e) => updateFormData((prev: any) => ({ ...prev, fees: parseFloat(e.target.value) || 0.00045 }))}
                        className="h-10" 
                      />
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-gray-700">Slippage (%)</Label>
                      <Input 
                        type="number" 
                        step="0.00001" 
                        value={formData.slippage}
                        onChange={(e) => updateFormData((prev: any) => ({ ...prev, slippage: parseFloat(e.target.value) || 0.0002 }))}
                        className="h-10" 
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Transformaciones */}
            <Card className="border-green-100 shadow-sm">
              <div className="bg-green-50/50 min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
                <div className="flex items-center gap-2 text-lg text-green-900 font-semibold">
                  <TrendingUp className="h-5 w-5" />
                  Transformaciones
                </div>
              </div>
              <CardContent className="px-4 py-6 space-y-4">
                <div className="grid grid-cols-4 gap-4 relative">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">Indicador (v)</Label>
                    <Select
                      value={formData.transform.v.type}
                      onValueChange={(value) => updateTransform('v', 'type', value)}
                    >
                      <SelectTrigger className="h-10 w-full">
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

                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">Período</Label>
                    <Input 
                      type="number" 
                      value={formData.transform.v.period}
                      onChange={(e) => updateTransform('v', 'period', parseInt(e.target.value) || 1)}
                      disabled={formData.transform.v.type === 'none'}
                      className="h-10" 
                    />
                  </div>

                  <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300 transform -translate-x-px"></div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">Precio (USD)</Label>
                    <Select
                      value={formData.transform.usd.type}
                      onValueChange={(value) => updateTransform('usd', 'type', value)}
                    >
                      <SelectTrigger className="h-10 w-full">
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

                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">Período</Label>
                    <Input 
                      type="number" 
                      value={formData.transform.usd.period}
                      onChange={(e) => updateTransform('usd', 'period', parseInt(e.target.value) || 1)}
                      disabled={formData.transform.usd.type === 'none'}
                      className="h-10" 
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Estrategia de backtesting */}
            <Card className="border-purple-100 shadow-sm">
              <div className="bg-purple-50/50 min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
                <div className="flex items-center gap-2 text-lg text-purple-900 font-semibold">
                  <Settings className="h-5 w-5" />
                  Estrategia de backtesting
                </div>
              </div>
              <CardContent className="px-4 py-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">Tipo de Estrategia</Label>
                    <Select
                      value={formData.strategy_type}
                      onValueChange={(value) => updateFormData((prev: any) => ({ ...prev, strategy_type: value as 'threshold' | 'crossover' | 'multi_dataset_crossover' }))}
                    >
                      <SelectTrigger className="h-10 w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="threshold">Umbrales</SelectItem>
                        <SelectItem value="crossover">Cruces de Medias Móviles</SelectItem>
                        <SelectItem value="multi_dataset_crossover">Cruce entre Datasets</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">
                      {formData.strategy_type === 'crossover' ? "Aplicar cruces sobre:" : "Aplicar señales a"}
                    </Label>
                    <Select
                      value={formData.apply_to}
                      onValueChange={(value) => updateFormData((prev: any) => ({ ...prev, apply_to: value as 'v' | 'usd' }))}
                    >
                      <SelectTrigger className="h-10 w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="v">Indicador (v)</SelectItem>
                        <SelectItem value="usd">Precio (USD)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="bg-gray-50 p-3 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-3">
                    {formData.strategy_type === 'threshold' && 'Umbrales'}
                    {formData.strategy_type === 'crossover' && 'Cruces de Medias Móviles'}
                    {formData.strategy_type === 'multi_dataset_crossover' && 'Cruce entre Datasets'}
                  </h3>

                  {formData.strategy_type === 'threshold' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">Umbral de Entrada</Label>
                        <Input 
                          type="number" 
                          value={formData.threshold_entry}
                          onChange={(e) => updateFormData((prev: any) => ({ ...prev, threshold_entry: parseFloat(e.target.value) || 0 }))}
                          className="h-10" 
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">Umbral de Salida</Label>
                        <Input 
                          type="number" 
                          value={formData.threshold_exit}
                          onChange={(e) => updateFormData((prev: any) => ({ ...prev, threshold_exit: parseFloat(e.target.value) || 0 }))}
                          className="h-10" 
                        />
                      </div>
                    </div>
                  )}

                                     {formData.strategy_type === 'multi_dataset_crossover' && (
                     <MultiDatasetSelector
                       datasets={datasets}
                       selectedDataset1={selectedDataset1}
                       selectedDataset2={selectedDataset2}
                       selectedPriceDataset={selectedPriceDataset}
                       onDataset1Select={setSelectedDataset1}
                       onDataset2Select={setSelectedDataset2}
                       onPriceDatasetSelect={setSelectedPriceDataset}
                       strategy={formData.multi_dataset_crossover_strategy}
                       onStrategyChange={updateMultiDatasetStrategy}
                     />
                   )}
                </div>

                <div className="bg-blue-50 p-3 rounded-lg space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="bitcoin-conditions"
                      checked={formData.bitcoin_price_condition.enabled}
                      onCheckedChange={(checked: boolean) => updateBitcoinPriceCondition('enabled', checked)}
                    />
                    <Label htmlFor="bitcoin-conditions" className="text-sm font-medium text-gray-700 cursor-pointer">
                      Activar condiciones de precio de Bitcoin
                    </Label>
                  </div>

                  {formData.bitcoin_price_condition.enabled && (
                    <div className="bg-blue-50 p-3 rounded-lg space-y-3">
                      <h4 className="font-medium text-blue-900">Condiciones de precio de Bitcoin</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label className="text-sm font-medium text-gray-700">Tipo de Media</Label>
                          <Select
                            value={formData.bitcoin_price_condition.ma_type}
                            onValueChange={(value) => updateBitcoinPriceCondition('ma_type', value)}
                          >
                            <SelectTrigger className="h-10 w-full">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="sma">SMA (Simple)</SelectItem>
                              <SelectItem value="ema">EMA (Exponencial)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label className="text-sm font-medium text-gray-700">Períodos</Label>
                          <Input 
                            type="number" 
                            value={formData.bitcoin_price_condition.ma_period}
                            onChange={(e) => updateBitcoinPriceCondition('ma_period', parseInt(e.target.value) || 50)}
                            className="h-10" 
                          />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-sm font-medium text-gray-700">Condición</Label>
                          <Select
                            value={formData.bitcoin_price_condition.condition}
                            onValueChange={(value) => updateBitcoinPriceCondition('condition', value)}
                          >
                            <SelectTrigger className="h-10 w-full">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="above">Por encima</SelectItem>
                              <SelectItem value="below">Por debajo</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          /* Flow Builder para Estrategias Compuestas */
          <CompositeStrategyFlowBuilder
            datasets={datasets}
            onStrategyChange={setCompositeStrategy}
          />
        )}

        <div className="flex justify-center pt-2">
          <Button
            type="submit"
            size="lg"
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg font-medium"
            disabled={
              isRunning || 
              (strategyMode === 'simple' && !selectedDataset) ||
              (strategyMode === 'simple' && formData.strategy_type === 'multi_dataset_crossover' && 
               (!selectedDataset1 || !selectedDataset2 || !selectedPriceDataset)) ||
              (strategyMode === 'composite' && !compositeStrategy)
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
                {strategyMode === 'composite' ? 
                  (!compositeStrategy ? 'Construye una Estrategia Compuesta' : 'Ejecutar Backtest Compuesto') :
                  !selectedDataset ? 'Selecciona un Dataset' : 
                  formData.strategy_type === 'multi_dataset_crossover' && (!selectedDataset1 || !selectedDataset2 || !selectedPriceDataset) ? 
                  'Selecciona todos los Datasets' : 'Ejecutar Backtest'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
