CREATE TABLE IF NOT EXISTS crypto_prices (
    id SERIAL PRIMARY KEY,
    coin_name VARCHAR(50),
    price_usd NUMERIC,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);  