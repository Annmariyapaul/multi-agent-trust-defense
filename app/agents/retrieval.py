from app.utils.news_api import fetch_news


def retrieval_agent(state):

    query = state["user_query"]

    print("\n[RETRIEVAL] Fetching news...")

    articles = fetch_news(query)

    if not articles:
        print("[RETRIEVAL] No articles found.")
        state["retrieved_information"] = []
        return state

    state["retrieved_information"] = articles

    print(f"[RETRIEVAL] Retrieved {len(articles)} articles.")

    return state