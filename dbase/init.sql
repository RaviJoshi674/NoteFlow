-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

--------------------------------------------------
-- Lectures Table
--------------------------------------------------
CREATE TABLE IF NOT EXISTS lectures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    duration_seconds FLOAT,
    mime_type VARCHAR(50),
    file_size_bytes BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- Processing Jobs Table
--------------------------------------------------
CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lecture_id UUID REFERENCES lectures(id) ON DELETE CASCADE,

    -- Job lifecycle state
    status VARCHAR(50) NOT NULL DEFAULT 'QUEUED', 
    -- QUEUED, PROCESSING, COMPLETED, FAILED

    -- Fine-grained execution stage
    current_stage VARCHAR(50) NOT NULL DEFAULT 'UPLOADED', 
    -- UPLOADED, VALIDATING, TRANSCRIBING, GENERATING, COMPLETED

    -- Retry & fault tolerance
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,

    -- Error tracking
    error_message TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- Auto-update updated_at on processing_jobs
--------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_processing_jobs_updated_at
BEFORE UPDATE ON processing_jobs
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

--------------------------------------------------
-- Transcripts Table
--------------------------------------------------
CREATE TABLE IF NOT EXISTS transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lecture_id UUID REFERENCES lectures(id) ON DELETE CASCADE,
    text_content TEXT,
    segments_json JSONB, -- timestamped transcript segments
    language VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- Generated Content Table
--------------------------------------------------
CREATE TABLE IF NOT EXISTS generated_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lecture_id UUID REFERENCES lectures(id) ON DELETE CASCADE,

    content_type VARCHAR(50) NOT NULL,
    -- SUMMARY, NOTES, QUIZ

    content_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
