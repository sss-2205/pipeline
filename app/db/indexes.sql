CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);

CREATE INDEX IF NOT EXISTS idx_scores_article_id ON article_scores(article_id);
CREATE INDEX IF NOT EXISTS idx_requests_article_id ON request_history(article_id);
CREATE INDEX IF NOT EXISTS idx_requests_created_at ON request_history(created_at);