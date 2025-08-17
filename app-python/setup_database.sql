-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create datasets table
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    row_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ticks table with TimescaleDB hypertable
CREATE TABLE IF NOT EXISTS ticks (
    id SERIAL,
    dataset_id INTEGER NOT NULL,
    t TIMESTAMP NOT NULL,
    v DOUBLE PRECISION NOT NULL,
    usd DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (id, t),
    FOREIGN KEY (dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('ticks', 't', if_not_exists => TRUE);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ticks_dataset_id ON ticks (dataset_id);
CREATE INDEX IF NOT EXISTS idx_ticks_dataset_t ON ticks (dataset_id, t DESC);

-- Create compression policy (compress data older than 7 days)
SELECT add_compression_policy('ticks', INTERVAL '7 days');

-- Create retention policy (keep data for 1 year)
SELECT add_retention_policy('ticks', INTERVAL '1 year');

-- Create function to update dataset row count
CREATE OR REPLACE FUNCTION update_dataset_row_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE datasets 
        SET row_count = row_count + 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.dataset_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE datasets 
        SET row_count = row_count - 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = OLD.dataset_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update row count
CREATE TRIGGER update_dataset_row_count_trigger
    AFTER INSERT OR DELETE ON ticks
    FOR EACH ROW
    EXECUTE FUNCTION update_dataset_row_count();

-- Create function to get dataset statistics
CREATE OR REPLACE FUNCTION get_dataset_stats(dataset_id_param INTEGER)
RETURNS TABLE (
    total_rows BIGINT,
    date_range DATERANGE,
    min_price DOUBLE PRECISION,
    max_price DOUBLE PRECISION,
    avg_price DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_rows,
        DATERANGE(MIN(t::DATE), MAX(t::DATE)) as date_range,
        MIN(usd) as min_price,
        MAX(usd) as max_price,
        AVG(usd) as avg_price
    FROM ticks 
    WHERE dataset_id = dataset_id_param;
END;
$$ LANGUAGE plpgsql;
