-- Crear tabla datasets
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    row_count INTEGER DEFAULT 0
);

-- Crear tabla ticks con referencia a dataset
CREATE TABLE IF NOT EXISTS ticks_new (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    t TIMESTAMP WITH TIME ZONE NOT NULL,
    v DOUBLE PRECISION NOT NULL,
    usd DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_ticks_dataset_id ON ticks_new(dataset_id);
CREATE INDEX IF NOT EXISTS idx_ticks_t ON ticks_new(t);
CREATE INDEX IF NOT EXISTS idx_datasets_name ON datasets(name);

-- Migrar datos existentes (opcional)
-- INSERT INTO datasets (name, description, row_count) 
-- SELECT 'Dataset Original', 'Dataset migrado desde la tabla original', COUNT(*) 
-- FROM ticks;

-- INSERT INTO ticks_new (dataset_id, t, v, usd)
-- SELECT 1, t, v, usd FROM ticks;
