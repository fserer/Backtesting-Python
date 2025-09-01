import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { 
  Plus, 
  Trash2, 
  Move, 
  Zap, 
  Target, 
  TrendingUp, 
  TrendingDown,
  Settings,
  ArrowRight,
  X
} from 'lucide-react';

interface StrategyCondition {
  id: string;
  type: 'threshold' | 'crossover' | 'multi_dataset_crossover';
  dataset_id: number;
  transform: {
    v: { type: 'none' | 'sma' | 'ema' | 'median'; period: number };
    usd: { type: 'none' | 'sma' | 'ema' | 'median'; period: number };
  };
  apply_to: 'v' | 'usd';
  threshold_entry?: number;
  threshold_exit?: number;
  crossover_strategy?: {
    entry_fast_period: number;
    entry_slow_period: number;
    exit_fast_period: number;
    exit_slow_period: number;
    entry_type: 'sma' | 'ema';
    exit_type: 'sma' | 'ema';
    entry_direction: 'up' | 'down';
    exit_direction: 'up' | 'down';
  };
  multi_dataset_crossover_strategy?: {
    dataset1_id: number;
    dataset1_indicator: 'v' | 'usd';
    dataset1_ma_type: 'sma' | 'ema';
    dataset1_ma_period: number;
    dataset2_id: number;
    dataset2_indicator: 'v' | 'usd';
    dataset2_ma_type: 'sma' | 'ema';
    dataset2_ma_period: number;
    entry_direction: 'up' | 'down';
    exit_direction: 'up' | 'down';
    price_dataset_id: number;
    take_profit_pct: number;
    stop_loss_pct: number;
    use_take_profit: boolean;
    use_stop_loss: boolean;
  };
  bitcoin_price_condition: {
    enabled: boolean;
    ma_type: 'sma' | 'ema';
    ma_period: number;
    condition: 'above' | 'below';
  };
  logic: 'AND' | 'OR';
}

interface CompositeStrategyFlowBuilderProps {
  datasets: any[];
  onStrategyChange: (strategy: any) => void;
}

