import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FileUploader } from './components/FileUploader';
import { DatasetManager } from './components/DatasetManager';
import { ParamsForm } from './components/ParamsForm';
import { KpiCards } from './components/KpiCards';
import { EquityChart } from './components/EquityChart';
import { TradesTable } from './components/TradesTable';
import { FundingCost } from './components/FundingCost';
import { BacktestResults } from './components/BacktestResults';
import PyfolioAnalysis from './components/PyfolioAnalysis';
import DatasetUpdater from './components/DatasetUpdater';
import Login from './components/Login';
import Register from './components/Register';
import SaveStrategyModal from './components/SaveStrategyModal';
import StrategiesPage from './components/StrategiesPage';
import HyperliquidPage from './components/HyperliquidPage';
import UserProfilePage from './components/UserProfilePage';
import DatasetsPage from './components/DatasetsPage';
import Footer from './components/Footer';
import { Header } from './components/Header';
import { Menu } from './components/Menu';
import { apiClient, UploadResponse, BacktestResponse, Dataset } from './lib/api';

const queryClient = new QueryClient();

function AppContent() {
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [backtestResult, setBacktestResult] = useState<BacktestResponse | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [initialCapital, setInitialCapital] = useState<number | undefined>(undefined);
  const [isUploading, setIsUploading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  
  // Estados de autenticación
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showRegister, setShowRegister] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Estados de estrategias
  const [currentPage, setCurrentPage] = useState<'backtesting' | 'strategies' | 'hyperliquid' | 'datasets' | 'profile'>('backtesting');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [isSavingStrategy, setIsSavingStrategy] = useState(false);
  const [saveStrategyError, setSaveStrategyError] = useState('');
  const [lastBacktestConfig, setLastBacktestConfig] = useState<any>(null);
  const [lastBacktestResults, setLastBacktestResults] = useState<any>(null);
  const [selectedDatasetName, setSelectedDatasetName] = useState<string>('');
  const [selectedPeriodDescription, setSelectedPeriodDescription] = useState<string>('');

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
      
      // Guardar configuración y resultados para poder guardar la estrategia
      setLastBacktestConfig(params);
      setLastBacktestResults(result);
      
      // Guardar nombre del dataset y descripción del período
      if (params.dataset_name) {
        setSelectedDatasetName(params.dataset_name);
      }
      if (params.period_description) {
        setSelectedPeriodDescription(params.period_description);
      }
    } catch (error) {
      console.error('Error running backtest:', error);
      // Aquí podrías mostrar un toast de error
    } finally {
      setIsRunning(false);
    }
  };

  // Funciones de autenticación
  const handleLogin = (token: string, user: any) => {
    setIsAuthenticated(true);
    setCurrentUser(user);
    setShowRegister(false);
  };

  const handleRegister = (token: string, user: any) => {
    setIsAuthenticated(true);
    setCurrentUser(user);
    setShowRegister(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  const switchToRegister = () => {
    setShowRegister(true);
  };

  const switchToLogin = () => {
    setShowRegister(false);
  };

  // Funciones de estrategias
  const handleSaveStrategy = async (comments: string) => {
    if (!lastBacktestConfig || !lastBacktestResults) {
      setSaveStrategyError('No hay resultados de backtest para guardar');
      return;
    }

    setIsSavingStrategy(true);
    setSaveStrategyError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/strategies/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          strategy_type: lastBacktestConfig.strategy_type,
          configuration: lastBacktestConfig,
          results: lastBacktestResults,
          comments: comments || null
        })
      });

      if (response.ok) {
        setShowSaveModal(false);
        // Opcional: mostrar mensaje de éxito
        alert('Estrategia guardada exitosamente');
      } else {
        const errorData = await response.json();
        setSaveStrategyError(errorData.detail || 'Error guardando estrategia');
      }
    } catch (err) {
      setSaveStrategyError('Error de conexión. Verifica que el backend esté funcionando.');
    } finally {
      setIsSavingStrategy(false);
    }
  };



  // Verificar token al cargar la aplicación
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      const user = localStorage.getItem('user');

      if (token && user) {
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/verify`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            setIsAuthenticated(true);
            setCurrentUser(JSON.parse(user));
          } else {
            // Token inválido, limpiar localStorage
            localStorage.removeItem('token');
            localStorage.removeItem('user');
          }
        } catch (error) {
          console.error('Error verificando token:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Mostrar loading mientras se verifica la autenticación
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando...</p>
        </div>
      </div>
    );
  }

  // Mostrar login/register si no está autenticado
  if (!isAuthenticated) {
    return showRegister ? (
      <Register onRegister={handleRegister} onSwitchToLogin={switchToLogin} />
    ) : (
      <Login onLogin={handleLogin} onSwitchToRegister={switchToRegister} />
    );
  }

  // Mostrar dashboard si está autenticado
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header 
        currentUser={currentUser}
        onProfileClick={() => setCurrentPage('profile')}
        onLogout={handleLogout}
      />
      <Menu 
        currentPage={currentPage}
        onPageChange={setCurrentPage}
      />
      <main className="flex-1 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Contenido de las pestañas */}
        {currentPage === 'backtesting' ? (
          <>
            {/* Parámetros del Backtest - 100% ancho */}
            <div className="mb-8">
              <ParamsForm
                onSubmit={handleBacktest}
                isRunning={isRunning}
                selectedDataset={selectedDataset || undefined}
                onDatasetSelect={setSelectedDataset}
              />
            </div>

            {/* Resultados del Backtest - Solo mostrar si hay resultados */}
            {backtestResult && (
              <BacktestResults
                results={backtestResult}
                initialCapital={initialCapital}
                onSaveStrategy={() => setShowSaveModal(true)}
                onViewStrategies={() => setCurrentPage('strategies')}
              />
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
          </>
        ) : currentPage === 'strategies' ? (
          <StrategiesPage 
            currentUserId={currentUser?.id || 0}
          />
        ) : currentPage === 'datasets' ? (
          <DatasetsPage
            onFileUpload={handleFileUpload}
            isUploading={isUploading}
            uploadResult={uploadResult}
          />
        ) : currentPage === 'profile' ? (
          <UserProfilePage 
            username={currentUser?.username || ''}
            onBack={() => setCurrentPage('backtesting')}
          />
        ) : (
          <HyperliquidPage />
        )}

        {/* Modal de Guardar Estrategia */}
        <SaveStrategyModal
          isOpen={showSaveModal}
          onClose={() => setShowSaveModal(false)}
          onSave={handleSaveStrategy}
          isLoading={isSavingStrategy}
          error={saveStrategyError}
          strategyType={lastBacktestConfig?.strategy_type || ''}
          configuration={lastBacktestConfig}
          results={lastBacktestResults}
          datasetName={selectedDatasetName}
          periodDescription={selectedPeriodDescription}
        />
        </div>
      </main>
      <Footer />
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
