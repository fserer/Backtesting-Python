from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
import logging

from core.config import settings
from services.sqlite_client import (
    save_ticks, load_ticks_by_dataset, create_dataset, get_all_datasets, 
    get_dataset_by_id, update_dataset, delete_dataset
)
from services.csv_ingest import process_csv_upload
from services.transform import apply_transformations
from services.backtest import run_backtest, run_multi_dataset_backtest
from services.quantstats_service import QuantStatsService
from models.schemas import (
    BacktestRequest, BacktestResponse, UploadResponse, Dataset, 
    CreateDatasetRequest, UpdateDatasetRequest, QuantStatsRequest
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.post("/api/quantstats")
async def generate_quantstats_analysis(request: QuantStatsRequest):
    """
    Genera análisis completo de QuantStats basado en los trades del backtesting.
    
    Args:
        trades: Lista de trades del backtesting
        initial_cash: Capital inicial (por defecto 10000.0)
        
    Returns:
        Análisis completo de QuantStats con métricas, drawdowns y datos para visualizaciones
    """
    try:
        if not request.trades:
            raise HTTPException(status_code=400, detail="No hay trades para analizar")
        
        # Inicializar servicio de QuantStats
        quantstats_service = QuantStatsService()
        
        # Generar serie de retornos desde los trades
        returns_series = quantstats_service.generate_returns_series(request.trades, request.initial_cash)
        
        if returns_series.empty:
            raise HTTPException(status_code=400, detail="No se pudo generar serie de retornos válida")
        
        # Generar análisis completo
        analysis = quantstats_service.generate_full_report(returns_series)
        
        logger.info(f"Análisis de QuantStats generado para {len(request.trades)} trades")
        return analysis
        
    except Exception as e:
        logger.error(f"Error generando análisis de QuantStats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
