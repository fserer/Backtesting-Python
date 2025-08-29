import { API_BASE_URL } from '../config';

export interface Dataset {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  row_count: number;
}

export interface CreateDatasetRequest {
  name: string;
  description?: string;
}

export interface UpdateDatasetRequest {
  name?: string;
  description?: string;
}

export interface UploadResponse {
  ok: boolean;
  rows: number;
  freq_detected: string;
  dataset_id: number;
}

export interface TransformConfig {
  type: 'none' | 'sma' | 'ema' | 'median';
  period: number;
}

export interface CrossoverStrategy {
  entry_fast_period: number;
  entry_slow_period: number;
  exit_fast_period: number;
  exit_slow_period: number;
  entry_type: 'sma' | 'ema';
  exit_type: 'sma' | 'ema';
  entry_direction: 'up' | 'down';
  exit_direction: 'up' | 'down';
}

export interface BitcoinPriceCondition {
  enabled: boolean;
  ma_type: 'sma' | 'ema';
  ma_period: number;
  condition: 'above' | 'below';  // 'above' = por encima, 'below' = por debajo
}

export interface MultiDatasetCrossoverStrategy {
  // Dataset 1 (indicador principal)
  dataset1_id: number;
  dataset1_indicator: 'v' | 'usd';
  dataset1_ma_type: 'sma' | 'ema';
  dataset1_ma_period: number;
  
  // Dataset 2 (indicador secundario)
  dataset2_id: number;
  dataset2_indicator: 'v' | 'usd';
  dataset2_ma_type: 'sma' | 'ema';
  dataset2_ma_period: number;
  
  // Direcciones de cruce
  entry_direction: 'up' | 'down';
  exit_direction: 'up' | 'down';
  
  // Dataset para precio de Bitcoin (usd)
  price_dataset_id: number;
  
  // Criterios de Take Profit y Stop Loss
  take_profit_pct: number;  // Porcentaje de ganancia para cerrar
  stop_loss_pct: number;    // Porcentaje de pérdida para cerrar
  use_take_profit: boolean; // Si usar Take Profit
  use_stop_loss: boolean;   // Si usar Stop Loss
}

export interface BacktestRequest {
  dataset_id: number;
  transform: {
    v: TransformConfig;
    usd: TransformConfig;
  };
  apply_to: 'v' | 'usd';
  strategy_type: 'threshold' | 'crossover' | 'multi_dataset_crossover';
  threshold_entry: number;
  threshold_exit: number;
  crossover_strategy?: CrossoverStrategy;
  multi_dataset_crossover_strategy?: MultiDatasetCrossoverStrategy;
  bitcoin_price_condition: BitcoinPriceCondition;
  period: '1w' | '1m' | '3m' | '6m' | '1y' | 'ytd' | '2y' | '4y' | '6y' | '8y' | '10y' | '2015' | '2016' | '2017' | '2018' | '2019' | '2020' | '2021' | '2022' | '2023' | '2024' | '2025' | 'all';
  fees: number;
  slippage: number;
  init_cash: number;
  override_freq?: string;
}

export interface BacktestResults {
  total_return: number;
  sharpe: number;
  max_drawdown: number;
  trades: number;
  cagr: number;
  period_duration: string;
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
}

export interface Trade {
  entry_date?: string;
  exit_date?: string;
  entry_price: number;
  exit_price: number;
  size: number;
  pnl: number;
  return_pct: number;
  duration: number;
  entry_fees: number;
  exit_fees: number;
}

export interface BacktestResponse {
  results: BacktestResults;
  equity: EquityPoint[];
  trades: Trade[];
  freq: string;
  dataset_interval?: string;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async uploadCsv(file: File, datasetName: string, datasetDescription?: string): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataset_name', datasetName);
    if (datasetDescription) {
      formData.append('dataset_description', datasetDescription);
    }

    const response = await fetch(`${this.baseUrl}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al subir el archivo');
    }

    return response.json();
  }

  async getDatasets(): Promise<Dataset[]> {
    const response = await fetch(`${this.baseUrl}/api/datasets`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al obtener datasets');
    }
    return response.json();
  }

  async getDataset(id: number): Promise<Dataset> {
    const response = await fetch(`${this.baseUrl}/api/datasets/${id}`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al obtener dataset');
    }
    return response.json();
  }

  async updateDataset(id: number, request: UpdateDatasetRequest): Promise<Dataset> {
    const response = await fetch(`${this.baseUrl}/api/datasets/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al actualizar dataset');
    }
    return response.json();
  }

  async deleteDataset(id: number): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/api/datasets/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al eliminar dataset');
    }
    return response.json();
  }

  async runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
    const response = await fetch(`${this.baseUrl}/api/backtest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al ejecutar el backtest');
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('Backend no disponible');
    }
    return response.json();
  }

  async generatePyfolioAnalysis(trades: any[], initialCash: number): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/pyfolio`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        trades: trades,
        initial_cash: initialCash
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al generar análisis Pyfolio');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
