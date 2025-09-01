import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FileUploader } from './components/FileUploader';
import { DatasetManager } from './components/DatasetManager';
import { ParamsForm } from './components/ParamsForm';
import { KpiCards } from './components/KpiCards';
import { EquityChart } from './components/EquityChart';
import { TradesTable } from './components/TradesTable';
import { FundingCost } from './components/FundingCost';
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
  
  // Estado global para persistir valores del formulario de backtest
  const [backtestFormState, setBacktestFormState] = useState({
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
  });

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

  // Función para actualizar el estado del formulario desde ParamsForm
  const updateBacktestFormState = (newState: any) => {
    setBacktestFormState(newState);
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
          onLogoClick={() => setCurrentPage('backtesting')}
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
                formState={backtestFormState}
                onFormStateChange={updateBacktestFormState}
              />
            </div>

            {/* Resultados del Backtest - Solo mostrar si hay resultados */}
            {backtestResult && (
              <>
                {/* Sección inferior - KPIs y Gráfico de Equity */}
                <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* KPIs - 1 tercio */}
                  <div>
                    <KpiCards results={backtestResult?.results} initialCapital={initialCapital} />
                  </div>
                  
                  {/* Gráfico de Equity - 2 tercios */}
                  <div className="lg:col-span-2 flex">
                    <EquityChart equity={backtestResult?.equity} />
                  </div>
                </div>

                {/* Tabla de Operaciones - Ancho completo */}
                <div className="mt-8">
                  <TradesTable 
                    trades={backtestResult?.trades || []} 
                    datasetInterval={backtestResult?.dataset_interval}
                  />
                </div>

                {/* Coste de Funding - Ancho completo */}
                {backtestResult?.trades && backtestResult.trades.length > 0 && (
                  <div className="mt-8">
                    <FundingCost 
                      trades={backtestResult.trades} 
                      fundingRateAnnual={11.6} 
                    />
                  </div>
                )}

                {/* Sección de Guardar Estrategia */}
                {backtestResult?.trades && backtestResult.trades.length > 0 && (
                  <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          ¿Te gusta esta estrategia?
                        </h3>
                        <p className="text-gray-600">
                          Guarda esta configuración para reutilizarla o compartirla con otros usuarios.
                        </p>
                      </div>
                      <div className="flex space-x-3">
                        <button
                          onClick={() => setShowSaveModal(true)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                          Guardar Estrategia
                        </button>
                        <button
                          onClick={() => setCurrentPage('strategies')}
                          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                        >
                          Ver Todas las Estrategias
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </>
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
