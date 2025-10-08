-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS ollama_logs;

-- Connect to the database
\c ollama_logs

-- Create request_logs table
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    api_key VARCHAR(255),
    model VARCHAR(100),
    prompt TEXT,
    response TEXT,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    duration_seconds REAL DEFAULT 0,
    power_wh REAL DEFAULT 0,
    cost_dollars REAL DEFAULT 0,
    http_status INTEGER DEFAULT 200,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_timestamp ON request_logs(timestamp);
CREATE INDEX idx_api_key ON request_logs(api_key);
CREATE INDEX idx_model ON request_logs(model);
CREATE INDEX idx_created_at ON request_logs(created_at);

-- Create a view for daily statistics
CREATE OR REPLACE VIEW daily_stats AS
SELECT
    DATE(timestamp) as date,
    COUNT(*) as total_requests,
    SUM(total_tokens) as total_tokens,
    SUM(duration_seconds) as total_duration_seconds,
    SUM(power_wh) as total_power_wh,
    SUM(cost_dollars) as total_cost_dollars,
    AVG(duration_seconds) as avg_duration_seconds,
    AVG(total_tokens) as avg_tokens,
    AVG(cost_dollars) as avg_cost_dollars
FROM request_logs
WHERE error_message IS NULL
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Create a view for hourly statistics
CREATE OR REPLACE VIEW hourly_stats AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as total_requests,
    SUM(total_tokens) as total_tokens,
    SUM(power_wh) as total_power_wh,
    SUM(cost_dollars) as total_cost_dollars
FROM request_logs
WHERE error_message IS NULL
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

-- Create a view for model usage statistics
CREATE OR REPLACE VIEW model_stats AS
SELECT
    model,
    COUNT(*) as total_requests,
    SUM(total_tokens) as total_tokens,
    SUM(cost_dollars) as total_cost_dollars,
    AVG(duration_seconds) as avg_duration_seconds
FROM request_logs
WHERE error_message IS NULL
GROUP BY model
ORDER BY total_requests DESC;