export function CompositeStrategyFlowBuilder({ datasets, onStrategyChange }: CompositeStrategyFlowBuilderProps) {
  const [conditions, setConditions] = useState<StrategyCondition[]>([]);
  const [commonParams, setCommonParams] = useState({
    period: '1y' as const,
    init_cash: 10000,
    fees: 0.00045,
    slippage: 0.0002
  });

  // Función para actualizar parámetros comunes y reconstruir la estrategia
  const updateCommonParams = (updates: Partial<typeof commonParams>) => {
    setCommonParams(prev => {
      const newParams = { ...prev, ...updates };
      // Construir y enviar la estrategia actualizada
      setTimeout(() => buildStrategy(), 0);
      return newParams;
    });
  };

  const addCondition = () => {
    const newCondition: StrategyCondition = {
      id: `condition-${Date.now()}`,
      type: 'threshold',
      dataset_id: 0,
      transform: {
        v: { type: 'none', period: 1 },
        usd: { type: 'none', period: 1 }
      },
      apply_to: 'v',
      threshold_entry: 0,
      threshold_exit: 0,
      crossover_strategy: {
        entry_fast_period: 7,
        entry_slow_period: 30,
        exit_fast_period: 7,
        exit_slow_period: 14,
        entry_type: 'sma',
        exit_type: 'sma',
        entry_direction: 'up',
        exit_direction: 'down'
      },
      multi_dataset_crossover_strategy: {
        dataset1_id: 0,
        dataset1_indicator: 'v',
        dataset1_ma_type: 'sma',
        dataset1_ma_period: 7,
        dataset2_id: 0,
        dataset2_indicator: 'v',
        dataset2_ma_type: 'sma',
        dataset2_ma_period: 30,
        entry_direction: 'up',
        exit_direction: 'down',
        price_dataset_id: 0,
        take_profit_pct: 3.0,
        stop_loss_pct: 1.0,
        use_take_profit: true,
        use_stop_loss: true
      },
      bitcoin_price_condition: {
        enabled: false,
        ma_type: 'sma',
        ma_period: 50,
        condition: 'above'
      },
      logic: 'AND'
    };
    
    setConditions(prev => {
      const newConditions = [...prev, newCondition];
      // Construir y enviar la estrategia actualizada
      setTimeout(() => buildStrategy(newConditions), 0);
      return newConditions;
    });
  };

  const removeCondition = (id: string) => {
    setConditions(prev => {
      const newConditions = prev.filter(c => c.id !== id);
      // Construir y enviar la estrategia actualizada
      setTimeout(() => buildStrategy(newConditions), 0);
      return newConditions;
    });
  };

  const updateCondition = (id: string, updates: Partial<StrategyCondition>) => {
    setConditions(prev => {
      const newConditions = prev.map(c => 
        c.id === id ? { ...c, ...updates } : c
      );
      // Construir y enviar la estrategia actualizada
      setTimeout(() => buildStrategy(newConditions), 0);
      return newConditions;
    });
  };

  const moveCondition = (fromIndex: number, toIndex: number) => {
    setConditions(prev => {
      const newConditions = [...prev];
      const [movedCondition] = newConditions.splice(fromIndex, 1);
      newConditions.splice(toIndex, 0, movedCondition);
      // Construir y enviar la estrategia actualizada
      setTimeout(() => buildStrategy(newConditions), 0);
      return newConditions;
    });
  };

  const buildStrategy = (conditionsToUse?: StrategyCondition[]) => {
    const conditionsToBuild = conditionsToUse || conditions;
    const strategy = {
      ...commonParams,
      conditions: conditionsToBuild.map(c => ({
        type: c.type,
        dataset_id: c.dataset_id,
        transform: c.transform,
        apply_to: c.apply_to,
        ...(c.type === 'threshold' && {
          threshold_entry: c.threshold_entry,
          threshold_exit: c.threshold_exit
        }),
        ...(c.type === 'crossover' && {
          crossover_strategy: c.crossover_strategy
        }),
        ...(c.type === 'multi_dataset_crossover' && {
          multi_dataset_crossover_strategy: c.multi_dataset_crossover_strategy
        }),
        bitcoin_price_condition: c.bitcoin_price_condition,
        logic: c.logic
      }))
    };
    
    onStrategyChange(strategy);
  };

  return (
    <div className="space-y-6">
      {/* Parámetros Comunes */}
      <Card className="border-blue-200 bg-blue-50/30">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-blue-900">
            <Zap className="h-5 w-5" />
            Parámetros Comunes de la Estrategia
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-blue-900">Período</Label>
                                  <Select
                      value={commonParams.period}
                      onValueChange={(value: any) => updateCommonParams({ period: value })}
                    >
                <SelectTrigger className="h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1w">1 Semana</SelectItem>
                  <SelectItem value="1m">1 Mes</SelectItem>
                  <SelectItem value="3m">3 Meses</SelectItem>
                  <SelectItem value="6m">6 Meses</SelectItem>
                  <SelectItem value="1y">1 Año</SelectItem>
                  <SelectItem value="ytd">Año Actual</SelectItem>
                  <SelectItem value="2y">2 Años</SelectItem>
                  <SelectItem value="4y">4 Años</SelectItem>
                  <SelectItem value="6y">6 Años</SelectItem>
                  <SelectItem value="8y">8 Años</SelectItem>
                  <SelectItem value="10y">10 Años</SelectItem>
                  <SelectItem value="2015">Desde 2015</SelectItem>
                  <SelectItem value="2016">Desde 2016</SelectItem>
                  <SelectItem value="2017">Desde 2017</SelectItem>
                  <SelectItem value="2018">Desde 2018</SelectItem>
                  <SelectItem value="2019">Desde 2019</SelectItem>
                  <SelectItem value="2020">Desde 2020</SelectItem>
                  <SelectItem value="2021">Desde 2021</SelectItem>
                  <SelectItem value="2022">Desde 2022</SelectItem>
                  <SelectItem value="2023">Desde 2023</SelectItem>
                  <SelectItem value="2024">Desde 2024</SelectItem>
                  <SelectItem value="2025">Desde 2025</SelectItem>
                  <SelectItem value="all">Todo el Histórico</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label className="text-sm font-medium text-blue-900">Capital Inicial</Label>
                                    <Input 
                        type="number" 
                        value={commonParams.init_cash}
                        onChange={(e) => updateCommonParams({ init_cash: parseFloat(e.target.value) || 10000 })}
                        className="h-10" 
                      />
            </div>
            
            <div className="space-y-2">
              <Label className="text-sm font-medium text-blue-900">Comisiones</Label>
                                    <Input 
                        type="number" 
                        step="0.00001" 
                        value={commonParams.fees}
                        onChange={(e) => updateCommonParams({ fees: parseFloat(e.target.value) || 0.00045 })}
                        className="h-10" 
                      />
            </div>
            
            <div className="space-y-2">
              <Label className="text-sm font-medium text-blue-900">Slippage</Label>
              <Input
                type="number"
                step="0.00001"
                value={commonParams.slippage}
                                        onChange={(e) => updateCommonParams({ slippage: parseFloat(e.target.value) || 0.0002 })}
                className="h-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Flow Builder de Condiciones */}
      <Card className="border-purple-200 bg-purple-50/30">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-purple-900">
            <Target className="h-5 w-5" />
            Constructor de Estrategias Compuestas
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Condiciones existentes */}
            {conditions.map((condition, index) => (
              <div key={condition.id} className="relative">
                {/* Línea de conexión */}
                {index > 0 && (
                  <div className="absolute left-6 top-0 w-0.5 h-4 bg-purple-300 transform -translate-y-full"></div>
                )}
                
                {/* Condición */}
                <div className="flex items-start gap-4 p-4 bg-white rounded-lg border-2 border-purple-200 shadow-sm hover:shadow-md transition-shadow">
                  {/* Drag Handle */}
                  <div className="flex-shrink-0 mt-2">
                    <Move className="h-4 w-4 text-purple-400 cursor-move" />
                  </div>
                  
                  {/* Lógica de conexión */}
                  {index > 0 && (
                    <div className="flex-shrink-0 mt-2">
                      <Select 
                        value={condition.logic} 
                        onValueChange={(value: 'AND' | 'OR') => updateCondition(condition.id, { logic: value })}
                      >
                        <SelectTrigger className="w-16 h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="AND">AND</SelectItem>
                          <SelectItem value="OR">OR</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                  
                  {/* Contenido de la condición */}
                  <div className="flex-1 space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-lg font-semibold text-purple-900">
                        Condición {index + 1}
                      </h4>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => removeCondition(condition.id)}
                        className="h-8 w-8 p-0"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    {/* Configuración de la condición */}
                    <StrategyConditionConfig
                      condition={condition}
                      datasets={datasets}
                      onUpdate={(updates) => updateCondition(condition.id, updates)}
                    />
                  </div>
                </div>
              </div>
            ))}
            
            {/* Botón para añadir condición */}
            <div className="flex justify-center pt-4">
              <Button
                onClick={addCondition}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3"
              >
                <Plus className="h-4 w-4 mr-2" />
                Añadir Nueva Condición
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Botón para construir la estrategia */}
      {conditions.length > 0 && (
        <div className="flex justify-center">
          <Button
            onClick={buildStrategy}
            size="lg"
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 text-lg font-medium"
          >
            <Zap className="h-5 w-5 mr-2" />
            Construir Estrategia Compuesta
          </Button>
        </div>
      )}
    </div>
  );
}

