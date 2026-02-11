-- Create general news table for copper news articles
-- Run this once to set up the table

-- Create the table
CREATE TABLE IF NOT EXISTS api_app_generalnews (
    id VARCHAR(255) PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    content TEXT,
    summary TEXT,
    image_url TEXT,
    date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_generalnews_url ON api_app_generalnews(url);
CREATE INDEX IF NOT EXISTS idx_generalnews_date ON api_app_generalnews(date);
CREATE INDEX IF NOT EXISTS idx_generalnews_source ON api_app_generalnews(source);
CREATE INDEX IF NOT EXISTS idx_generalnews_created_at ON api_app_generalnews(created_at);

-- Display table info
SELECT 
    'Table created successfully!' as status,
    COUNT(*) as existing_records 
FROM api_app_generalnews;

-- Show table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'api_app_generalnews'
ORDER BY ordinal_position;
