import os
import requests
from app.db.supabase_client import supabase


def build_url(env_key: str, path: str) -> str:
    base = os.environ.get(env_key)
    if not base:
        raise RuntimeError(f"Missing environment variable: {env_key}")
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


import time
import requests

def post_json(url: str, payload: dict, article_id=None):
    start = time.time()

    try:
        resp = requests.post(
            url,
            json=payload,
            timeout=(10, 280)
        )

        resp.raise_for_status()
        duration = int((time.time() - start) * 1000)

        # ✅ success log
        supabase.table("request_history").insert({
            "article_id": article_id,
            "status_code": resp.status_code,
            "response_time_ms": duration,
            "status_message": "success"
        }).execute()

        return resp.json()

    # 🔴 TIMEOUT
    except requests.exceptions.ReadTimeout:
        error_msg = f"Timeout while calling {url}"

    # 🔴 CONNECTION ERROR
    except requests.exceptions.ConnectionError:
        error_msg = f"Connection error while calling {url}"

    # 🔴 HTTP ERROR (4xx, 5xx)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "unknown"
        response_text = e.response.text if e.response else "no body"
        error_msg = f"HTTP {status_code}: {response_text}"

    # 🔴 ANY OTHER ERROR
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"

    # 🔴 LOG FAILURE
    duration = int((time.time() - start) * 1000)

    try:
        supabase.table("request_history").insert({
            "article_id": article_id,
            "status_code": 500,
            "response_time_ms": duration,
            "status_message": error_msg
        }).execute()
    except Exception:
        pass  # avoid breaking pipeline due to logging failure

    raise Exception(error_msg)