from pydantic import BaseModel, Field, validator, EmailStr
from typing import Dict, List, Optional, Literal, Any
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
    
    # Criterios de Take Profit y Stop Loss
    take_profit_pct: float = Field(3.0, ge=0.1, le=100.0)  # Porcentaje de ganancia para cerrar
    stop_loss_pct: float = Field(1.0, ge=0.1, le=50.0)     # Porcentaje de pérdida para cerrar
    use_take_profit: bool = True   # Si usar Take Profit
    use_stop_loss: bool = True     # Si usar Stop Loss

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
        "2y", "3y", "4y", "5y", "6y", "7y", "8y", "9y", "10y",
        "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025",
        "all"
    ] = "all"
    fees: float = Field(0.00045, ge=0.0, le=0.1)
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

# Esquemas de autenticación
class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)

class UserRegister(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    password: str = Field(..., min_length=1)
    confirm_password: str = Field(..., min_length=1)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None
    is_active: bool

class PyfolioRequest(BaseModel):
    trades: List[Dict]
    initial_cash: float = Field(10000.0, gt=0.0)

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

# Esquemas para estrategias guardadas
class SaveStrategyRequest(BaseModel):
    strategy_type: str = Field(..., min_length=1, max_length=50)
    configuration: Dict[str, Any]
    results: Dict[str, Any]
    comments: Optional[str] = Field(None, max_length=1000)
    period_description: Optional[str] = Field(None, max_length=100)

class FormattedConfiguration(BaseModel):
    dataset_name: str
    strategy_description: str
    period: str
    fees_percentage: str
    init_cash_formatted: str
    transformations: List[str]
    thresholds: Optional[Dict[str, float]]
    crossover_details: str
    apply_to: str
    raw_configuration: Dict[str, Any]

class StrategySummary(BaseModel):
    id: int
    user_id: int
    username: str
    strategy_type: str
    created_at: str
    num_trades: int
    total_pnl: float
    total_costs: float
    net_pnl: float
    comments: Optional[str]
    formatted_config: FormattedConfiguration

class StrategyDetail(BaseModel):
    id: int
    user_id: int
    username: str
    strategy_type: str
    configuration: Dict[str, Any]
    results: Dict[str, Any]
    created_at: str
    comments: Optional[str]
    formatted_config: FormattedConfiguration

class StrategiesResponse(BaseModel):
    strategies: List[StrategySummary]
    total_count: int

# Esquemas para Hyperliquid
class HyperliquidSettingsRequest(BaseModel):
    main_wallet: str = Field(..., min_length=42, max_length=42)  # Ethereum address length
    hyperliquid_wallet: str = Field(..., min_length=42, max_length=42)  # Ethereum address length
    api_secret_key: str = Field(..., min_length=64, max_length=66)  # Private key length
    
    @validator('main_wallet')
    def validate_main_wallet(cls, v):
        if not v.startswith('0x'):
            raise ValueError('La dirección de wallet principal debe comenzar con 0x')
        if len(v) != 42:
            raise ValueError('La dirección de wallet principal debe tener 42 caracteres')
        return v
    
    @validator('hyperliquid_wallet')
    def validate_hyperliquid_wallet(cls, v):
        if not v.startswith('0x'):
            raise ValueError('La dirección de wallet de Hyperliquid debe comenzar con 0x')
        if len(v) != 42:
            raise ValueError('La dirección de wallet de Hyperliquid debe tener 42 caracteres')
        return v
    
    @validator('api_secret_key')
    def validate_private_key(cls, v):
        if not v.startswith('0x'):
            v = '0x' + v
        if len(v) != 66:
            raise ValueError('La clave privada debe tener 64 caracteres (66 con 0x)')
        return v

class HyperliquidSettingsResponse(BaseModel):
    main_wallet: Optional[str]
    hyperliquid_wallet: Optional[str]
    api_secret_key: Optional[str]

# Esquemas para cambio de contraseña
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('La nueva contraseña debe tener al menos 6 caracteres')
        return v

class ChangePasswordResponse(BaseModel):
    message: str
