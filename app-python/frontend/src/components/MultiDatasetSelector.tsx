import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Database, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { Dataset } from '@/lib/api';

interface MultiDatasetSelectorProps {
  datasets: Dataset[];
  selectedDataset1: Dataset | null;
  selectedDataset2: Dataset | null;
  selectedPriceDataset: Dataset | null;
  onDataset1Select: (dataset: Dataset) => void;
  onDataset2Select: (dataset: Dataset) => void;
  onPriceDatasetSelect: (dataset: Dataset) => void;
  strategy: {
    dataset1_indicator: 'v' | 'usd';
    dataset1_ma_type: 'sma' | 'ema';
    dataset1_ma_period: number;
    dataset2_indicator: 'v' | 'usd';
    dataset2_ma_type: 'sma' | 'ema';
    dataset2_ma_period: number;
    entry_direction: 'up' | 'down';
    exit_direction: 'up' | 'down';
    take_profit_pct: number;
    stop_loss_pct: number;
    use_take_profit: boolean;
    use_stop_loss: boolean;
  };
  onStrategyChange: (field: string, value: any) => void;
}

export function MultiDatasetSelector({
  datasets,
  selectedDataset1,
  selectedDataset2,
  selectedPriceDataset,
  onDataset1Select,
  onDataset2Select,
  onPriceDatasetSelect,
  strategy,
  onStrategyChange
}: MultiDatasetSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Cruce entre Datasets
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Selección de Datasets */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Dataset 1 */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Dataset 1 (Principal)</Label>
            <Select
              value={selectedDataset1?.id.toString() || ''}
              onValueChange={(value) => {
                const dataset = datasets.find(d => d.id.toString() === value);
                if (dataset) onDataset1Select(dataset);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar dataset" />
              </SelectTrigger>
              <SelectContent>
                {datasets.map((dataset) => (
                  <SelectItem key={dataset.id} value={dataset.id.toString()}>
                    {dataset.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedDataset1 && (
              <div className="text-xs text-gray-500">
                {selectedDataset1.row_count.toLocaleString()} registros
              </div>
            )}
          </div>

          {/* Dataset 2 */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Dataset 2 (Secundario)</Label>
            <Select
              value={selectedDataset2?.id.toString() || ''}
              onValueChange={(value) => {
                const dataset = datasets.find(d => d.id.toString() === value);
                if (dataset) onDataset2Select(dataset);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar dataset" />
              </SelectTrigger>
              <SelectContent>
                {datasets.map((dataset) => (
                  <SelectItem key={dataset.id} value={dataset.id.toString()}>
                    {dataset.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedDataset2 && (
              <div className="text-xs text-gray-500">
                {selectedDataset2.row_count.toLocaleString()} registros
              </div>
            )}
          </div>

          {/* Dataset para Precios */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Dataset Precios (USD)</Label>
            <Select
              value={selectedPriceDataset?.id.toString() || ''}
              onValueChange={(value) => {
                const dataset = datasets.find(d => d.id.toString() === value);
                if (dataset) onPriceDatasetSelect(dataset);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar dataset" />
              </SelectTrigger>
              <SelectContent>
                {datasets.map((dataset) => (
                  <SelectItem key={dataset.id} value={dataset.id.toString()}>
                    {dataset.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedPriceDataset && (
              <div className="text-xs text-gray-500">
                {selectedPriceDataset.row_count.toLocaleString()} registros
              </div>
            )}
          </div>
        </div>

        {/* Configuración Dataset 1 */}
        {selectedDataset1 && (
          <div className="space-y-3 p-4 border rounded-lg bg-gray-50">
            <Label className="text-sm font-medium text-gray-700">Configuración Dataset 1</Label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-xs">Indicador</Label>
                <Select
                  value={strategy.dataset1_indicator}
                  onValueChange={(value: 'v' | 'usd') => onStrategyChange('dataset1_indicator', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="v">Indicador (v)</SelectItem>
                    <SelectItem value="usd">Precio Bitcoin (usd)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-xs">Tipo Media</Label>
                <Select
                  value={strategy.dataset1_ma_type}
                  onValueChange={(value: 'sma' | 'ema') => onStrategyChange('dataset1_ma_type', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sma">SMA</SelectItem>
                    <SelectItem value="ema">EMA</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-xs">Período</Label>
                <Input
                  type="number"
                  min="1"
                  max="1000"
                  value={strategy.dataset1_ma_period}
                  onChange={(e) => onStrategyChange('dataset1_ma_period', parseInt(e.target.value))}
                />
              </div>
            </div>
          </div>
        )}

        {/* Configuración Dataset 2 */}
        {selectedDataset2 && (
          <div className="space-y-3 p-4 border rounded-lg bg-gray-50">
            <Label className="text-sm font-medium text-gray-700">Configuración Dataset 2</Label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-xs">Indicador</Label>
                <Select
                  value={strategy.dataset2_indicator}
                  onValueChange={(value: 'v' | 'usd') => onStrategyChange('dataset2_indicator', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="v">Indicador (v)</SelectItem>
                    <SelectItem value="usd">Precio Bitcoin (usd)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-xs">Tipo Media</Label>
                <Select
                  value={strategy.dataset2_ma_type}
                  onValueChange={(value: 'sma' | 'ema') => onStrategyChange('dataset2_ma_type', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sma">SMA</SelectItem>
                    <SelectItem value="ema">EMA</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-xs">Período</Label>
                <Input
                  type="number"
                  min="1"
                  max="1000"
                  value={strategy.dataset2_ma_period}
                  onChange={(e) => onStrategyChange('dataset2_ma_period', parseInt(e.target.value))}
                />
              </div>
            </div>
          </div>
        )}

        {/* Direcciones de Cruce */}
        <div className="space-y-3 p-4 border rounded-lg bg-blue-50">
          <Label className="text-sm font-medium text-blue-700">Direcciones de Cruce</Label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-xs flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                Entrada
              </Label>
              <Select
                value={strategy.entry_direction}
                onValueChange={(value: 'up' | 'down') => onStrategyChange('entry_direction', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="up">Al Alza (Dataset 1 cruza por encima)</SelectItem>
                  <SelectItem value="down">A la Baja (Dataset 1 cruza por debajo)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label className="text-xs flex items-center gap-1">
                <TrendingDown className="h-3 w-3" />
                Salida
              </Label>
              <Select
                value={strategy.exit_direction}
                onValueChange={(value: 'up' | 'down') => onStrategyChange('exit_direction', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="up">Al Alza (Dataset 1 cruza por encima)</SelectItem>
                  <SelectItem value="down">A la Baja (Dataset 1 cruza por debajo)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Take Profit y Stop Loss */}
        <div className="space-y-3 p-4 border rounded-lg bg-orange-50">
          <Label className="text-sm font-medium text-orange-700 flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            Take Profit y Stop Loss
          </Label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Take Profit */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="use-take-profit"
                  checked={strategy.use_take_profit}
                  onChange={(e) => onStrategyChange('use_take_profit', e.target.checked)}
                  className="rounded"
                />
                <Label htmlFor="use-take-profit" className="text-sm font-medium">Take Profit</Label>
              </div>
              {strategy.use_take_profit && (
                <div className="space-y-2">
                  <Label className="text-xs">Porcentaje de ganancia (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="100"
                    value={strategy.take_profit_pct}
                    onChange={(e) => onStrategyChange('take_profit_pct', parseFloat(e.target.value) || 3.0)}
                    placeholder="3.0"
                  />
                </div>
              )}
            </div>
            
            {/* Stop Loss */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="use-stop-loss"
                  checked={strategy.use_stop_loss}
                  onChange={(e) => onStrategyChange('use_stop_loss', e.target.checked)}
                  className="rounded"
                />
                <Label htmlFor="use-stop-loss" className="text-sm font-medium">Stop Loss</Label>
              </div>
              {strategy.use_stop_loss && (
                <div className="space-y-2">
                  <Label className="text-xs">Porcentaje de pérdida (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="50"
                    value={strategy.stop_loss_pct}
                    onChange={(e) => onStrategyChange('stop_loss_pct', parseFloat(e.target.value) || 1.0)}
                    placeholder="1.0"
                  />
                </div>
              )}
            </div>
          </div>
          
          {/* Descripción */}
          <div className="text-xs text-orange-600 mt-2">
            <p><strong>Take Profit:</strong> Cierra la operación cuando el precio sube el porcentaje especificado desde la entrada.</p>
            <p><strong>Stop Loss:</strong> Cierra la operación cuando el precio baja el porcentaje especificado desde la entrada.</p>
            <p>Estos criterios se aplican además de las señales de cruce configuradas.</p>
          </div>
        </div>

        {/* Resumen de la Estrategia */}
        {selectedDataset1 && selectedDataset2 && selectedPriceDataset && (
          <div className="p-4 border rounded-lg bg-green-50">
            <Label className="text-sm font-medium text-green-700">Resumen de Estrategia</Label>
            <div className="text-xs text-green-600 mt-2 space-y-1">
              <div>• <strong>Entrada:</strong> {strategy.entry_direction === 'up' ? 'Al alza' : 'A la baja'} cuando {selectedDataset1.name} ({strategy.dataset1_ma_type.toUpperCase()}({strategy.dataset1_ma_period})) cruza {selectedDataset2.name} ({strategy.dataset2_ma_type.toUpperCase()}({strategy.dataset2_ma_period}))</div>
              <div>• <strong>Salida:</strong> {strategy.exit_direction === 'up' ? 'Al alza' : 'A la baja'} cuando {selectedDataset1.name} ({strategy.dataset1_ma_type.toUpperCase()}({strategy.dataset1_ma_period})) cruza {selectedDataset2.name} ({strategy.dataset2_ma_type.toUpperCase()}({strategy.dataset2_ma_period}))</div>
              <div>• <strong>Precios:</strong> Usando datos de {selectedPriceDataset.name}</div>
              {strategy.use_take_profit && (
                <div>• <strong>Take Profit:</strong> {strategy.take_profit_pct}% de ganancia desde la entrada</div>
              )}
              {strategy.use_stop_loss && (
                <div>• <strong>Stop Loss:</strong> {strategy.stop_loss_pct}% de pérdida desde la entrada</div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