// Componente para configurar cada condición individual
function StrategyConditionConfig({ 
  condition, 
  datasets, 
  onUpdate 
}: { 
  condition: StrategyCondition; 
  datasets: any[]; 
  onUpdate: (updates: Partial<StrategyCondition>) => void;
}) {
  return (
    <div className="space-y-4">
      {/* Tipo de estrategia */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">Tipo de Estrategia</Label>
          <Select 
            value={condition.type} 
            onValueChange={(value: 'threshold' | 'crossover' | 'multi_dataset_crossover') => 
              onUpdate({ type: value })
            }
          >
            <SelectTrigger className="h-10">
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
          <Label className="text-sm font-medium text-gray-700">Dataset</Label>
          <Select 
            value={condition.dataset_id.toString()} 
            onValueChange={(value) => onUpdate({ dataset_id: parseInt(value) })}
          >
            <SelectTrigger className="h-10">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {datasets.map(dataset => (
                <SelectItem key={dataset.id} value={dataset.id.toString()}>
                  {dataset.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Transformaciones */}
      <div className="space-y-3">
        <Label className="text-sm font-medium text-gray-700">Transformaciones</Label>
        <div className="grid grid-cols-4 gap-4">
          <div className="space-y-2">
            <Label className="text-xs text-gray-600">Indicador (v)</Label>
            <Select
              value={condition.transform.v.type}
              onValueChange={(value: 'none' | 'sma' | 'ema' | 'median') => 
                onUpdate({
                  transform: {
                    ...condition.transform,
                    v: { ...condition.transform.v, type: value }
                  }
                })
              }
            >
              <SelectTrigger className="h-8">
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
            <Label className="text-xs text-gray-600">Período</Label>
            <Input
              type="number"
              value={condition.transform.v.period}
              onChange={(e) => onUpdate({
                transform: {
                  ...condition.transform,
                  v: { ...condition.transform.v, period: parseInt(e.target.value) || 1 }
                }
              })}
              disabled={condition.transform.v.type === 'none'}
              className="h-8"
            />
          </div>
          
          <div className="space-y-2">
            <Label className="text-xs text-gray-600">Precio (USD)</Label>
            <Select
              value={condition.transform.usd.type}
              onValueChange={(value: 'none' | 'sma' | 'ema' | 'median') => 
                onUpdate({
                  transform: {
                    ...condition.transform,
                    usd: { ...condition.transform.usd, type: value }
                  }
                })
              }
            >
              <SelectTrigger className="h-8">
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
            <Label className="text-xs text-gray-600">Período</Label>
            <Input
              type="number"
              value={condition.transform.usd.period}
              onChange={(e) => onUpdate({
                transform: {
                  ...condition.transform,
                  usd: { ...condition.transform.usd, period: parseInt(e.target.value) || 1 }
                }
              })}
              disabled={condition.transform.usd.type === 'none'}
              className="h-8"
            />
          </div>
        </div>
      </div>

      {/* Configuración específica según el tipo */}
      {condition.type === 'threshold' && (
        <div className="space-y-3">
          <Label className="text-sm font-medium text-gray-700">Umbrales</Label>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-xs text-gray-600">Entrada</Label>
              <Input
                type="number"
                value={condition.threshold_entry}
                onChange={(e) => onUpdate({ threshold_entry: parseFloat(e.target.value) || 0 })}
                className="h-10"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-xs text-gray-600">Salida</Label>
              <Input
                type="number"
                value={condition.threshold_exit}
                onChange={(e) => onUpdate({ threshold_exit: parseFloat(e.target.value) || 0 })}
                className="h-10"
              />
            </div>
          </div>
        </div>
      )}

      {condition.type === 'crossover' && (
        <div className="space-y-4">
          <div className="bg-green-50 p-4 rounded-lg space-y-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <h4 className="font-medium text-green-900">Señales de Entrada</h4>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs text-gray-600">Período Rápido</Label>
                <Input
                  type="number"
                  value={condition.crossover_strategy?.entry_fast_period}
                  onChange={(e) => onUpdate({
                    crossover_strategy: {
                      ...condition.crossover_strategy!,
                      entry_fast_period: parseInt(e.target.value) || 7
                    }
                  })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs text-gray-600">Período Lento</Label>
                <Input
                  type="number"
                  value={condition.crossover_strategy?.entry_slow_period}
                  onChange={(e) => onUpdate({
                    crossover_strategy: {
                      ...condition.crossover_strategy!,
                      entry_slow_period: parseInt(e.target.value) || 30
                    }
                  })}
                  className="h-8"
                />
              </div>
            </div>
          </div>

          <div className="bg-red-50 p-4 rounded-lg space-y-3">
            <div className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <h4 className="font-medium text-red-900">Señales de Salida</h4>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs text-gray-600">Período Rápido</Label>
                <Input
                  type="number"
                  value={condition.crossover_strategy?.exit_fast_period}
                  onChange={(e) => onUpdate({
                    crossover_strategy: {
                      ...condition.crossover_strategy!,
                      exit_fast_period: parseInt(e.target.value) || 7
                    }
                  })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs text-gray-600">Período Lento</Label>
                <Input
                  type="number"
                  value={condition.crossover_strategy?.exit_slow_period}
                  onChange={(e) => onUpdate({
                    crossover_strategy: {
                      ...condition.crossover_strategy!,
                      exit_slow_period: parseInt(e.target.value) || 14
                    }
                  })}
                  className="h-8"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Condiciones de Bitcoin */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <Checkbox
            id={`bitcoin-${condition.id}`}
            checked={condition.bitcoin_price_condition.enabled}
            onCheckedChange={(checked: boolean) => onUpdate({
              bitcoin_price_condition: {
                ...condition.bitcoin_price_condition,
                enabled: checked
              }
            })}
          />
          <Label htmlFor={`bitcoin-${condition.id}`} className="text-sm font-medium text-gray-700">
            Activar condiciones de precio de Bitcoin
          </Label>
        </div>

        {condition.bitcoin_price_condition.enabled && (
          <div className="bg-blue-50 p-3 rounded-lg space-y-3">
            <h4 className="font-medium text-blue-900">Condiciones de precio de Bitcoin</h4>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-sm font-medium text-gray-700">Tipo de Media</Label>
                <Select
                  value={condition.bitcoin_price_condition.ma_type}
                  onValueChange={(value: 'sma' | 'ema') => onUpdate({
                    bitcoin_price_condition: {
                      ...condition.bitcoin_price_condition,
                      ma_type: value
                    }
                  })}
                >
                  <SelectTrigger className="h-10">
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
                  value={condition.bitcoin_price_condition.ma_period}
                  onChange={(e) => onUpdate({
                    bitcoin_price_condition: {
                      ...condition.bitcoin_price_condition,
                      ma_period: parseInt(e.target.value) || 50
                    }
                  })}
                  className="h-10"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium text-gray-700">Condición</Label>
                <Select
                  value={condition.bitcoin_price_condition.condition}
                  onValueChange={(value: 'above' | 'below') => onUpdate({
                    bitcoin_price_condition: {
                      ...condition.bitcoin_price_condition,
                      condition: value
                    }
                  })}
                >
                  <SelectTrigger className="h-10">
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
    </div>
  );
}
