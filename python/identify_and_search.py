import os
import sys
import requests

API_KEY = os.environ["KARANFIL_API_KEY"]
BASE_URL = "https://api.karanfillabs.com"
HEADERS = {"X-API-Key": API_KEY}


def identify_frame(image_path: str, top_k: int = 5, min_score: float = 0.70) -> dict:
    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/v1/identify",
            headers=HEADERS,
            params={"top_k": top_k, "min_score": min_score},
            files={"file": (os.path.basename(image_path), f, "image/jpeg")},
            timeout=20,
        )
    resp.raise_for_status()
    return resp.json()


def semantic_search(query: str, top_k: int = 5) -> dict:
    resp = requests.post(
        f"{BASE_URL}/v1/search",
        headers=HEADERS,
        json={"query": query, "top_k": top_k},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        print(identify_frame(sys.argv[1]))
    else:
        prompt = " ".join(sys.argv[1:]) or "astronaut floating in deep space"
        print(semantic_search(prompt))
