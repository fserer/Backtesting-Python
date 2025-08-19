import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { X, Save, Info } from 'lucide-react';

interface SaveStrategyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (comments: string) => void;
  isLoading: boolean;
  error: string;
  strategyType: string;
  configuration: any;
  results: any;
}

const SaveStrategyModal: React.FC<SaveStrategyModalProps> = ({
  isOpen,
  onClose,
  onSave,
  isLoading,
  error,
  strategyType,
  configuration,
  results
}) => {
  const [comments, setComments] = useState('');

  // Funciones auxiliares para mostrar información descriptiva
  const getStrategyTypeDescription = (type: string, config: any) => {
    if (type === 'threshold') {
      return 'Estrategia de Umbrales';
    } else if (type === 'crossover' && config?.crossover_strategy) {
      const crossover = config.crossover_strategy;
      return `Cruce de Medias (${crossover.entry_type.toUpperCase()} ${crossover.entry_fast_period}/${crossover.entry_slow_period} - ${crossover.exit_type.toUpperCase()} ${crossover.exit_fast_period}/${crossover.exit_slow_period})`;
    } else if (type === 'multi_dataset_crossover') {
      return 'Cruce Multi-Dataset';
    }
    return type;
  };

  const getDatasetName = (datasetId: number) => {
    // Por ahora retornamos el ID, pero esto debería obtener el nombre real del dataset
    return `Dataset ${datasetId}`;
  };

  const handleSave = () => {
    onSave(comments.trim());
  };

  const handleClose = () => {
    setComments('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-xl font-bold">Guardar Estrategia</CardTitle>
              <CardDescription>
                Guarda la configuración actual del backtest para reutilizarla
              </CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              disabled={isLoading}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Información de lo que se va a guardar */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-semibold">Se guardará la siguiente información:</p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li><strong>Tipo de estrategia:</strong> {getStrategyTypeDescription(strategyType, configuration)}</li>
                  <li><strong>Dataset:</strong> {getDatasetName(configuration?.dataset_id)}</li>
                  <li><strong>Período:</strong> {configuration?.period || 'N/A'}</li>
                  <li><strong>Comisiones:</strong> {(configuration?.fees * 100).toFixed(3)}%</li>
                  <li><strong>Capital inicial:</strong> ${configuration?.init_cash?.toLocaleString() || 'N/A'}</li>
                  {configuration?.transform?.v?.type !== 'none' && (
                    <li><strong>Transformación Indicador:</strong> {configuration.transform.v.type.toUpperCase()} {configuration.transform.v.period}</li>
                  )}
                  {configuration?.transform?.usd?.type !== 'none' && (
                    <li><strong>Transformación Precio:</strong> {configuration.transform.usd.type.toUpperCase()} {configuration.transform.usd.period}</li>
                  )}
                  {configuration?.strategy_type === 'threshold' && (
                    <>
                      <li><strong>Umbral de entrada:</strong> {configuration?.threshold_entry}</li>
                      <li><strong>Umbral de salida:</strong> {configuration?.threshold_exit}</li>
                    </>
                  )}
                  {configuration?.strategy_type === 'crossover' && configuration?.crossover_strategy && (
                    <>
                      <li><strong>Entrada:</strong> {configuration.crossover_strategy.entry_type.toUpperCase()} {configuration.crossover_strategy.entry_fast_period}/{configuration.crossover_strategy.entry_slow_period}</li>
                      <li><strong>Salida:</strong> {configuration.crossover_strategy.exit_type.toUpperCase()} {configuration.crossover_strategy.exit_fast_period}/{configuration.crossover_strategy.exit_slow_period}</li>
                    </>
                  )}
                  <li><strong>Resultados del backtest:</strong> {results?.trades?.length || 0} operaciones</li>
                  <li><strong>P&L Total:</strong> ${results?.total_pnl?.toFixed(2) || 'N/A'}</li>
                </ul>
                <p className="text-xs text-muted-foreground mt-2">
                  La estrategia será visible para todos los usuarios registrados.
                </p>
              </div>
            </AlertDescription>
          </Alert>

          {/* Comentarios */}
          <div className="space-y-2">
            <Label htmlFor="comments">Comentarios (opcional)</Label>
            <textarea
              id="comments"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Escribe notas sobre esta estrategia, observaciones, razones de los parámetros elegidos, etc. (máximo 1000 caracteres)"
              className="w-full min-h-[100px] p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
              disabled={isLoading}
              maxLength={1000}
            />
            <p className="text-xs text-muted-foreground">
              {comments.length}/1000 caracteres
            </p>
          </div>

          {/* Error */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Botones */}
          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancelar
            </Button>
            <Button
              onClick={handleSave}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Guardar Estrategia
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SaveStrategyModal;
