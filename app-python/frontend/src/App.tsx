import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FileUploader } from './components/FileUploader';
import { DatasetManager } from './components/DatasetManager';
import { ParamsForm } from './components/ParamsForm';
import { KpiCards } from './components/KpiCards';
import { EquityChart } from './components/EquityChart';
import { TradesTable } from './components/TradesTable';
import { FundingCost } from './components/FundingCost';
import PyfolioAnalysis from './components/PyfolioAnalysis';
import { apiClient, UploadResponse, BacktestResponse, Dataset } from './lib/api';

const queryClient = new QueryClient();

function AppContent() {
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [backtestResult, setBacktestResult] = useState<BacktestResponse | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [initialCapital, setInitialCapital] = useState<number | undefined>(undefined);
  const [isUploading, setIsUploading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const handleFileUpload = async (file: File, datasetName: string, datasetDescription?: string) => {
    setIsUploading(true);
    try {
      const result = await apiClient.uploadCsv(file, datasetName, datasetDescription);
      setUploadResult(result);
      // Limpiar resultados anteriores del backtest
      setBacktestResult(null);
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadResult({
        ok: false,
        rows: 0,
        freq_detected: '',
        dataset_id: 0
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleBacktest = async (params: any) => {
    setIsRunning(true);
    try {
      // Guardar el capital inicial para mostrarlo en los KPIs
      setInitialCapital(params.init_cash);
      const result = await apiClient.runBacktest(params);
      setBacktestResult(result);
    } catch (error) {
      console.error('Error running backtest:', error);
      // Aquí podrías mostrar un toast de error
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Backtesting App</h1>
          <p className="text-muted-foreground mt-2">
            Sube tu CSV y ejecuta backtests con vectorbt
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Primer tercio - Datasets y Upload */}
          <div className="space-y-6">
            <DatasetManager
              onDatasetSelect={setSelectedDataset}
              selectedDataset={selectedDataset || undefined}
            />
            
            <FileUploader
              onFileUpload={handleFileUpload}
              isUploading={isUploading}
              uploadResult={uploadResult || undefined}
            />
          </div>

          {/* Segundo y tercer tercio - Parámetros del Backtest */}
          <div className="lg:col-span-2">
            <ParamsForm
              onSubmit={handleBacktest}
              isRunning={isRunning}
              selectedDataset={selectedDataset || undefined}
            />
          </div>
        </div>

        {/* Sección inferior - KPIs y Gráfico de Equity */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* KPIs - 1 tercio */}
          <div>
            <KpiCards results={backtestResult?.results} initialCapital={initialCapital} />
          </div>
          
          {/* Gráfico de Equity - 2 tercios */}
          <div className="lg:col-span-2">
            <EquityChart equity={backtestResult?.equity} />
          </div>
        </div>

        {/* Tabla de Operaciones - Ancho completo */}
        <div className="mt-8">
          <TradesTable trades={backtestResult?.trades || []} />
        </div>

        {/* Coste de Funding - Ancho completo */}
        {backtestResult?.trades && backtestResult.trades.length > 0 && (
          <div className="mt-8">
            <FundingCost 
              trades={backtestResult.trades} 
              fundingRateAnnual={10} 
            />
          </div>
        )}

        {/* Análisis Pyfolio - Ancho completo */}
        {backtestResult?.trades && backtestResult.trades.length > 0 && (
          <div className="mt-8">
            <PyfolioAnalysis 
              trades={backtestResult.trades} 
              initialCash={initialCapital || 10000} 
            />
          </div>
        )}

        {/* Información adicional */}
        {uploadResult?.ok && (
          <div className="mt-8 p-4 bg-muted rounded-lg">
            <h3 className="font-medium mb-2">Información del archivo</h3>
            <p className="text-sm text-muted-foreground">
              Filas procesadas: {uploadResult.rows} | 
              Frecuencia detectada: {uploadResult.freq_detected === '1D' ? 'Diaria' : 'Horaria'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
