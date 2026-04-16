from starlette.concurrency import run_in_threadpool
from app.db.supabase_client import supabase

from app.schemas.schema import (
    ScrapeRequest,
    article,
    coref_request,
    Coref_Article,
    Inference_Response,
    ExplainRequest,ExplainResponse,
    FinalResult
)
from app.services.job_store import update_job
from app.utils.http_client import build_url, post_json
import time
import json
SCRAPE_API = build_url("SCRAPE_API", "api/v1/scrape")
PREPROCESS_API = build_url("PREPROCESS_API", "api/v1/preprocess")
COREF_API = build_url("COREF_API", "api/v1/coref")
BIAS_API = build_url("BIAS_API", "api/v1/bias/inference")
EXPLAIN_API = build_url("EXPLAIN_API", "api/explain")

async def run_pipeline_job(job_id: str, data: ScrapeRequest, article_id: str = None) -> None:
    try:
        start_time = time.time()

        # ------------------ SCRAPING ------------------
        try:
            update_job(job_id, status="running", step="scraping")

            scraped_json = await run_in_threadpool(
                post_json,
                SCRAPE_API,
                {"url": str(data.url)},
                article_id
            )

            print("SCRAPE RESPONSE:", scraped_json)

            scraped_article = article(**scraped_json)

        except Exception as e:
            raise Exception(f"[SCRAPING FAILED] {str(e)}")

        # ------------------ DB INSERT/UPDATE ------------------
        try:
            print("ARTICLE ID BEFORE DB:", article_id)

            if article_id:
                supabase.table("articles").update({
                    "title": scraped_article.title,
                    "source": scraped_article.source,
                    "url": str(scraped_article.url),
                    "raw_text": scraped_article.content
                }).eq("article_id", article_id).execute()
            else:
                response = supabase.table("articles").insert({
                    "title": scraped_article.title,
                    "source": scraped_article.source,
                    "url": str(scraped_article.url),
                    "raw_text": scraped_article.content
                }).execute()

                print("INSERT RESPONSE:", response.data)

                article_id = response.data[0]["article_id"]

        except Exception as e:
            raise Exception(f"[DB INSERT/UPDATE FAILED] {str(e)}")

        # ------------------ PREPROCESS ------------------
        try:
            update_job(job_id, status="running", step="preprocessing")

            preprocessed_json = await run_in_threadpool(
                post_json,
                PREPROCESS_API,
                scraped_article.model_dump(),
                article_id
            )

            print("PREPROCESS RESPONSE:", preprocessed_json)

            preprocessed = article(**preprocessed_json)

            supabase.table("articles").update({
                "cleaned_text": preprocessed.content
            }).eq("article_id", article_id).execute()

        except Exception as e:
            raise Exception(f"[PREPROCESS FAILED] {str(e)}")

        # ------------------ COREF ------------------
        try:
            update_job(job_id, status="running", step="coreference")

            coref_payload = coref_request(
                content=preprocessed.content,
                url=str(preprocessed.url)
            )

            coref_json = await run_in_threadpool(
                post_json,
                COREF_API,
                coref_payload.model_dump(),
            )

            print("COREF RESPONSE:", coref_json)

            coref_result = Coref_Article(**coref_json)

        except Exception as e:
            raise Exception(f"[COREF FAILED] {str(e)}")

        # ------------------ BIAS ------------------
        try:
            update_job(job_id, status="running", step="bias_inference")

            bias_payload = {
                "ner_list": [i.model_dump() for i in (coref_result.ner_list or [])]
            }

            bias_json = await run_in_threadpool(
                post_json,
                BIAS_API,
                bias_payload,
            )

            print("BIAS RESPONSE:", bias_json)

            bias_score_result = Inference_Response(**bias_json)
            

        except Exception as e:
            raise Exception(f"[BIAS FAILED] {str(e)}")

        # ------------------ SCORE INSERT ------------------
        try:
            score_insert = {
                "article_id": article_id,
                "bjp_axis": bias_score_result.bjp_axis,
                "congress_axis": bias_score_result.congress_axis,
                "scored_list": [i.model_dump() for i in bias_score_result.scored_list],
                "median_score": bias_score_result.median_score,
                "mode_value": bias_score_result.mode_value
            }

            print("SCORE INSERT:", score_insert)

            supabase.table("article_scores").insert(score_insert).execute()

        except Exception as e:
            raise Exception(f"[SCORE INSERT FAILED] {str(e)}")

        
        # ------------------ EXPLAINABILITY ------------------
    
        try:
            update_job(job_id, status="running", step="explainability")

            explain_payload = ExplainRequest(
    bjp_axis=bias_score_result.bjp_axis,
    congress_axis=bias_score_result.congress_axis,
    scored_list=bias_score_result.scored_list   # ✅ FIX
)
            # print("FINAL PAYLOAD:", json.dumps(explain_payload.model_dump(), indent=2))

            explain_json = await run_in_threadpool(
                post_json,
                EXPLAIN_API,
                explain_payload.model_dump(),
            )

            print("EXPLAIN RESPONSE:", explain_json)


            explain_result = ExplainResponse(**explain_json)

            

        except Exception as e:
            raise Exception(f"[explainer FAILED] {str(e)}")

        # ------------------ SCORE INSERT ------------------
    #     bias_explanation: str
    # overall_interpretation: str
    # axis_analysis: Dict[str, str]
    # evidence: List[str]
    # confidence_note: str
    # alternative_sources:
        try:
             supabase.table("article_scores").update({"explainability": explain_result.model_dump()}).eq("article_id", article_id).execute()

        except Exception as e:
            raise Exception(f"[SCORE EXPLANATION INSERT FAILED] {str(e)}")

        # ------------------ DONE ------------------
        result_data = {
    "bias": bias_score_result.model_dump(),
    "explainability": explain_result.model_dump()
}
        update_job(
            job_id,
            status="completed",
            step="done",
            result=FinalResult(**result_data),
            error=None,
        )

    except Exception as e:
        print("❌ FINAL ERROR:", str(e))

        update_job(
            job_id,
            status="failed",
            step=str(e).split("]")[0].replace("[", ""),  # extract step name
            error=str(e),
        )