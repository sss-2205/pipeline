
--------------------------------------------------
-- 1. ARTICLE + SCORE (Core Join View)
--------------------------------------------------
CREATE OR REPLACE VIEW article_with_score AS
SELECT 
    a.article_id,
    a.title,
    COALESCE(a.source, 'unknown') AS source,
    a.url,
    s.bias_score,
    COALESCE(s.label, 'unknown') AS label,
    s.median_score,
    s.mode_score
FROM articles a
LEFT JOIN article_scores s 
ON a.article_id = s.article_id;


--------------------------------------------------
-- 2. REQUEST STATS (Per Article + Date)
--------------------------------------------------
CREATE OR REPLACE VIEW request_error_stats AS
SELECT 
    article_id,
    DATE(created_at) AS date,
    COUNT(*) AS total_requests,
    AVG(response_time_ms) AS avg_response_time,
    COUNT(*) FILTER (WHERE status_code != 200) AS error_count
FROM request_history
GROUP BY article_id, DATE(created_at);


--------------------------------------------------
-- 3. GLOBAL SYSTEM STATS
--------------------------------------------------
CREATE OR REPLACE VIEW global_stats AS
SELECT 
    COUNT(*) AS total_requests,
    AVG(response_time_ms) AS avg_response_time,
    COUNT(*) FILTER (WHERE status_code != 200) AS total_errors
FROM request_history;


--------------------------------------------------
-- 4. BIAS DISTRIBUTION
--------------------------------------------------
CREATE OR REPLACE VIEW bias_distribution AS
SELECT 
    COALESCE(label, 'unknown') AS label,
    COUNT(*) AS count
FROM article_scores
GROUP BY COALESCE(label, 'unknown');


--------------------------------------------------
-- 6. SOURCE ANALYTICS (Bias per Source)
--------------------------------------------------
CREATE OR REPLACE VIEW source_bias_stats AS
SELECT 
    COALESCE(a.source, 'unknown') AS source,
    COALESCE(s.label, 'unknown') AS label,
    COUNT(*) AS count
FROM articles a
JOIN article_scores s 
ON a.article_id = s.article_id
GROUP BY 
    COALESCE(a.source, 'unknown'),
    COALESCE(s.label, 'unknown');


--------------------------------------------------
-- 7. DAILY REQUEST TREND (Overall)
--------------------------------------------------
CREATE OR REPLACE VIEW daily_requests_detailed AS
SELECT 
    DATE(r.created_at) AS date,
    COALESCE(a.source, 'unknown') AS source,
    COALESCE(s.label, 'unknown') AS label,
    COUNT(*) AS total_requests
FROM request_history r
LEFT JOIN articles a 
    ON r.article_id = a.article_id
LEFT JOIN article_scores s 
    ON r.article_id = s.article_id
GROUP BY 
    DATE(r.created_at),
    COALESCE(a.source, 'unknown'),
    COALESCE(s.label, 'unknown')
ORDER BY date;


--------------------------------------------------
-- 8. ERROR ANALYTICS
--------------------------------------------------
CREATE OR REPLACE VIEW error_stats AS
SELECT 
    status_code,
    COUNT(*) AS count
FROM request_history
WHERE status_code != 200
GROUP BY status_code;

CREATE OR REPLACE VIEW source_label_avg_bias AS
SELECT 
    COALESCE(a.source, 'unknown') AS source,
    COALESCE(s.label, 'unknown') AS label,
    AVG(s.bias_score) AS avg_bias_score
FROM articles a
JOIN article_scores s 
ON a.article_id = s.article_id
GROUP BY 
    COALESCE(a.source, 'unknown'),
    COALESCE(s.label, 'unknown');


CREATE OR REPLACE VIEW top_articles_requests AS
SELECT 
    a.article_id,
    a.title,
    a.url,
    COUNT(r.*) AS request_count
FROM articles a
JOIN request_history r 
    ON a.article_id = r.article_id
GROUP BY 
    a.article_id, a.title, a.url
ORDER BY request_count DESC
LIMIT 10;