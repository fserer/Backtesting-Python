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
      const token = localStorage.getItem('token');
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const timestamp = Date.now(); // Evitar caché
      const fullUrl = `${apiUrl}/api/datasets/update-all?_t=${timestamp}`;
      
      console.log('🔗 Llamando a URL:', fullUrl);
      console.log('🔑 Token presente:', !!token);
      console.log('🌐 API URL configurada:', apiUrl);
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
        },
      });

      console.log('📡 Status de respuesta:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error en respuesta:', errorText);
        throw new Error(`Error ${response.status}: ${response.statusText} - ${errorText}`);
      }

      const data: UpdateAllResponse = await response.json();
      
      console.log('Respuesta del backend:', data);
      console.log('data.results:', data.results);
      console.log('typeof data.results:', typeof data.results);
      console.log('Object.keys(data.results):', Object.keys(data.results));
      
      // Convertir resultados a array para facilitar el renderizado
      const resultsArray = Object.entries(data.results).map(([datasetName, result]) => ({
        dataset_name: datasetName,
        ...result
      }));

      console.log('Resultados procesados:', resultsArray);
      console.log('📊 Total de datasets procesados:', resultsArray.length);
      console.log('📋 Datasets procesados:', resultsArray.map(r => r.dataset_name));
      
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
    <Card className="border border-gray-200">
      <div className="min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
        <div className="flex items-center gap-2 text-lg text-purple-900 font-semibold">
          <RefreshCw className="h-5 w-5" />
          Actualización de Datasets
        </div>
      </div>
      <CardContent className="px-4 py-4 space-y-4">
        <p className="text-sm text-gray-600 mb-4">
          Actualiza automáticamente todos los datasets desde NodeCharts API
        </p>
        
        <Button 
          onClick={updateAllDatasets} 
          disabled={isUpdating}
          className="w-full sm:w-auto"
        >
          {isUpdating ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Actualizando...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Actualizar Todos los Datasets
            </>
          )}
        </Button>

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
