import os
import requests
from dotenv import load_dotenv

load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")


def fetch_news(query):
    url = "https://gnews.io/api/v4/search"

    params = {
        "q": query,
        "lang": "en",
        "country": "us",
        "max": 10,
        "apikey": GNEWS_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(
            f"GNews API error: {response.status_code} - {response.text}"
        )

    data = response.json()

    return data.get("articles", [])