-- Permissions run these permisions once on supabase SQl editor after the schema, views and indexes are executed
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

GRANT SELECT, INSERT, UPDATE, DELETE 
ON ALL TABLES IN SCHEMA public 
TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE 
ON TABLES TO anon, authenticated, service_role;





-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
SET TIME ZONE 'Asia/Kolkata';

--------------------------------------------------
-- ARTICLES
--------------------------------------------------
CREATE TABLE IF NOT EXISTS articles (
    article_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT,
    source          VARCHAR(100),
    url             TEXT UNIQUE NOT NULL,
    raw_text        TEXT,
    cleaned_text    TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- ARTICLE SCORES
--------------------------------------------------
CREATE TABLE IF NOT EXISTS article_scores (
    score_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id      UUID NOT NULL REFERENCES articles(article_id) ON DELETE CASCADE,

    bjp_axis        DOUBLE PRECISION,
    congress_axis   DOUBLE PRECISION,

    median_score    DOUBLE PRECISION,
    mode_value      varchar(75),

    scored_list     JSONB,
    explainability  JSONB
    );



--------------------------------------------------
-- REQUEST HISTORY
--------------------------------------------------
CREATE TABLE IF NOT EXISTS request_history (
    request_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id       UUID REFERENCES articles(article_id) ON DELETE SET NULL,
    status_code      INT,
    response_time_ms INT,
    status_message   TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




-- Alter permissions for the tables
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE article_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all articles"
ON articles FOR ALL USING (true);

CREATE POLICY "Allow all scores"
ON article_scores FOR ALL USING (true);

CREATE POLICY "Allow all requests"
ON request_history FOR ALL USING (true);
