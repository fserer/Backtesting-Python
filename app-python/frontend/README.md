# Frontend - Backtesting App

Aplicación React para backtesting de estrategias con interfaz moderna y responsive.

## Características

- ✅ Interfaz moderna con Tailwind CSS y shadcn/ui
- ✅ Drag & drop para subida de archivos CSV
- ✅ Formulario de parámetros intuitivo
- ✅ Gráficos interactivos con Recharts
- ✅ KPIs en tiempo real
- ✅ Diseño responsive
- ✅ TypeScript para type safety

## Tecnologías

- **React 18** con TypeScript
- **Vite** para build y desarrollo
- **Tailwind CSS** para estilos
- **shadcn/ui** para componentes
- **Recharts** para gráficos
- **React Query** para gestión de estado
- **React Dropzone** para upload de archivos

## Instalación

1. **Instalar dependencias:**
```bash
npm install
```

2. **Configurar variables de entorno (opcional):**
Crear archivo `.env` si necesitas cambiar la URL del backend:
```bash
VITE_API_URL=http://localhost:8000
```

## Uso

### Desarrollo
```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

### Build para producción
```bash
npm run build
```

### Preview del build
```bash
npm run preview
```

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Componentes de shadcn/ui
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   └── label.tsx
│   │   ├── FileUploader.tsx # Componente de subida de archivos
│   │   ├── ParamsForm.tsx   # Formulario de parámetros
│   │   ├── KpiCards.tsx     # Tarjetas de KPIs
│   │   └── EquityChart.tsx  # Gráfico de equity
│   ├── lib/
│   │   ├── api.ts          # Cliente de API
│   │   └── utils.ts        # Utilidades
│   ├── App.tsx             # Componente principal
│   ├── main.tsx           # Punto de entrada
│   └── styles.css         # Estilos globales
├── public/                # Archivos estáticos
├── package.json          # Dependencias
├── vite.config.ts        # Configuración de Vite
├── tailwind.config.js    # Configuración de Tailwind
└── tsconfig.json         # Configuración de TypeScript
```

## Componentes Principales

### FileUploader
- Drag & drop para archivos CSV
- Validación de formato
- Indicadores de estado (cargando, éxito, error)
- Muestra información del archivo subido

### ParamsForm
- Configuración de transformaciones (SMA, EMA, Median)
- Parámetros de backtest (thresholds, fees, slippage)
- Validación de formulario
- Estado de carga durante ejecución

### KpiCards
- Retorno total
- Ratio Sharpe
- Máximo drawdown
- Número de operaciones
- Colores dinámicos según rendimiento

### EquityChart
- Gráfico de línea de equity
- Tooltips interactivos
- Formateo de fechas y moneda
- Responsive design

## API Integration

La aplicación se comunica con el backend a través de:

- `POST /api/upload` - Subida de archivos CSV
- `POST /api/backtest` - Ejecución de backtests
- `GET /health` - Verificación de estado

## Formato de CSV Requerido

El archivo CSV debe contener exactamente estas columnas:
- `t`: timestamp (UNIX en segundos o milisegundos)
- `v`: valor del indicador (numérico)
- `usd`: precio BTC/USD (numérico)

## Transformaciones Soportadas

- **Ninguna**: Sin transformación
- **SMA**: Media Móvil Simple
- **EMA**: Media Móvil Exponencial
- **Median**: Mediana Móvil

## Scripts Disponibles

- `npm run dev` - Servidor de desarrollo
- `npm run build` - Build de producción
- `npm run preview` - Preview del build
- `npm run lint` - Linting con ESLint

## Notas de Desarrollo

- La aplicación usa React Query para gestión de estado del servidor
- Todos los componentes son TypeScript para type safety
- Los estilos usan Tailwind CSS con variables CSS personalizadas
- Los gráficos son responsivos y se adaptan al tamaño de pantalla
- La interfaz es completamente en español
