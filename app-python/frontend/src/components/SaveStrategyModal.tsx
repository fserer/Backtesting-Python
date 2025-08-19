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
  onSave: (strategyName: string) => void;
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
  const [strategyName, setStrategyName] = useState('');

  const handleSave = () => {
    if (strategyName.trim()) {
      onSave(strategyName.trim());
    }
  };

  const handleClose = () => {
    setStrategyName('');
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
          {/* Nombre de la estrategia */}
          <div className="space-y-2">
            <Label htmlFor="strategyName">Nombre de la Estrategia *</Label>
            <Input
              id="strategyName"
              type="text"
              value={strategyName}
              onChange={(e) => setStrategyName(e.target.value)}
              placeholder="Ej: Estrategia SOPR Umbral 0.9"
              disabled={isLoading}
            />
          </div>

          {/* Información de lo que se va a guardar */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-semibold">Se guardará la siguiente información:</p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li><strong>Tipo de estrategia:</strong> {strategyType}</li>
                  <li><strong>Dataset:</strong> {configuration?.dataset_id || 'N/A'}</li>
                  <li><strong>Período:</strong> {configuration?.period || 'N/A'}</li>
                  <li><strong>Comisiones:</strong> {(configuration?.fees * 100).toFixed(3)}%</li>
                  <li><strong>Capital inicial:</strong> ${configuration?.init_cash?.toLocaleString() || 'N/A'}</li>
                  <li><strong>Resultados del backtest:</strong> {results?.trades?.length || 0} operaciones</li>
                  <li><strong>P&L Total:</strong> ${results?.total_pnl?.toFixed(2) || 'N/A'}</li>
                </ul>
                <p className="text-xs text-muted-foreground mt-2">
                  La estrategia será visible para todos los usuarios registrados.
                </p>
              </div>
            </AlertDescription>
          </Alert>

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
              disabled={isLoading || !strategyName.trim()}
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
