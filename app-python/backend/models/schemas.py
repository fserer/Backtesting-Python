from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Literal
from datetime import datetime

class TransformConfig(BaseModel):
    type: Literal["none", "sma", "ema", "median"] = "none"
    period: int = Field(1, ge=1, le=1000)

class CrossoverStrategy(BaseModel):
    entry_fast_period: int = Field(7, ge=1, le=1000)
    entry_slow_period: int = Field(30, ge=1, le=1000)
    exit_fast_period: int = Field(7, ge=1, le=1000)
    exit_slow_period: int = Field(14, ge=1, le=1000)
    entry_type: Literal["sma", "ema"] = "sma"
    exit_type: Literal["sma", "ema"] = "sma"
    entry_direction: Literal["up", "down"] = "up"  # "up" = cruce al alza, "down" = cruce a la baja
    exit_direction: Literal["up", "down"] = "down"  # "up" = cruce al alza, "down" = cruce a la baja

class MultiDatasetCrossoverStrategy(BaseModel):
    # Dataset 1 (indicador principal)
    dataset1_id: int
    dataset1_indicator: Literal["v", "usd"] = "v"
    dataset1_ma_type: Literal["sma", "ema"] = "sma"
    dataset1_ma_period: int = Field(7, ge=1, le=1000)
    
    # Dataset 2 (indicador secundario)
    dataset2_id: int
    dataset2_indicator: Literal["v", "usd"] = "v"
    dataset2_ma_type: Literal["sma", "ema"] = "sma"
    dataset2_ma_period: int = Field(30, ge=1, le=1000)
    
    # Direcciones de cruce
    entry_direction: Literal["up", "down"] = "up"  # "up" = cruce al alza, "down" = cruce a la baja
    exit_direction: Literal["up", "down"] = "down"  # "up" = cruce al alza, "down" = cruce a la baja
    
    # Dataset para precio de Bitcoin (usd)
    price_dataset_id: int  # De qué dataset tomar el precio USD

class TransformRequest(BaseModel):
    v: TransformConfig = Field(default_factory=lambda: TransformConfig(type="none", period=1))
    usd: TransformConfig = Field(default_factory=lambda: TransformConfig(type="none", period=1))

class BacktestRequest(BaseModel):
    dataset_id: int
    transform: TransformRequest
    apply_to: Literal["v", "usd"] = "v"
    strategy_type: Literal["threshold", "crossover", "multi_dataset_crossover"] = "threshold"
    threshold_entry: float = 0.0
    threshold_exit: float = 0.0
    crossover_strategy: Optional[CrossoverStrategy] = None
    multi_dataset_crossover_strategy: Optional[MultiDatasetCrossoverStrategy] = None
    period: Literal[
        "1w", "1m", "3m", "6m", "1y", "ytd", 
        "2y", "4y", "6y", "8y", "10y", "all"
    ] = "all"
    fees: float = Field(0.0005, ge=0.0, le=0.1)
    slippage: float = Field(0.0002, ge=0.0, le=0.1)
    init_cash: float = Field(10000.0, gt=0.0)
    override_freq: Optional[str] = None
    
    @validator('threshold_entry', 'threshold_exit')
    def validate_thresholds(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Los thresholds deben ser numéricos')
        return float(v)

class Dataset(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    row_count: int

class CreateDatasetRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class UpdateDatasetRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class UploadResponse(BaseModel):
    ok: bool
    rows: int
    freq_detected: str
    dataset_id: int

class EquityPoint(BaseModel):
    timestamp: str
    equity: float

class Trade(BaseModel):
    entry_date: Optional[str]
    exit_date: Optional[str]
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    return_pct: float
    duration: int
    entry_fees: float
    exit_fees: float

class BacktestResults(BaseModel):
    total_return: float
    sharpe: float
    max_drawdown: float
    trades: int

class BacktestResponse(BaseModel):
    results: BacktestResults
    equity: List[EquityPoint]
    trades: List[Trade]
    freq: str
