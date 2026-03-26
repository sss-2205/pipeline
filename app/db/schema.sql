-- Permissions run these permisions once on supabase SQl editor after the schema, views and indexes are executed
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO anon, authenticated, service_role;

CREATE POLICY "Allow all access"
ON articles
FOR ALL
USING (true);
NOTIFY pgrst, 'reload schema';





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
    bias_score      DOUBLE PRECISION,
    label           VARCHAR(20),
    median_score      DOUBLE PRECISION,
    mode_score      VARCHAR(20)

);

ALTER TABLE article_scores
ADD CONSTRAINT check_label 
CHECK (label IN ('anti-BJP', 'neutral','pro-BJP', 'anti-Congress','pro-Congress'));


--------------------------------------------------
-- REQUEST HISTORY
--------------------------------------------------
CREATE TABLE IF NOT EXISTS request_history (
    request_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id      UUID REFERENCES articles(article_id) ON DELETE SET NULL,
    status_code     INT,
    response_time_ms INT,
    status_message   TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




