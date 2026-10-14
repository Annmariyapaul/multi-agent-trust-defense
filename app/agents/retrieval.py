from app.utils.news_api import fetch_news


def retrieval_agent(state):

    query = state["user_query"]

    print("\n[RETRIEVAL] Fetching news...")

    try:
        articles = fetch_news(query)
    except Exception as e:
        # GNews down, daily quota used up, or no network. Carry on with no
        # articles: the researchers mark themselves unavailable and the
        # report says no verified answer could be produced.
        print(f"[RETRIEVAL] News fetch failed: {e}")
        articles = []

    if not articles:
        print("[RETRIEVAL] No articles found.")
        return {"retrieved_information": {"relevance": [], "recency": []}}

    # Researcher A receives the retrieved articles
    relevance_articles = articles.copy()

    # Researcher B receives the same articles,
    # but ordered from newest to oldest
    recency_articles = sorted(
        articles,
        key=lambda article: article.get("publishedAt", ""),
        reverse=True
    )

    print(f"[RETRIEVAL] Retrieved {len(articles)} unique articles.")

    # Return only the key this node changes, instead of the whole state.
    return {
        "retrieved_information": {
            "relevance": relevance_articles,
            "recency": recency_articles,
        }
    }