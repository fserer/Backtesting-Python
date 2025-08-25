# Hyperliquid Positions Checker

Un proyecto completo en Python para consultar información detallada de tu cuenta en Hyperliquid usando el SDK oficial.

## Características

### Script Básico (`hyperliquid_positions.py`)
- 🔗 Conexión automática a Hyperliquid Mainnet
- 📊 Visualización de posiciones abiertas
- 💰 Información de margen y colateral
- 💎 Balances spot
- 📈 Cálculo de PnL no realizado
- 🎨 Interfaz con emojis para mejor legibilidad

### Script Detallado (`hyperliquid_detailed_info.py`)
- 📊 Estado completo de la cuenta con ratios de margen
- 📈 Posiciones con precios de liquidación
- 📋 Órdenes abiertas
- 🔄 Historial de trades recientes
- 💎 Balances spot detallados
- 📊 Resúmenes y estadísticas

### Script de Cierre de Posiciones (`hyperliquid_close_position.py`)
- 🚀 Cierre de posiciones a market price
- 📈 Visualización de posiciones disponibles
- ⚠️ Confirmación de seguridad antes de ejecutar
- 📊 Verificación del estado después del cierre
- 📤 **Muestra el payload que se envía a la API**

### Script de Ampliación de Posiciones (`hyperliquid_increase_position.py`)
- 📈 Ampliar posiciones existentes
- 💰 Agregar más exposición al mismo activo
- ⚠️ Confirmación de seguridad antes de ejecutar
- 📊 Cálculo del nuevo tamaño total
- 📤 **Muestra el payload que se envía a la API**

### Script de Reducción de Posiciones (`hyperliquid_reduce_position.py`)
- 📉 Reducir posiciones existentes
- 💰 Disminuir exposición al activo
- 🔄 Opción de cierre completo
- ⚠️ Confirmación de seguridad antes de ejecutar
- 📤 **Muestra el payload que se envía a la API**

### Script de Apertura de Posiciones (`hyperliquid_open_position.py`)
 - 🆕 Abrir nuevas posiciones desde cero
 - 🪙 Lista completa de coins disponibles
 - 📈 Selección de dirección (LONG/SHORT)
 - ⚡ Configuración de leverage
 - 💰 Cálculo de margen requerido
 - 📤 **Muestra el payload que se envía a la API**

### Script de Demostración de Payloads (`hyperliquid_demo_payloads.py`)
 - 📋 Demostración de payloads sin ejecutar órdenes reales
 - 🔍 Ejemplos de diferentes tipos de órdenes
 - 📚 Explicación detallada de la estructura de payloads
 - 🔒 **Solo demostración - no ejecuta órdenes reales**

## Instalación

1. **Crear entorno virtual:**
```bash
python3 -m venv venv
```

2. **Activar entorno virtual e instalar dependencias:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configurar credenciales:**
El archivo `config.json` ya está configurado con tus credenciales:
- `account_address`: Tu dirección de wallet
- `secret_key`: Tu clave privada

## Uso

### Script Básico (Posiciones)

#### Opción 1: Usar el script de shell (recomendado)
```bash
./run.sh
```

#### Opción 2: Ejecutar manualmente
```bash
source venv/bin/activate
python hyperliquid_positions.py
```

### Script Detallado (Información Completa)

#### Opción 1: Usar el script de shell (recomendado)
```bash
./run_detailed.sh
```

#### Opción 2: Ejecutar manualmente
```bash
source venv/bin/activate
python hyperliquid_detailed_info.py
```

### Script de Cierre de Posiciones

#### Opción 1: Usar el script de shell (recomendado)
```bash
./run_close_position.sh
```

#### Opción 2: Ejecutar manualmente
```bash
source venv/bin/activate
python hyperliquid_close_position.py
```

### Script de Ampliación de Posiciones

#### Opción 1: Usar el script de shell (recomendado)
```bash
./run_increase_position.sh
```

#### Opción 2: Ejecutar manualmente
```bash
source venv/bin/activate
python hyperliquid_increase_position.py
```

### Script de Reducción de Posiciones

#### Opción 1: Usar el script de shell (recomendado)
```bash
./run_reduce_position.sh
```

#### Opción 2: Ejecutar manualmente
```bash
source venv/bin/activate
python hyperliquid_reduce_position.py
```

### Script de Apertura de Posiciones

#### Opción 1: Usar el script de shell (recomendado)
```bash
./run_open_position.sh
```

#### Opción 2: Ejecutar manualmente
```bash
source venv/bin/activate
python hyperliquid_open_position.py
```

### Script de Demostración de Payloads

#### Opción 1: Usar el script de shell (recomendado)
```bash
./run_demo_payloads.sh
```

#### Opción 2: Ejecutar manualmente
```bash
source venv/bin/activate
python hyperliquid_demo_payloads.py
```

## Ejemplo de salida

### Script Básico
```
🚀 Iniciando consulta de posiciones en Hyperliquid...
🔗 Conectando con cuenta: 0xFc9f61267Def9B40987F18693f1EbA82C2DdD472

============================================================
📊 ESTADO DE LA CUENTA
============================================================
💰 Valor de la cuenta: $98.05
📈 Margen total usado: $7.19
💵 Total USD: $134.00
💸 Fondos retirables: $90.86
✅ Colateral libre: $90.86

============================================================
📈 POSICIONES ABIERTAS
============================================================

1. ETH 🔴 SHORT
   📊 Tamaño: 0.010000
   ⚡ Leverage: 5x
   💰 Precio de entrada: $3,638.80
   💵 Valor de posición: $35.95
   📈 PnL no realizado: $0.44
   📈 PnL %: +1.22%

============================================================
💎 BALANCES SPOT
============================================================
✅ No hay balances spot disponibles
   💡 Los balances spot aparecen cuando tienes tokens en el trading spot de Hyperliquid

============================================================
✅ Consulta completada
============================================================
```

