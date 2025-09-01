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
    setFormData(prev => {
      const newState = updater(prev);
      // También actualizar el estado global si está disponible
      if (onFormStateChange) {
        onFormStateChange(newState);
      }
      return newState;
    });
  };

  // Actualizar dataset_id cuando cambie el dataset seleccionado
  React.useEffect(() => {
    if (selectedDataset) {
      updateFormData(prev => ({ ...prev, dataset_id: selectedDataset.id }));
    }
  }, [selectedDataset]);

  // Actualizar estrategia multi-dataset cuando cambien los datasets seleccionados
  React.useEffect(() => {
    if (selectedDataset1) {
      updateFormData(prev => ({
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
      updateFormData(prev => ({
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
      updateFormData(prev => ({
        ...prev,
        multi_dataset_crossover_strategy: {
          ...prev.multi_dataset_crossover_strategy,
          price_dataset_id: selectedPriceDataset.id
        }
      }));
    }
  }, [selectedPriceDataset]);

  // Mapeo de períodos para descripción
  const getPeriodDescription = (period: string) => {
    const periodMap: { [key: string]: string } = {
      '1w': 'Última Semana',
      '1m': 'Último Mes',
      '3m': 'Último Trimestre',
      '6m': 'Últimos 6 Meses',
      'ytd': 'Este Año (YTD)',
      '1y': 'Último Año',
      '2y': 'Últimos 2 Años',
      '3y': 'Últimos 3 Años',
      '4y': 'Últimos 4 Años',
      '5y': 'Últimos 5 Años',
      '6y': 'Últimos 6 Años',
      '7y': 'Últimos 7 Años',
      '8y': 'Últimos 8 Años',
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
    
    // Añadir nombre del dataset y descripción del período
    const paramsWithMetadata = {
      ...formData,
      dataset_name: selectedDataset?.name || '',
      period_description: getPeriodDescription(formData.period)
    };
    
    onSubmit(paramsWithMetadata);
  };

  const updateTransform = (field: 'v' | 'usd', key: keyof TransformConfig, value: any) => {
    updateFormData(prev => ({
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
    updateFormData(prev => ({
      ...prev,
      multi_dataset_crossover_strategy: {
        ...prev.multi_dataset_crossover_strategy,
        [field]: value
      }
    }));
  };

  const updateBitcoinPriceCondition = (field: string, value: any) => {
    updateFormData(prev => ({
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
        <Card className="border-blue-100 shadow-sm">
          <div className="bg-blue-50/50 min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
            <div className="flex items-center gap-2 text-lg text-blue-900 font-semibold">
              <BarChart3 className="h-5 w-5" />
              Parámetros del backtest
            </div>
          </div>
          <CardContent className="px-4 py-6 space-y-4">
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
                              value={dataset.id.toString()}
                              onSelect={(currentValue: string) => {
                                const selected = datasets.find(d => d.id.toString() === currentValue);
                                if (selected && onDatasetSelect) {
                                  onDatasetSelect(selected);
                                }
                                setDatasetOpen(false);
                              }}
                            >
                              <div>
                                <div className="font-medium">{dataset.name}</div>
                                <div className="text-xs text-gray-500">{dataset.row_count.toLocaleString()} registros</div>
                              </div>
                            </CommandItem>
                          ))}
                        </CommandGroup>
                      </CommandList>
                    </Command>
                  </PopoverContent>
                </Popover>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="period" className="text-sm font-medium text-gray-700">
                    Período de backtesting
                  </Label>
                  <Select
                    value={formData.period}
                    onValueChange={(value) => updateFormData(prev => ({ ...prev, period: value as any }))}
                  >
                    <SelectTrigger className="h-10 w-full">
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

                <div className="grid grid-cols-3 gap-3">
                  <div className="space-y-2">
                    <Label htmlFor="capital" className="text-sm font-medium text-gray-700">
                      Capital inicial ($)
                    </Label>
                    <Input 
                      id="capital" 
                      type="number" 
                      value={formData.init_cash}
                      onChange={(e) => updateFormData(prev => ({ ...prev, init_cash: parseFloat(e.target.value) || 10000 }))}
                      className="h-10" 
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="commission" className="text-sm font-medium text-gray-700">
                      Comisiones (%)
                    </Label>
                    <Input 
                      id="commission" 
                      type="number" 
                      step="0.001" 
                      value={formData.fees * 100}
                      onChange={(e) => updateFormData(prev => ({ ...prev, fees: (parseFloat(e.target.value) || 0) / 100 }))}
                      className="h-10" 
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="slippage" className="text-sm font-medium text-gray-700">
                      Slippage (%)
                    </Label>
                    <Input 
                      id="slippage" 
                      type="number" 
                      step="0.01" 
                      value={formData.slippage * 100}
                      onChange={(e) => updateFormData(prev => ({ ...prev, slippage: (parseFloat(e.target.value) || 0) / 100 }))}
                      className="h-10" 
                    />
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

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
                  onValueChange={(value) => updateFormData(prev => ({ ...prev, strategy_type: value as 'threshold' | 'crossover' | 'multi_dataset_crossover' }))}
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
                  onValueChange={(value) => updateFormData(prev => ({ ...prev, apply_to: value as 'v' | 'usd' }))}
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
                      onChange={(e) => updateFormData(prev => ({ ...prev, threshold_entry: parseFloat(e.target.value) || 0 }))}
                      className="h-10" 
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">Umbral de Salida</Label>
                    <Input 
                      type="number" 
                      value={formData.threshold_exit}
                      onChange={(e) => updateFormData(prev => ({ ...prev, threshold_exit: parseFloat(e.target.value) || 0 }))}
                      className="h-10" 
                    />
                  </div>
                </div>
              )}

              {formData.strategy_type === 'crossover' && (
                <div className="space-y-6">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <h4 className="font-medium text-green-700">Señales de Entrada</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">Período Rápido</Label>
                        <Input 
                          type="number" 
                          value={formData.crossover_strategy.entry_fast_period}
                          onChange={(e) => updateFormData(prev => ({
                            ...prev,
                            crossover_strategy: {
                              ...prev.crossover_strategy,
                              entry_fast_period: parseInt(e.target.value) || 7
                            }
                          }))}
                          className="h-10" 
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">Período Lento</Label>
                        <Input 
                          type="number" 
                          value={formData.crossover_strategy.entry_slow_period}
                          onChange={(e) => updateFormData(prev => ({
                            ...prev,
                            crossover_strategy: {
                              ...prev.crossover_strategy,
                              entry_slow_period: parseInt(e.target.value) || 30
                            }
                          }))}
                          className="h-10" 
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">Tipo</Label>
                        <Select
                          value={formData.crossover_strategy.entry_type}
                          onValueChange={(value) => updateFormData(prev => ({
                            ...prev,
                            crossover_strategy: {
                              ...prev.crossover_strategy,
                              entry_type: value as 'sma' | 'ema'
                            }
                          }))}
                        >
                          <SelectTrigger className="h-10 w-full">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="sma">SMA</SelectItem>
                            <SelectItem value="ema">EMA</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">↑ Dirección</Label>
                        <Select
                          value={formData.crossover_strategy.entry_direction}
                          onValueChange={(value) => updateFormData(prev => ({
                            ...prev,
                            crossover_strategy: {
                              ...prev.crossover_strategy,
                              entry_direction: value as 'up' | 'down'
                            }
                          }))}
                        >
                          <SelectTrigger className="h-10 w-full">
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

                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <TrendingDown className="h-4 w-4 text-red-600" />
                      <h4 className="font-medium text-red-700">Señales de Salida</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">Período Rápido</Label>
                        <Input 
                          type="number" 
                          value={formData.crossover_strategy.exit_fast_period}
                          onChange={(e) => updateFormData(prev => ({
                            ...prev,
                            crossover_strategy: {
                              ...prev.crossover_strategy,
                              exit_fast_period: parseInt(e.target.value) || 7
                            }
                          }))}
                          className="h-10" 
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">Período Lento</Label>
                        <Input 
                          type="number" 
                          value={formData.crossover_strategy.exit_slow_period}
                          onChange={(e) => updateFormData(prev => ({
                            ...prev,
                            crossover_strategy: {
                              ...prev.crossover_strategy,
                              exit_slow_period: parseInt(e.target.value) || 14
                            }
                          }))}
                          className="h-10" 
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">Tipo</Label>
                        <Select
                          value={formData.crossover_strategy.exit_type}
                          onValueChange={(value) => updateFormData(prev => ({
                            ...prev,
                            crossover_strategy: {
                              ...prev.crossover_strategy,
                              exit_type: value as 'sma' | 'ema'
                            }
                          }))}
                        >
                          <SelectTrigger className="h-10 w-full">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="sma">SMA</SelectItem>
                            <SelectItem value="ema">EMA</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm font-medium text-gray-700">↓ Dirección</Label>
                        <Select
                          value={formData.crossover_strategy.exit_direction}
                          onValueChange={(value) => updateFormData(prev => ({
                            ...prev,
                            crossover_strategy: {
                              ...prev.crossover_strategy,
                              exit_direction: value as 'up' | 'down'
                            }
                          }))}
                        >
                          <SelectTrigger className="h-10 w-full">
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
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-2 cursor-pointer">
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

        <div className="flex justify-center pt-2">
          <Button
            type="submit"
            size="lg"
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg font-medium"
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
        </div>
      </form>
    </div>
  );
}
