from app.utils.news_api import fetch_news


def retrieval_agent(state):

    query = state["user_query"]

    print("\n[RETRIEVAL] Fetching news...")

    articles = fetch_news(query)

    if not articles:
        print("[RETRIEVAL] No articles found.")

        state["retrieved_information"] = {
            "relevance": [],
            "recency": []
        }

        return state

    # Researcher A receives the retrieved articles
    relevance_articles = articles.copy()

    # Researcher B receives the same articles,
    # but ordered from newest to oldest
    recency_articles = sorted(
        articles,
        key=lambda article: article.get("publishedAt", ""),
        reverse=True
    )

    state["retrieved_information"] = {
        "relevance": relevance_articles,
        "recency": recency_articles
    }

    print(
        f"[RETRIEVAL] Retrieved {len(articles)} unique articles."
    )

    return state