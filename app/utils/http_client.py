import os
import requests


def build_url(env_key: str, path: str) -> str:
    base = os.environ.get(env_key)
    if not base:
        raise RuntimeError(f"Missing environment variable: {env_key}")
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def post_json(url: str, payload: dict):
    try:
        resp = requests.post(
            url,
            json=payload,
            timeout=(10, 280)
        )
        resp.raise_for_status()
        return resp.json()

    except requests.exceptions.ReadTimeout:
        raise Exception(f"Timeout while calling {url}")

    except requests.exceptions.ConnectionError:
        raise Exception(f"Connection error while calling {url}")

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else "unknown"
        response_text = e.response.text if e.response is not None else "no response body"
        raise Exception(
            f"HTTP error while calling {url}. "
            f"Status: {status_code}. Response: {response_text}"
        )

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed for {url}: {str(e)}")