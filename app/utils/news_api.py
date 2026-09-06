import json
import urllib.request
from dotenv import load_dotenv
import os
load_dotenv()

# TODO: replace API_KEY with your API key.
apikey = os.getenv('NEWS_API_KEY')
category = "general"
url = f"https://gnews.io/api/v4/top-headlines?category={category}&lang=en&country=us&max=10&apikey={apikey}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode("utf-8"))
    articles = data["articles"]
    # print(articles)

    for i in range(len(articles)):
        print(f"Title: {articles[i]['title']}")
        print(f"Description: {articles[i]['description']}\n")
        # You can replace {property} below with any of the article properties returned by the API.
        # articles[i].{property}
        # print(f"{articles[i]['{property}']}")

       