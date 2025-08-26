import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

interface DatasetUpdateResult {
  dataset_name: string;
  success: boolean;
  rows_added: number;
  error?: string;
}

interface UpdateAllResponse {
  message: string;
  results: Record<string, DatasetUpdateResult>;
}

const DatasetUpdater: React.FC = () => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateResults, setUpdateResults] = useState<DatasetUpdateResult[]>([]);
  const [lastUpdateTime, setLastUpdateTime] = useState<string | null>(null);

  const updateAllDatasets = async () => {
    setIsUpdating(true);
    setUpdateResults([]);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/datasets/update-all`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data: UpdateAllResponse = await response.json();
      
      console.log('Respuesta del backend:', data);
      
      // Convertir resultados a array para facilitar el renderizado
      const resultsArray = Object.entries(data.results).map(([datasetName, result]) => ({
        dataset_name: datasetName,
        ...result
      }));

      console.log('Resultados procesados:', resultsArray);
      
      setUpdateResults(resultsArray);
      setLastUpdateTime(new Date().toLocaleString('es-ES'));
    } catch (error) {
      console.error('Error actualizando datasets:', error);
      setUpdateResults([{
        dataset_name: 'Error',
        success: false,
        rows_added: 0,
        error: error instanceof Error ? error.message : 'Error desconocido'
      }]);
    } finally {
      setIsUpdating(false);
    }
  };

  const getSuccessCount = () => updateResults.filter(r => r.success).length;
  const getTotalRowsAdded = () => updateResults.reduce((sum, r) => sum + r.rows_added, 0);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5" />
          Actualización Automática de Datasets
        </CardTitle>
        <CardDescription>
          Actualiza automáticamente todos los datasets desde NodeCharts API
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <Button 
            onClick={updateAllDatasets} 
            disabled={isUpdating}
            className="flex items-center gap-2"
          >
            {isUpdating ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                Actualizando...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4" />
                Actualizar Todos los Datasets
              </>
            )}
          </Button>
          
          {lastUpdateTime && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              Última actualización: {lastUpdateTime}
            </div>
          )}
        </div>

        {updateResults.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium">Resumen:</span>
                <span className="text-sm">
                  ✅ {getSuccessCount()}/{updateResults.length} exitosos
                </span>
                <span className="text-sm">
                  📊 {getTotalRowsAdded()} registros añadidos
                </span>
              </div>
            </div>

            <div className="space-y-2">
              {updateResults.map((result, index) => (
                <div 
                  key={index} 
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {result.success ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-600" />
                    )}
                    <span className="font-medium">{result.dataset_name}</span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm">
                    {result.success ? (
                      <>
                        <span className="text-green-600">
                          {result.rows_added} registros añadidos
                        </span>
                      </>
                    ) : (
                      <span className="text-red-600">
                        {result.error || 'Error desconocido'}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DatasetUpdater;
