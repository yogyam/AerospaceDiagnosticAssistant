-- Enable the pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the documents table to store text chunks and embeddings
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embeddings are 1536 dimensions
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index for vector similarity search
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create an index on metadata for filtering
CREATE INDEX IF NOT EXISTS documents_metadata_idx 
ON documents USING GIN (metadata);

-- Create a function to search for similar documents
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id int,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE sql
AS $$
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Insert some sample aerospace data for testing
INSERT INTO documents (content, metadata) VALUES 
(
    'Engine anomaly detection systems monitor various parameters including temperature, pressure, vibration, and fuel flow rates. Critical thresholds are defined for each parameter, and alerts are triggered when values exceed normal operating ranges.',
    '{"document": "Engine_Diagnostics_Manual_v2.1.pdf", "page": 45, "section": "Anomaly Detection Systems", "category": "engine"}'
),
(
    'Hydraulic system pressure should maintain between 2800-3200 PSI during normal operations. Pressure drops below 2500 PSI indicate potential pump failure or system leakage requiring immediate inspection.',
    '{"document": "Hydraulic_Systems_Handbook.pdf", "page": 78, "section": "Pressure Monitoring", "category": "hydraulics"}'
),
(
    'Flight control surface actuators are equipped with position feedback sensors. Discrepancies between commanded and actual positions greater than 2 degrees trigger fault isolation procedures.',
    '{"document": "Flight_Control_Systems.pdf", "page": 156, "section": "Actuator Diagnostics", "category": "flight_controls"}'
),
(
    'Avionics systems require continuous monitoring of power supply voltages. Voltage fluctuations beyond ±5% of nominal values can cause system instability and should trigger backup power activation.',
    '{"document": "Avionics_Power_Systems.pdf", "page": 23, "section": "Power Monitoring", "category": "avionics"}'
),
(
    'Landing gear retraction systems use hydraulic actuators with position sensors. Failure to achieve full retraction within 15 seconds indicates actuator malfunction or hydraulic pressure loss.',
    '{"document": "Landing_Gear_Manual.pdf", "page": 67, "section": "Retraction Systems", "category": "landing_gear"}'
);

-- Create a trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
