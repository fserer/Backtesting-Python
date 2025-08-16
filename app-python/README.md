# App Python - Backtesting Platform

Plataforma completa de backtesting con FastAPI (backend) y React (frontend) para análisis de estrategias de trading usando vectorbt.

## 🚀 Características

### Backend (FastAPI)
- ✅ API RESTful con FastAPI
- ✅ Subida y validación de archivos CSV
- ✅ Detección automática de frecuencia (diaria/horaria)
- ✅ Transformaciones: SMA, EMA, Median
- ✅ Backtesting con vectorbt
- ✅ Integración con Supabase (PostgreSQL)
- ✅ Validación con Pydantic
- ✅ CORS configurado

### Frontend (React)
- ✅ Interfaz moderna con Tailwind CSS y shadcn/ui
- ✅ Drag & drop para subida de archivos
- ✅ Formulario de parámetros intuitivo
- ✅ Gráficos interactivos con Recharts
- ✅ KPIs en tiempo real
- ✅ Diseño responsive
- ✅ TypeScript para type safety

## 🏗️ Arquitectura

```
app-python/
├── backend/                 # API FastAPI
│   ├── app.py              # Aplicación principal
│   ├── core/               # Configuración
│   ├── services/           # Lógica de negocio
│   ├── models/             # Esquemas Pydantic
│   └── requirements.txt    # Dependencias Python
├── frontend/               # Aplicación React
│   ├── src/                # Código fuente
│   ├── components/         # Componentes React
│   └── package.json       # Dependencias Node.js
├── samples/               # Datos de ejemplo
├── docker-compose.yml     # Orquestación Docker
└── README.md             # Este archivo
```

## 📋 Prerrequisitos

- Python 3.11+
- Node.js 18+
- Cuenta en [Supabase](https://supabase.com)

## 🛠️ Instalación

### 1. Configurar Supabase

1. Crear proyecto en [Supabase](https://supabase.com)
2. Obtener URL y ANON KEY desde Settings > API
3. Ejecutar este SQL en el SQL Editor:

```sql
create table if not exists ticks (
  id bigserial primary key,
  t timestamptz not null,
  v double precision not null,
  usd double precision not null
);
create index if not exists idx_ticks_t on ticks(t);
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Supabase
SUPABASE_URL=tu_supabase_url
SUPABASE_ANON_KEY=tu_supabase_anon_key

# Frontend (opcional)
VITE_API_URL=http://localhost:8000
```

### 3. Instalar Dependencias

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

## 🚀 Uso

### Opción 1: Desarrollo Local

#### Backend
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run dev
```

### Opción 2: Docker Compose

```bash
docker-compose up --build
```

### Opción 3: Solo Backend con Docker

```bash
cd backend
docker build -t backtesting-backend .
docker run -p 8000:8000 --env-file ../.env backtesting-backend
```

## 📊 Formato de Datos

El archivo CSV debe contener exactamente estas columnas:

```csv
t,v,usd
1640995200,0.5,46200.5
1641081600,0.3,45800.2
...
```

- `t`: timestamp UNIX (segundos o milisegundos)
- `v`: valor del indicador (numérico)
- `usd`: precio BTC/USD (numérico)

## 🔧 Transformaciones Soportadas

- **Ninguna**: Sin transformación
- **SMA**: Media Móvil Simple
- **EMA**: Media Móvil Exponencial
- **Median**: Mediana Móvil

## 📈 KPIs Calculados

- **Retorno Total**: Porcentaje de ganancia/pérdida
- **Ratio Sharpe**: Medida de rendimiento ajustado al riesgo
- **Máximo Drawdown**: Mayor caída desde un pico
- **Operaciones**: Número total de trades

## 🌐 Endpoints API

### POST /api/upload
Sube archivo CSV para backtesting.

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data.csv"
```

### POST /api/backtest
Ejecuta backtest con parámetros.

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/backtest" \
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

## 📁 Estructura de Archivos

### Backend
```
backend/
├── app.py                 # FastAPI app
├── core/
│   └── config.py         # Configuración
├── services/
│   ├── supabase_client.py # Cliente Supabase
│   ├── csv_ingest.py     # Procesamiento CSV
│   ├── transform.py      # Transformaciones
│   └── backtest.py       # Lógica backtesting
├── models/
│   └── schemas.py        # Esquemas Pydantic
└── requirements.txt      # Dependencias
```

### Frontend
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # Componentes shadcn/ui
│   │   ├── FileUploader.tsx
│   │   ├── ParamsForm.tsx
│   │   ├── KpiCards.tsx
│   │   └── EquityChart.tsx
│   ├── lib/
│   │   ├── api.ts       # Cliente API
│   │   └── utils.ts     # Utilidades
│   ├── App.tsx          # Componente principal
│   └── main.tsx         # Punto de entrada
├── package.json         # Dependencias
└── vite.config.ts       # Configuración Vite
```

## 🧪 Datos de Ejemplo

Incluido archivo `samples/data.csv` con ~100 filas de datos de ejemplo para pruebas.

## 🔍 Troubleshooting

### Error de CORS
- Verificar que el backend esté corriendo en puerto 8000
- Verificar configuración CORS en `backend/app.py`

### Error de Supabase
- Verificar variables de entorno
- Verificar que la tabla `ticks` exista
- Verificar permisos de la API key

### Error de vectorbt
- Verificar que los datos CSV tengan el formato correcto
- Verificar que no haya valores nulos

## 📝 Notas de Desarrollo

- Backend usa FastAPI con validación automática
- Frontend usa React Query para gestión de estado
- Todos los componentes son TypeScript
- Gráficos responsivos con Recharts
- Interfaz completamente en español

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte, crear un issue en el repositorio o contactar al equipo de desarrollo.
