CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_url ON articles(url);


CREATE INDEX idx_scores_article_id ON article_scores(article_id); -- FK index (MUST)
CREATE INDEX idx_requests_article_id ON request_history(article_id); -- FK index (MUST)
CREATE INDEX idx_requests_created_at ON request_history(created_at);
