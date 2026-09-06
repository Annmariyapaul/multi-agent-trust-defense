'''
import json
import urllib.request
import urllib.parse
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
print("API key loaded:", API_KEY is not None)

def search_news(query, sortby="relevance"):
    encoded_query = urllib.parse.quote(query)

    url = (
        f"https://gnews.io/api/v4/search"
        f"?q={encoded_query}"
        f"&lang=en"
        f"&max=10"
        f"&sortby={sortby}"
        f"&apikey={API_KEY}"
    )

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["articles"]
'''
import json
import hashlib
import pathlib
import urllib.request
import urllib.parse
import urllib.error
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
print("API key loaded:", API_KEY is not None)

CACHE_DIR = pathlib.Path("cache/news")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(query, sortby):
    key = hashlib.sha1(f"{query}|{sortby}".encode("utf-8")).hexdigest()[:12]
    return CACHE_DIR / f"{key}.json"


def search_news(query, sortby="relevance"):

    path = _cache_path(query, sortby)

    if path.exists():
        print(f"[NEWS API] Cache hit ({sortby})")
        return json.loads(path.read_text(encoding="utf-8"))

    encoded_query = urllib.parse.quote(query)

    url = (
        f"https://gnews.io/api/v4/search"
        f"?q={encoded_query}"
        f"&lang=en"
        f"&max=10"
        f"&sortby={sortby}"
        f"&apikey={API_KEY}"
    )

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[NEWS API] HTTP {e.code} for '{query}' (sortby={sortby})")
        return []
    except Exception as e:
        print(f"[NEWS API] Failed: {e}")
        return []

    articles = data.get("articles", [])

    seen = set()
    unique = []

    for a in articles:
        link = a.get("url", "")
        if link and link not in seen:
            seen.add(link)
            unique.append(a)

    path.write_text(json.dumps(unique), encoding="utf-8")

    return unique