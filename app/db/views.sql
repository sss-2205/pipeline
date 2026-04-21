-- =========================================================
-- VIEW: article_with_score
-- Purpose: Combine article metadata with bias scores and explainability
-- =========================================================
CREATE OR REPLACE VIEW article_with_score AS
SELECT 
    a.article_id,                         -- Unique identifier for article
    a.title,                              -- Article title
    COALESCE(a.source, 'unknown') AS source, -- Replace NULL source with 'unknown'
    a.url,                                -- Article URL

    s.bjp_axis,                           -- Bias score towards BJP
    s.congress_axis,                      -- Bias score towards Congress

    s.median_score,                       -- Median of computed scores
    s.mode_value,                         -- Most frequent score
    s.scored_list,                        -- List of scores from models
    s.explainability                      -- Model explainability output

FROM articles a
LEFT JOIN article_scores s 
ON a.article_id = s.article_id;           -- Keep all articles even if scores are missing



-- =========================================================
-- VIEW: source_bias_stats
-- Purpose: Aggregate average bias per news source
-- =========================================================
CREATE OR REPLACE VIEW source_bias_stats AS
SELECT 
    COALESCE(a.source, 'unknown') AS source, -- Normalize NULL sources

    AVG(s.bjp_axis) AS avg_bjp_bias,         -- Average BJP bias
    AVG(s.congress_axis) AS avg_congress_bias, -- Average Congress bias

    COUNT(*) AS article_count                -- Total articles per source

FROM articles a
JOIN article_scores s 
ON a.article_id = s.article_id              -- Only include scored articles

GROUP BY COALESCE(a.source, 'unknown');     -- Group by normalized source



-- =========================================================
-- VIEW: daily_requests_detailed
-- Purpose: Track daily requests and bias trends per source
-- =========================================================
CREATE OR REPLACE VIEW daily_requests_detailed AS
SELECT 
    DATE(r.created_at) AS date,             -- Extract date from timestamp
    COALESCE(a.source, 'unknown') AS source,-- Normalize NULL sources

    AVG(s.bjp_axis) AS avg_bjp_bias,        -- Daily average BJP bias
    AVG(s.congress_axis) AS avg_congress_bias, -- Daily average Congress bias

    COUNT(*) AS total_requests              -- Total requests per day per source

FROM request_history r
LEFT JOIN articles a 
    ON r.article_id = a.article_id          -- Map request to article
LEFT JOIN article_scores s 
    ON r.article_id = s.article_id          -- Map request to score

WHERE COALESCE(a.source, 'unknown') != 'unknown' -- Exclude unknown sources

GROUP BY 
    DATE(r.created_at),
    COALESCE(a.source, 'unknown')

ORDER BY date;                              -- Sort chronologically



-- =========================================================
-- VIEW: global_stats
-- Purpose: Provide overall system performance metrics
-- =========================================================
CREATE OR REPLACE VIEW global_stats AS
SELECT 
    COUNT(*) AS total_requests,             -- Total number of API requests
    AVG(response_time_ms) AS avg_response_time, -- Average response time in ms
    COUNT(*) FILTER (WHERE status_code != 200) AS total_errors -- Non-success responses
FROM request_history;



-- =========================================================
-- VIEW: error_stats
-- Purpose: Analyze error distribution by status code
-- =========================================================
CREATE OR REPLACE VIEW error_stats AS
SELECT 
    status_code,                            -- HTTP status code
    COUNT(*) AS count                       -- Number of occurrences
FROM request_history
WHERE status_code != 200                    -- Only errors
GROUP BY status_code;



-- =========================================================
-- VIEW: top_articles_requests
-- Purpose: Identify most requested articles (Top 10)
-- =========================================================
CREATE OR REPLACE VIEW top_articles_requests AS
SELECT 
    a.article_id,                           -- Article ID
    a.title,                                -- Article title
    a.url,                                  -- Article URL
    COUNT(r.*) AS request_count             -- Number of times requested
FROM articles a
JOIN request_history r 
    ON a.article_id = r.article_id          -- Link requests to articles
GROUP BY 
    a.article_id, a.title, a.url
ORDER BY request_count DESC                 -- Highest requests first
LIMIT 10;                                   -- Top 10 articles