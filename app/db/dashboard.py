from app.db.supabase_client import supabase

def get_dashboard_summary():
    # 1. Total articles
    total_res = supabase.table("articles").select("article_id", count="exact").execute()
    total_articles = total_res.count or 0

    # 2. Average bias (combine BJP + Congress)
    avg_res = supabase.table("article_with_score") \
        .select("bjp_axis, congress_axis") \
        .execute()

    data = avg_res.data or []

    scores = []
    for row in data:
        if row["bjp_axis"] is not None and row["congress_axis"] is not None:
            # simple combined bias metric
            scores.append((row["bjp_axis"] + row["congress_axis"]) / 2)

    avg_score = sum(scores) / len(scores) if scores else 0

    # 3. Label distribution (use mode_value)
    label_map = {}
    for row in data:
        label = row.get("mode_value")
        if label:
            label_map[label] = label_map.get(label, 0) + 1

    # 4. Source stats (use new view)
    source_res = supabase.table("source_bias_stats").select("*").execute()
    top_sources = source_res.data or []

    return {
        "total_articles": total_articles,
        "avg_bias_score": round(avg_score, 2),
        "label_distribution": label_map,
        "top_sources": top_sources
    }


def get_top_sources(limit: int = 8):
    res = supabase.table("daily_requests_detailed") \
        .select("source, total_requests") \
        .execute()

    data = res.data or []

    source_map = {}

    for row in data:
        source = row.get("source", "unknown")
        count = row.get("total_requests", 0)

        source_map[source] = source_map.get(source, 0) + count

    sorted_sources = sorted(
        [{"source": k, "requests": v} for k, v in source_map.items()],
        key=lambda x: x["requests"],
        reverse=True
    )

    return sorted_sources[:limit]



def get_source_label_bias():
    res = supabase.table("source_bias_stats") \
        .select("*") \
        .execute()

    data = res.data or []

    result = []

    for row in data:
        result.append({
            "source": row["source"],
            "avg_bjp_bias": round(row["avg_bjp_bias"], 2) if row["avg_bjp_bias"] else 0,
            "avg_congress_bias": round(row["avg_congress_bias"], 2) if row["avg_congress_bias"] else 0,
            "article_count": row["article_count"]
        })

    return result