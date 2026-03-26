from app.db.supabase_client import supabase


def get_dashboard_summary():
    # 1. Total articles
    total_res = supabase.table("articles").select("article_id", count="exact").execute()
    total_articles = total_res.count or 0

    # 2. Average bias score (from view not RPC)
    avg_res = supabase.table("article_with_score").select("bias_score").execute()
    scores = [row["bias_score"] for row in avg_res.data if row["bias_score"] is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    # 3. Label distribution (use view)
    label_res = supabase.table("bias_distribution").select("*").execute()
    label_data = {row["label"]: row["count"] for row in label_res.data} if label_res.data else {}

    # 4. Source comparison (use view)
    source_res = supabase.table("source_label_avg_bias").select("*").execute()
    top_sources = source_res.data if source_res.data else []

    return {
        "total_articles": total_articles,
        "avg_bias_score": round(avg_score, 2),
        "label_distribution": label_data,
        "top_sources": top_sources
    }


# source comparison - top 8 sources by article count
def get_top_sources(limit: int = 8):
    res = supabase.table("daily_requests_detailed") \
        .select("source, total_requests") \
        .execute()

    data = res.data or []

    # Aggregate total requests per source
    source_map = {}

    for row in data:
        source = row.get("source", "unknown")
        count = row.get("total_requests", 0)

        source_map[source] = source_map.get(source, 0) + count

    # Convert to list + sort
    sorted_sources = sorted(
        [{"source": k, "requests": v} for k, v in source_map.items()],
        key=lambda x: x["requests"],
        reverse=True
    )

    return sorted_sources[:limit]



def get_source_label_bias():
    res = supabase.table("source_label_avg_bias") \
        .select("*") \
        .execute()

    data = res.data or []

    # Transform into frontend-friendly format
    source_map = {}

    for row in data:
        source = row["source"]
        label = row["label"]
        score = row["avg_bias_score"]

        if source not in source_map:
            source_map[source] = {}

        source_map[source][label] = round(score, 2) if score else 0

    # Convert to list
    result = []
    for source, labels in source_map.items():
        result.append({
            "source": source,
            **labels
        })

    return result