### Script Detallado
```
🚀 Iniciando consulta detallada de Hyperliquid...
🔗 Conectando con cuenta: 0xFc9f61267Def9B40987F18693f1EbA82C2DdD472

============================================================
📊 ESTADO COMPLETO DE LA CUENTA
============================================================
💰 Valor de la cuenta: $98.05
📈 Margen total usado: $7.19
💵 Total USD: $134.00
💸 Fondos retirables: $90.86
✅ Colateral libre: $90.86
📊 Ratio de margen: 1263.40%

============================================================
📈 POSICIONES ABIERTAS (DETALLADO)
============================================================

1. ETH 🔴 SHORT
   📊 Tamaño: 0.010000
   ⚡ Leverage: 5x
   💰 Precio de entrada: $3,638.80
   💵 Valor de posición: $35.96
   📈 PnL no realizado: $0.43
   📈 PnL %: +1.20%
   ⚠️  Precio de liquidación: $13,137.67

📊 RESUMEN DE POSICIONES:
   💵 Valor total de posiciones: $35.96
   📈 PnL total no realizado: $0.43
   📊 PnL total %: +1.20%

============================================================
📋 ÓRDENES ABIERTAS
============================================================
✅ No hay órdenes abiertas

============================================================
🔄 TRADES RECIENTES (Últimas 24h)
============================================================

1. ETH 🔴 VENTA - 09:18:49
   📊 Tamaño: 0.010000
   💰 Precio: $3,638.80
   💵 Volumen: $36.39
   💸 Fee: $0.0164

📊 RESUMEN DE TRADES:
   💵 Volumen total: $770.59
   💸 Fees totales: $0.3468

============================================================
💎 BALANCES SPOT (DETALLADO)
============================================================
✅ No hay balances spot disponibles
   💡 Los balances spot aparecen cuando tienes tokens en el trading spot de Hyperliquid

============================================================
✅ Consulta detallada completada
============================================================
```

## Seguridad

⚠️ **Importante:** 
- Nunca compartas tu `secret_key` 
- El archivo `config.json` contiene información sensible
- Considera usar variables de entorno para mayor seguridad

## Estructura del proyecto

```
.
├── hyperliquid_positions.py      # Script básico de posiciones
├── hyperliquid_detailed_info.py  # Script detallado completo
├── hyperliquid_close_position.py # Script de cierre de posiciones
├── hyperliquid_increase_position.py # Script de ampliación de posiciones
├── hyperliquid_reduce_position.py   # Script de reducción de posiciones
├── hyperliquid_open_position.py     # Script de apertura de posiciones
├── config.json                   # Configuración con credenciales
├── requirements.txt              # Dependencias de Python
├── run.sh                        # Script de ejecución básico
├── run_detailed.sh               # Script de ejecución detallado
├── run_close_position.sh         # Script de ejecución de cierre
├── run_increase_position.sh      # Script de ejecución de ampliación
├── run_reduce_position.sh        # Script de ejecución de reducción
├── run_open_position.sh          # Script de ejecución de apertura
├── venv/                         # Entorno virtual (se crea automáticamente)
└── README.md                     # Este archivo
```

## Dependencias

- `hyperliquid-python-sdk`: SDK oficial de Hyperliquid
- `eth-account`: Para manejo de cuentas Ethereum
- `requests`: Para peticiones HTTP

## Solución de problemas

Si encuentras errores:

1. **Verifica que las credenciales sean correctas** en `config.json`
2. **Asegúrate de tener fondos** en la cuenta de Hyperliquid
3. **Revisa la conexión a internet**
4. **Verifica que el SDK esté instalado correctamente**

## Notas adicionales

- El script se conecta a **Mainnet** por defecto
- Si no hay posiciones abiertas, mostrará un mensaje informativo
- Los **balances spot** aparecen cuando tienes tokens en el trading spot de Hyperliquid
- Si no tienes balances spot, el script mostrará un mensaje explicativo
- El script muestra información completa incluyendo:
  - Valor total de la cuenta
  - Fondos retirables
  - Colateral libre
  - Ratio de margen
  - Leverage de las posiciones
  - Precios de liquidación

## 📤 Payloads de API

Todos los scripts de trading ahora muestran los payloads que se envían a la API de Hyperliquid antes de ejecutar las órdenes. Esto te permite:

- **Verificar la estructura** de las órdenes antes de ejecutarlas
- **Entender exactamente** qué datos se envían a la API
- **Debuggear** problemas con las órdenes
- **Aprender** la estructura de la API de Hyperliquid

### Ejemplo de Payload mostrado:
```json
{
  "type": "order",
  "orders": [{
    "a": 1,        // ID del activo (1 = ETH)
    "b": true,     // is_buy (true = compra)
    "p": "0",      // limit_px (0 = market)
    "s": "0.01",   // size (tamaño)
    "r": false,    // reduce_only
    "t": {         // order_type
      "limit": {
        "tif": "Ioc"  // Immediate or Cancel
      }
    }
  }],
  "grouping": "na"
}
```

### Script de Demostración
Usa `./run_demo_payloads.sh` para ver ejemplos de payloads sin ejecutar órdenes reales.

## ⚠️ Seguridad

- **Todos los scripts de trading ejecutan órdenes reales** en Mainnet
- Siempre verifica la información antes de confirmar
- Los scripts requieren confirmación manual escribiendo 'SI'
- Las órdenes se ejecutan a market price, por lo que el precio puede variar
- **Recomendación:** Prueba primero con cantidades pequeñas
- **Los payloads se muestran** para que puedas verificar qué se envía 