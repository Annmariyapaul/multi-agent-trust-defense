import os
import json
import hashlib
import time
from pathlib import Path
import re

import requests
from dotenv import load_dotenv

load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

CACHE_DIR = Path("cache/news")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DURATION = 600  # 10 minutes

STOP_WORDS = {
    "a", "an", "and", "are", "about", "be", "by", "can", "for",
    "from", "how", "in", "into", "is", "latest", "news", "of",
    "on", "the", "to", "what", "were", "with",
}

def build_query_candidates(query):
    normalized = normalize_news_query(query)
    words = normalized.lower().split()

    meaningful_words = [
        word for word in words
        if word not in STOP_WORDS
    ]

    candidates = [normalized]

    if meaningful_words:
        candidates.append(" ".join(meaningful_words))

    # Preserve useful two-word concepts such as "artificial intelligence".
    if "artificial intelligence" in normalized.lower():
        candidates.append("artificial intelligence")

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(candidates))

def normalize_news_query(query):
    """Convert natural-language input into a safe GNews search query."""
    normalized = re.sub(r"[^\w\s]", " ", query)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    if not normalized:
        raise ValueError("The news query contains no searchable text.")

    return normalized

def _cache_path(query):
    key = hashlib.sha1(
        query.encode("utf-8")
    ).hexdigest()[:12]

    return CACHE_DIR / f"{key}.json"


def fetch_news(query):
    search_query = normalize_news_query(query)
    cache_file = _cache_path(search_query)

    # Use recent cached results if available
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime

        if age < CACHE_DURATION:
            print("[NEWS API] Cache hit")

            with open(cache_file, "r", encoding="utf-8") as file:
                return json.load(file)

    url = "https://gnews.io/api/v4/search"

    params = {
        "q": search_query,
        "lang": "en",
        "country": "us",
        "max": 10,
        "apikey": GNEWS_API_KEY,
    }

    print(f"[NEWS API] Fetching from GNews: {search_query}")

    response = requests.get(url, params=params, timeout=15)

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
        article_url = article.get("url", "")

        if article_url and article_url not in seen_urls:
            seen_urls.add(article_url)
            unique_articles.append(article)

    if unique_articles:
        with open(cache_file, "w", encoding="utf-8") as file:
            json.dump(unique_articles, file, indent=2)

    return unique_articles