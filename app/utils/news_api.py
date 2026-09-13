import os
import json
import hashlib
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

CACHE_DIR = Path("cache/news")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DURATION = 600  # 10 minutes


def _cache_path(query):
    key = hashlib.sha1(
        query.encode("utf-8")
    ).hexdigest()[:12]

    return CACHE_DIR / f"{key}.json"


def fetch_news(query):

    cache_file = _cache_path(query)

    # Use recent cached results if available
    if cache_file.exists():

        age = time.time() - cache_file.stat().st_mtime

        if age < CACHE_DURATION:

            print("[NEWS API] Cache hit")

            with open(cache_file, "r", encoding="utf-8") as file:
                return json.load(file)

    url = "https://gnews.io/api/v4/search"

    params = {
        "q": query,
        "lang": "en",
        "country": "us",
        "max": 10,
        "apikey": GNEWS_API_KEY
    }

    print("[NEWS API] Fetching from GNews")

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(
            f"GNews API error: {response.status_code} - {response.text}"
        )

    data = response.json()

    articles = data.get("articles", [])

    # Remove duplicate articles using their URL
    seen_urls = set()
    unique_articles = []

    for article in articles:

        url = article.get("url", "")

        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)

    # Cache only non-empty results
    if unique_articles:
        with open(cache_file, "w", encoding="utf-8") as file:
            json.dump(unique_articles, file, indent=2)

    return unique_articles