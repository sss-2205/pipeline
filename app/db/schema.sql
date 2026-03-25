-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

--------------------------------------------------
-- ARTICLES
--------------------------------------------------
CREATE TABLE IF NOT EXISTS articles (
    article_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT,
    source          VARCHAR(100),
    url             TEXT UNIQUE NOT NULL,
    language        VARCHAR(10),
    raw_text        TEXT,
    cleaned_text    TEXT
);

--------------------------------------------------
-- ARTICLE SCORES
--------------------------------------------------
CREATE TABLE IF NOT EXISTS article_scores (
    score_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id      UUID NOT NULL REFERENCES articles(article_id) ON DELETE CASCADE,
    bias_score      DOUBLE PRECISION,
    label           VARCHAR(20),
    tags            TEXT[],
    median_score      DOUBLE PRECISION,
    mode_score      DOUBLE PRECISION

);

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
