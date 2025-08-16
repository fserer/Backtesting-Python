# Backend - Backtesting API

API de FastAPI para backtesting de estrategias usando vectorbt.

## Características

- ✅ Subida y validación de archivos CSV
- ✅ Detección automática de frecuencia (diaria/horaria)
- ✅ Transformaciones: SMA, EMA, Median
- ✅ Backtesting con vectorbt
- ✅ Integración con Supabase (PostgreSQL)
- ✅ CORS configurado para frontend

## Instalación

1. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar Supabase:**
   - Crear proyecto en [Supabase](https://supabase.com)
   - Copiar URL y ANON KEY
   - Crear archivo `.env` basado en `env.example`:
```bash
cp env.example .env
```

4. **Configurar base de datos:**
   Ejecutar este SQL en el SQL Editor de Supabase:
```sql
create table if not exists ticks (
  id bigserial primary key,
  t timestamptz not null,
  v double precision not null,
  usd double precision not null
);
create index if not exists idx_ticks_t on ticks(t);
```

## Uso

### Desarrollo
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Producción
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Endpoints

### POST /api/upload
Sube un archivo CSV con datos de backtesting.

**Formato CSV requerido:**
- `t`: timestamp (UNIX en segundos o milisegundos)
- `v`: valor del indicador (numérico)
- `usd`: precio BTC/USD (numérico)

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data.csv"
```

**Respuesta:**
```json
{
  "ok": true,
  "rows": 1000,
  "freq_detected": "1D"
}
```

### POST /api/backtest
Ejecuta un backtest con los parámetros especificados.

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "transform": {
      "v": {"type": "sma", "period": 20},
      "usd": {"type": "none", "period": 1}
    },
    "apply_to": "v",
    "threshold_entry": 0.5,
    "threshold_exit": -0.5,
    "fees": 0.0005,
    "slippage": 0.0002,
    "init_cash": 10000.0
  }'
```

**Respuesta:**
```json
{
  "results": {
    "total_return": 0.15,
    "sharpe": 1.2,
    "max_drawdown": -0.08,
    "trades": 25
  },
  "equity": [
    {"timestamp": "2023-01-01T00:00:00Z", "equity": 10000.0},
    {"timestamp": "2023-01-02T00:00:00Z", "equity": 10100.0}
  ],
  "freq": "1D"
}
```

## Transformaciones Soportadas

- `none`: Sin transformación
- `sma`: Media Móvil Simple
- `ema`: Media Móvil Exponencial
- `median`: Mediana Móvil

## Estructura del Proyecto

```
backend/
├── app.py                 # Aplicación principal FastAPI
├── core/
│   └── config.py         # Configuración y variables de entorno
├── services/
│   ├── supabase_client.py # Cliente de Supabase
│   ├── csv_ingest.py     # Procesamiento de CSV
│   ├── transform.py      # Transformaciones de datos
│   └── backtest.py       # Lógica de backtesting
├── models/
│   └── schemas.py        # Esquemas Pydantic
├── requirements.txt      # Dependencias Python
└── README.md            # Este archivo
```

## Variables de Entorno

- `SUPABASE_URL`: URL de tu proyecto Supabase
- `SUPABASE_ANON_KEY`: Clave anónima de Supabase
- `DEBUG`: Modo debug (True/False)

## Notas

- Los datos se guardan en Supabase y se cargan automáticamente para el backtest
- La frecuencia se detecta automáticamente (1D para diario, 1H para horario)
- Los timestamps se normalizan a UTC automáticamente
- Se soportan timestamps en segundos y milisegundos
