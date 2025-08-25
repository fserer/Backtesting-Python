# Lista de Activos de Hyperliquid - Resumen

## 📊 Información General
- **Total de activos**: 202
- **Fecha de exportación**: 2024-12-19
- **Fuente**: Hyperliquid API

## 🪙 Activos Principales (Top 20 por importancia)

| ID | Símbolo | Nombre | Max Leverage | Decimales |
|----|---------|--------|--------------|-----------|
| 0  | BTC     | Bitcoin | 40x | 5 |
| 1  | ETH     | Ethereum | 25x | 4 |
| 5  | SOL     | Solana | 20x | 2 |
| 6  | AVAX    | Avalanche | 10x | 2 |
| 7  | BNB     | Binance Coin | 10x | 3 |
| 11 | ARB     | Arbitrum | 20x | 1 |
| 12 | DOGE    | Dogecoin | 20x | 0 |
| 13 | INJ     | Injective | 20x | 2 |
| 14 | SUI     | Sui | 20x | 1 |
| 18 | LINK    | Chainlink | 20x | 1 |
| 25 | XRP     | Ripple | 20x | 0 |
| 26 | BCH     | Bitcoin Cash | 20x | 3 |
| 27 | APT     | Aptos | 20x | 1 |
| 28 | AAVE    | Aave | 10x | 2 |
| 29 | COMP    | Compound | 10x | 2 |
| 30 | MKR     | Maker | 10x | 3 |
| 31 | WLD     | Worldcoin | 20x | 1 |
| 38 | UNI     | Uniswap | 20x | 1 |
| 48 | DOT     | Polkadot | 20x | 1 |
| 65 | ADA     | Cardano | 20x | 0 |

## 🔥 Memecoins y Tokens Populares

| ID | Símbolo | Max Leverage | Decimales |
|----|---------|--------------|-----------|
| 15 | kPEPE   | 20x | 0 |
| 38 | kSHIB   | 20x | 0 |
| 75 | MEME    | 20x | 0 |
| 76 | ORDI    | 20x | 0 |
| 85 | kBONK   | 20x | 0 |
| 91 | kLUNC   | 20x | 0 |
| 98 | WIF     | 20x | 0 |
| 119 | kFLOKI | 20x | 0 |
| 120 | BOME    | 20x | 0 |
| 141 | kDOGS   | 20x | 0 |

## 🆕 Tokens Nuevos y Trending

| ID | Símbolo | Max Leverage | Decimales |
|----|---------|--------------|-----------|
| 103 | XAI     | 20x | 1 |
| 104 | MANTA   | 20x | 1 |
| 113 | STRK    | 20x | 1 |
| 114 | PIXEL   | 20x | 1 |
| 115 | AI      | 20x | 1 |
| 116 | TAO     | 20x | 1 |
| 121 | ETHFI   | 20x | 1 |
| 122 | ENA     | 20x | 1 |
| 125 | SAGA    | 20x | 1 |
| 130 | EIGEN   | 20x | 1 |

## 📋 Cómo usar los IDs en órdenes API

### Ejemplo de Orden de Mercado (Market Order)
```json
{
  "type": "order",
  "orders": [{
    "a": 1,        // ID del activo (1 = ETH)
    "b": true,     // is_buy (true = compra, false = venta)
    "p": "0",      // limit_px (0 para market)
    "s": "0.01",   // size (tamaño de la orden)
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

### Ejemplo de Consulta de Información
```json
{
  "type": "l2Book",
  "coin": "ETH"    // Símbolo del activo
}
```

## 🔗 URLs de API

- **Exchange API**: `https://api.hyperliquid.xyz/exchange`
- **Info API**: `https://api.hyperliquid.xyz/info`
- **Documentación**: https://hyperliquid.gitbook.io/hyperliquid/

## 📁 Archivos Generados

- `hyperliquid_assets.json` - Lista completa en formato JSON
- `hyperliquid_assets.csv` - Lista completa en formato CSV

## ⚠️ Notas Importantes

1. **IDs**: Los IDs son secuenciales empezando desde 0
2. **Leverage**: El leverage máximo puede variar según las condiciones del mercado
3. **Decimales**: Indica la precisión decimal para el tamaño de las órdenes
4. **Estado**: Todos los activos mostrados están activos, excepto MATIC que está delistado
5. **Actualización**: Esta lista se actualiza automáticamente desde la API de Hyperliquid

## 🚀 Uso en Diferentes Lenguajes

### Python
```python
# Usar el ID directamente
asset_id = 1  # ETH
order_size = "0.01"
```

### JavaScript
```javascript
// Usar el ID directamente
const assetId = 1; // ETH
const orderSize = "0.01";
```

### Go
```go
// Usar el ID directamente
assetID := 1 // ETH
orderSize := "0.01"
```

### Rust
```rust
// Usar el ID directamente
let asset_id: u32 = 1; // ETH
let order_size: String = "0.01".to_string();
``` 