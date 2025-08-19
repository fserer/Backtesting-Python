from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
import logging

from core.config import settings
from services.sqlite_client import (
    save_ticks, load_ticks_by_dataset, create_dataset, get_all_datasets, 
    get_dataset_by_id, update_dataset, delete_dataset
)
from services.nodecharts_service import NodeChartsService
from services.csv_ingest import process_csv_upload
from services.transform import apply_transformations
from services.backtest import run_backtest, run_multi_dataset_backtest
from services.pyfolio_service import PyfolioService
from services.auth_service import AuthService
from services.strategies_service import StrategiesService
from models.schemas import (
    BacktestRequest, BacktestResponse, UploadResponse, Dataset, 
    CreateDatasetRequest, UpdateDatasetRequest, PyfolioRequest,
    UserLogin, UserRegister, Token, User,
    SaveStrategyRequest, StrategySummary, StrategyDetail, StrategiesResponse
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de autenticación
security = HTTPBearer()
auth_service = AuthService()
strategies_service = StrategiesService()

app = FastAPI(
    title="Backtesting API",
    description="API para backtesting de estrategias con vectorbt",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Backtesting API v1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    dataset_name: str = Form(..., description="Nombre del dataset"),
    dataset_description: str = Form(None, description="Descripción del dataset")
):
    """
    Sube un archivo CSV con datos de backtesting.
    
    El CSV debe contener las columnas: t (timestamp), v (indicador), usd (precio BTC)
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")
        
        # Procesar el CSV
        df, freq_detected, rows_count = await process_csv_upload(file)
        
        # Crear el dataset
        dataset = create_dataset(dataset_name, dataset_description)
        dataset_id = dataset['id']
        
        # Guardar en SQLite
        save_ticks(dataset_id, df)
        
        return UploadResponse(
            ok=True,
            rows=rows_count,
            freq_detected=freq_detected,
            dataset_id=dataset_id
        )
        
    except ValueError as e:
        # Error específico de validación (ej: nombre duplicado)
        logger.error(f"Error de validación en upload: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest", response_model=BacktestResponse)
async def run_backtest_endpoint(request: BacktestRequest):
    """
    Ejecuta un backtest con los parámetros especificados.
    """
    try:
        # Debug: Log de la request recibida
        logger.info(f"Backtest request recibida:")
        logger.info(f"  - dataset_id: {request.dataset_id}")
        logger.info(f"  - transform.v: {request.transform.v}")
        logger.info(f"  - transform.usd: {request.transform.usd}")
        logger.info(f"  - apply_to: {request.apply_to}")
        logger.info(f"  - strategy_type: {request.strategy_type}")
        logger.info(f"  - threshold_entry: {request.threshold_entry}")
        logger.info(f"  - threshold_exit: {request.threshold_exit}")
        
        # Verificar que el dataset existe
        dataset = get_dataset_by_id(request.dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=404, 
                detail=f"Dataset con ID {request.dataset_id} no encontrado."
            )
        
        # Cargar datos desde SQLite
        df = load_ticks_by_dataset(request.dataset_id)
        
        if df.empty:
            raise HTTPException(
                status_code=400, 
                detail=f"No hay datos disponibles en el dataset '{dataset['name']}'."
            )
        
        # Aplicar transformaciones
        df_transformed = apply_transformations(df, request.transform)
        
        # Ejecutar backtest según el tipo de estrategia
        if request.strategy_type == "multi_dataset_crossover" and request.multi_dataset_crossover_strategy:
            # Estrategia multi-dataset
            strategy = request.multi_dataset_crossover_strategy
            
            # Cargar datasets adicionales
            df1 = load_ticks_by_dataset(strategy.dataset1_id)
            df2 = load_ticks_by_dataset(strategy.dataset2_id)
            price_df = load_ticks_by_dataset(strategy.price_dataset_id)
            
            if df1.empty or df2.empty or price_df.empty:
                raise HTTPException(
                    status_code=400, 
                    detail="Uno o más datasets no tienen datos disponibles."
                )
            
            # Ejecutar backtest multi-dataset
            results = run_multi_dataset_backtest(
                df1=df1,
                df2=df2,
                price_df=price_df,
                strategy=strategy.dict(),
                fees=request.fees,
                slippage=request.slippage,
                init_cash=request.init_cash,
                period=request.period
            )
        else:
            # Estrategias tradicionales (threshold o crossover)
            results = run_backtest(
                df=df_transformed,
                threshold_entry=request.threshold_entry,
                threshold_exit=request.threshold_exit,
                fees=request.fees,
                slippage=request.slippage,
                init_cash=request.init_cash,
                apply_to=request.apply_to,
                override_freq=request.override_freq,
                strategy_type=request.strategy_type,
                crossover_strategy=request.crossover_strategy.dict() if request.crossover_strategy else None,
                multi_dataset_crossover_strategy=request.multi_dataset_crossover_strategy.dict() if request.multi_dataset_crossover_strategy else None,
                period=request.period
            )
        
        return BacktestResponse(**results)
        
    except Exception as e:
        logger.error(f"Error en backtest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets", response_model=List[Dataset])
async def get_datasets():
    """
    Obtiene todos los datasets disponibles.
    """
    try:
        datasets = get_all_datasets()
        return datasets
        
    except Exception as e:
        logger.error(f"Error obteniendo datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: int):
    """
    Obtiene un dataset específico por ID.
    """
    try:
        dataset = get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset no encontrado")
        
        return dataset
        
    except Exception as e:
        logger.error(f"Error obteniendo dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/datasets/{dataset_id}", response_model=Dataset)
async def update_dataset_endpoint(dataset_id: int, request: UpdateDatasetRequest):
    """
    Actualiza un dataset existente.
    """
    try:
        # Verificar que el dataset existe
        dataset = get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset no encontrado")
        
        # Actualizar el dataset
        updated_dataset = update_dataset(
            dataset_id, 
            name=request.name, 
            description=request.description
        )
        
        return updated_dataset
        
    except Exception as e:
        logger.error(f"Error actualizando dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/datasets/{dataset_id}")
async def delete_dataset_endpoint(dataset_id: int):
    """
    Elimina un dataset y todos sus datos.
    """
    try:
        # Verificar que el dataset existe
        dataset = get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset no encontrado")
        
        # Eliminar el dataset
        delete_dataset(dataset_id)
        
        return {"message": f"Dataset '{dataset['name']}' eliminado correctamente"}
        
    except Exception as e:
        logger.error(f"Error eliminando dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/datasets/{dataset_id}/update")
async def update_dataset_from_nodecharts(dataset_id: int):
    """
    Actualiza un dataset con datos nuevos desde NodeCharts.
    """
    try:
        # Obtener el dataset
        dataset = get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} no encontrado")
        
        # Inicializar servicio de NodeCharts
        api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdG9yZSI6MCwidXNlcmlkIjoyNTUyLCJjcmVhdGlvbnRpbWUiOjE3MTM3Nzc0NTJ9.bFd4Y_134nmvUjboy8CZRkMRc8WngTA9_zDx18qAkXE"
        nodecharts_service = NodeChartsService(api_key)
        
        # Actualizar el dataset
        success, rows_added = nodecharts_service.update_dataset(dataset['name'], None)
        
        if success:
            return {
                "message": f"Dataset {dataset['name']} actualizado correctamente",
                "rows_added": rows_added,
                "dataset_id": dataset_id
            }
        else:
            raise HTTPException(status_code=500, detail=f"Error actualizando dataset {dataset['name']}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/datasets/update-all")
async def update_all_datasets_from_nodecharts():
    """
    Actualiza todos los datasets que tienen mapeo con NodeCharts.
    """
    try:
        # Inicializar servicio de NodeCharts
        api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdG9yZSI6MCwidXNlcmlkIjoyNTUyLCJjcmVhdGlvbnRpbWUiOjE3MTM3Nzc0NTJ9.bFd4Y_134nmvUjboy8CZRkMRc8WngTA9_zDx18qAkXE"
        nodecharts_service = NodeChartsService(api_key)
        
        # Actualizar todos los datasets
        results = nodecharts_service.update_all_datasets(None)
        
        return {
            "message": "Actualización completada",
            "results": results
        }
            
    except Exception as e:
        logger.error(f"Error actualizando todos los datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pyfolio")
async def generate_pyfolio_analysis(request: PyfolioRequest):
    """
    Genera análisis completo de Pyfolio basado en los trades del backtesting.
    
    Args:
        trades: Lista de trades del backtesting
        initial_cash: Capital inicial (por defecto 10000.0)
        
    Returns:
        Análisis completo de Pyfolio con métricas, drawdowns y datos para visualizaciones
    """
    try:
        if not request.trades:
            raise HTTPException(status_code=400, detail="No hay trades para analizar")
        
        # Inicializar servicio de Pyfolio
        pyfolio_service = PyfolioService()
        
        # Generar análisis completo
        analysis = pyfolio_service.generate_full_report(request.trades, request.initial_cash)
        
        logger.info(f"Análisis de Pyfolio generado para {len(request.trades)} trades")
        return analysis
        
    except Exception as e:
        logger.error(f"Error generando análisis de Pyfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================================================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Obtiene el usuario actual basado en el token JWT"""
    token = credentials.credentials
    user = auth_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/api/auth/register", response_model=Dict[str, Any])
async def register_user(user_data: UserRegister):
    """
    Registra un nuevo usuario.
    """
    try:
        user = auth_service.create_user(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email
        )
        
        # Crear token de acceso
        access_token = auth_service.create_access_token(data={"sub": user["username"]})
        
        return {
            "message": "Usuario registrado exitosamente",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/auth/login", response_model=Token)
async def login_user(user_data: UserLogin):
    """
    Autentica un usuario y devuelve un token JWT.
    """
    try:
        user = auth_service.authenticate_user(user_data.username, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear token de acceso
        access_token = auth_service.create_access_token(data={"sub": user["username"]})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Obtiene información del usuario actual.
    """
    try:
        user = auth_service.get_user_by_id(current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return User(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo información del usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/auth/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Verifica si el token es válido.
    """
    return {"valid": True, "user": current_user}

# ============================================================================
# ENDPOINTS DE ESTRATEGIAS
# ============================================================================

@app.post("/api/strategies/save", response_model=Dict[str, Any])
async def save_strategy(
    strategy_data: SaveStrategyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Guarda una estrategia de backtesting.
    """
    try:
        # Obtener el nombre del dataset
        dataset_name = None
        if strategy_data.configuration.get('dataset_id'):
            try:
                dataset = get_dataset_by_id(strategy_data.configuration['dataset_id'])
                if dataset:
                    dataset_name = dataset['name']
            except Exception as e:
                logger.warning(f"No se pudo obtener el nombre del dataset {strategy_data.configuration['dataset_id']}: {e}")
        
        strategy = strategies_service.save_strategy(
            user_id=current_user["id"],
            username=current_user["username"],
            strategy_type=strategy_data.strategy_type,
            configuration=strategy_data.configuration,
            results=strategy_data.results,
            comments=strategy_data.comments,
            dataset_name=dataset_name,
            period_description=strategy_data.period_description
        )
        
        return {
            "message": "Estrategia guardada exitosamente",
            "strategy": strategy
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error guardando estrategia: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/strategies", response_model=StrategiesResponse)
async def get_all_strategies(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Obtiene todas las estrategias de todos los usuarios.
    """
    try:
        strategies = strategies_service.get_all_strategies()
        
        # Convertir a StrategySummary
        strategy_summaries = []
        for strategy in strategies:
            strategy_summaries.append(StrategySummary(
                id=strategy["id"],
                user_id=strategy["user_id"],
                username=strategy["username"],
                strategy_type=strategy["strategy_type"],
                created_at=strategy["created_at"],
                num_trades=strategy["num_trades"],
                total_pnl=strategy["total_pnl"],
                total_costs=strategy["total_costs"],
                net_pnl=strategy["net_pnl"],
                comments=strategy["comments"],
                formatted_config=strategy["formatted_config"]
            ))
        
        return StrategiesResponse(
            strategies=strategy_summaries,
            total_count=len(strategy_summaries)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estrategias: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/strategies/{strategy_id}", response_model=StrategyDetail)
async def get_strategy_by_id(
    strategy_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtiene una estrategia específica por ID.
    """
    try:
        strategy = strategies_service.get_strategy_by_id(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Estrategia no encontrada")
        
        return StrategyDetail(**strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estrategia {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Elimina una estrategia (solo el propietario puede eliminarla).
    """
    try:
        success = strategies_service.delete_strategy(strategy_id, current_user["id"])
        if not success:
            raise HTTPException(status_code=404, detail="Estrategia no encontrada o no tienes permisos para eliminarla")
        
        return {"message": "Estrategia eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando estrategia {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
