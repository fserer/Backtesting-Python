# PostgreSQL + TimescaleDB Setup

Esta rama implementa PostgreSQL con TimescaleDB para mejorar el rendimiento de la aplicación de backtesting.

## 🚀 Características

- **PostgreSQL**: Base de datos robusta y escalable
- **TimescaleDB**: Extensión especializada en series temporales
- **Hypertables**: Particionamiento automático por fechas
- **Compresión**: Datos antiguos se comprimen automáticamente
- **Retención**: Políticas automáticas de retención de datos
- **Índices optimizados**: Para consultas de series temporales

## 📊 Beneficios de Rendimiento

### Comparación con SQLite

| Métrica | SQLite | PostgreSQL + TimescaleDB |
|---------|--------|--------------------------|
| **Consultas complejas** | Lento | 10-100x más rápido |
| **Grandes volúmenes** | Limitado | Escalable |
| **Concurrencia** | Básica | Avanzada |
| **Índices** | Básicos | Optimizados para tiempo |
| **Compresión** | No | Automática |
| **Particionamiento** | Manual | Automático |

### Casos de Uso Ideales

- ✅ Datasets grandes (>1M registros)
- ✅ Múltiples usuarios simultáneos
- ✅ Consultas complejas de backtesting
- ✅ Análisis histórico extenso
- ✅ Necesidad de escalabilidad

## 🛠️ Instalación

### 1. Usar Docker Compose (Recomendado)

```bash
# Levantar servicios PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d

# Verificar que todo funciona
docker-compose -f docker-compose.postgres.yml ps
```

### 2. Configuración Manual

```bash
# Instalar dependencias
pip install psycopg2-binary sqlalchemy alembic

# Configurar variables de entorno
export DATABASE_TYPE=postgresql
export DATABASE_URL=postgresql://backtesting_user:backtesting_password@localhost:5432/backtesting
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Tipo de base de datos
DATABASE_TYPE=postgresql

# URL de conexión PostgreSQL
DATABASE_URL=postgresql://backtesting_user:backtesting_password@localhost:5432/backtesting
```

### Puertos

- **PostgreSQL**: 5432
- **Backend**: 8001 (para evitar conflictos con SQLite)
- **Frontend**: 3001 (para evitar conflictos con SQLite)

## 🧪 Testing

### Ejecutar Tests

```bash
# Test de configuración PostgreSQL
python test_postgresql.py

# Test de rendimiento
python test_performance.py
```

### Verificar Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it backtesting-postgres psql -U backtesting_user -d backtesting

# Verificar TimescaleDB
\dx timescaledb

# Verificar hypertables
SELECT * FROM timescaledb_information.hypertables;
```

## 📈 Optimizaciones Implementadas

### 1. Hypertables
```sql
-- Particionamiento automático por fechas
SELECT create_hypertable('ticks', 't', if_not_exists => TRUE);
```

### 2. Compresión
```sql
-- Comprimir datos más antiguos de 7 días
SELECT add_compression_policy('ticks', INTERVAL '7 days');
```

### 3. Retención
```sql
-- Mantener datos por 1 año
SELECT add_retention_policy('ticks', INTERVAL '1 year');
```

### 4. Índices Optimizados
```sql
-- Índice compuesto para consultas por dataset y tiempo
CREATE INDEX idx_ticks_dataset_t ON ticks (dataset_id, t DESC);
```

## 🔄 Migración desde SQLite

### Automática
La aplicación detecta automáticamente el tipo de base de datos y usa el cliente apropiado.

### Manual
```python
from services.database_factory import DatabaseFactory

# Obtener funciones de base de datos
db_functions = DatabaseFactory.get_database_functions()

# Usar normalmente
datasets = db_functions.get_all_datasets()
```

## 📊 Monitoreo

### Métricas de Rendimiento

```sql
-- Consultas lentas
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

-- Uso de índices
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes;
```

### Logs

```bash
# Ver logs de PostgreSQL
docker logs backtesting-postgres

# Ver logs del backend
docker logs app-python-backend-postgres
```

## 🚨 Troubleshooting

### Problemas Comunes

1. **TimescaleDB no habilitado**
   ```sql
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   ```

2. **Error de conexión**
   ```bash
   # Verificar que PostgreSQL está corriendo
   docker ps | grep postgres
   ```

3. **Permisos de base de datos**
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE backtesting TO backtesting_user;
   ```

## 🔄 Rollback a SQLite

Si necesitas volver a SQLite:

```bash
# Cambiar variable de entorno
export DATABASE_TYPE=sqlite

# Usar Docker Compose original
docker-compose up -d
```

## 📝 Próximos Pasos

- [ ] Implementar migración automática de datos
- [ ] Añadir más optimizaciones de consultas
- [ ] Implementar cache en Redis
- [ ] Añadir métricas de rendimiento
- [ ] Optimizar consultas de backtesting

## 🤝 Contribuir

1. Crear rama feature: `git checkout -b feature/postgresql-improvements`
2. Hacer cambios
3. Ejecutar tests: `python test_postgresql.py`
4. Commit y push: `git push origin feature/postgresql-improvements`
