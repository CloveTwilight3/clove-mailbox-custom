-- Database initialization script for Email Client
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create a schema for the email client if you want to organize tables
-- CREATE SCHEMA IF NOT EXISTS email_client;

-- Set timezone
SET timezone = 'UTC';

-- Create indexes that might be useful for performance
-- Note: The actual tables will be created by SQLAlchemy migrations

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant necessary permissions to the email user
GRANT USAGE ON SCHEMA public TO emailuser;
GRANT CREATE ON SCHEMA public TO emailuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO emailuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO emailuser;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO emailuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO emailuser;
